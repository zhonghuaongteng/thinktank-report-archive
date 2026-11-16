"""Isolated Git integration tests; no production repository or mail is used."""
import json
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

_default_helper = Path(__file__).with_name("prepare_weekly_worktree.py")
if not _default_helper.is_file():
    _default_helper = Path(__file__).resolve().parents[1] / "scripts/prepare_weekly_worktree.py"
_helper_path = Path(os.environ.get("AUTOMATION4_BOOTSTRAP_MODULE", _default_helper))
_spec = importlib.util.spec_from_file_location("automation4_bootstrap_under_test", _helper_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
PreparationError, TARGET_BRANCH, prepare = _module.PreparationError, _module.TARGET_BRANCH, _module.prepare


def git(repo, *args, input=None):
    return subprocess.run(["git", "-c", "gc.auto=0", "-c", "maintenance.auto=false", "-C", str(repo), *args],
                          input=input.encode("utf-8") if input is not None else None,
                          capture_output=True, check=True).stdout.decode("utf-8").strip()


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="automation4-bootstrap-test-")
        self.root = Path(self.temp.name).resolve()
        self.entry = self.root / "entry"
        self.remote = self.root / "remote.git"
        self.worktrees = self.root / "worktrees"
        self.state = self.root / "runs"
        self.entry.mkdir()
        self.remote.mkdir()
        git(self.remote, "init", "--bare")
        git(self.entry, "init", "-b", "main")
        git(self.entry, "config", "user.name", "Isolated test")
        git(self.entry, "config", "user.email", "test@example.invalid")
        (self.entry / "base.txt").write_text("base\n", encoding="utf-8")
        git(self.entry, "add", "base.txt")
        git(self.entry, "commit", "-m", "base")
        self.base = git(self.entry, "rev-parse", "HEAD")
        git(self.entry, "remote", "add", "origin", str(self.remote))
        git(self.entry, "push", "origin", f"HEAD:refs/heads/{TARGET_BRANCH}")
        self.args = dict(entry=self.entry, date="2026-11-22", worktree_root=self.worktrees,
                         state_dir=self.state, expected_remote=str(self.remote), minimum_commit=self.base)

    def tearDown(self):
        # Every path removed here was created beneath this verified temporary root.
        self.assertTrue(self.root.name.startswith("automation4-bootstrap-test-"))
        self.temp.cleanup()

    def test_one_vs_245_divergence_recovers_and_preserves_entry(self):
        pieces = []
        previous = self.base
        for i in range(245):
            mark = i + 1
            pieces.append(f"commit refs/heads/{TARGET_BRANCH}\nmark :{mark}\nauthor Test <test@example.invalid> 1790000000 +0000\ncommitter Test <test@example.invalid> 1790000000 +0000\ndata 6\nremote\nfrom {previous}\n\n")
            previous = f":{mark}"
        git(self.entry, "fast-import", "--quiet", input="".join(pieces))
        git(self.entry, "push", "origin", f"refs/heads/{TARGET_BRANCH}")
        git(self.entry, "commit", "--allow-empty", "-m", "local old archive")
        original = git(self.entry, "rev-parse", "HEAD")
        result = prepare(**self.args)
        self.assertEqual(result["action"], "new_from_verified_remote")
        self.assertEqual((result["entry_local_only_commits"], result["remote_only_commits"]), (1, 245))
        self.assertEqual(git(self.entry, "rev-parse", "HEAD"), original)
        self.assertEqual(git(Path(result["worktree"]), "rev-parse", "HEAD"), result["base_commit"])
        self.assertEqual(git(Path(result["worktree"]), "status", "--porcelain"), "")

    def test_dirty_entry_bytes_and_status_preserved(self):
        (self.entry / "base.txt").write_bytes(b"uncommitted change\n")
        (self.entry / "notes.txt").write_bytes(b"untracked note\n")
        before = git(self.entry, "status", "--porcelain")
        result = prepare(**self.args)
        self.assertTrue(result["entry_dirty"])
        self.assertEqual((self.entry / "base.txt").read_bytes(), b"uncommitted change\n")
        self.assertEqual((self.entry / "notes.txt").read_bytes(), b"untracked note\n")
        self.assertEqual(git(self.entry, "status", "--porcelain"), before)

    def test_second_call_resumes_without_new_worktree(self):
        first = prepare(**self.args)
        (Path(first["worktree"]) / "in_progress.txt").write_text("keep me", encoding="utf-8")
        second = prepare(**self.args)
        self.assertEqual(second["action"], "resume_existing")
        self.assertEqual(second["worktree"], first["worktree"])
        self.assertEqual(len(list(self.worktrees.iterdir())), 1)
        self.assertTrue(second["collection_must_not_restart"])

    def test_sent_receipt_requires_mail_verification_not_repeat(self):
        first = prepare(**self.args)
        path = Path(first["worktree"]) / "docs/run_receipts/2026-11-22.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"business_date": "2026-11-22", "delivery": {"status": "sent_verified"}}), encoding="utf-8")
        second = prepare(**self.args)
        self.assertEqual(second["action"], "verify_already_sent")
        self.assertEqual(second["worktree"], first["worktree"])
        self.assertTrue(second["mail_must_be_checked_before_send"])

    def test_wrong_remote_cannot_pass(self):
        with self.assertRaisesRegex(PreparationError, "unexpected_remote"):
            prepare(**{**self.args, "expected_remote": "https://example.invalid/other.git"})
        self.assertFalse(self.state.exists())

    def test_unknown_minimum_cannot_pass(self):
        with self.assertRaisesRegex(PreparationError, "remote_minimum_version_failed"):
            prepare(**{**self.args, "minimum_commit": "a" * 40})
        self.assertEqual(list(self.worktrees.iterdir()), [])

    def test_fetch_failure_cannot_pass(self):
        missing = self.root / "missing.git"
        git(self.entry, "remote", "set-url", "origin", str(missing))
        with self.assertRaisesRegex(PreparationError, "git_operation_failed"):
            prepare(**{**self.args, "expected_remote": str(missing)})
        self.assertFalse((self.state / "2026-11-22_workspace.json").exists())

    def test_rewritten_remote_tracking_cache_refreshes_only_cache(self):
        git(self.entry, "commit", "--allow-empty", "-m", "first remote line")
        old = git(self.entry, "rev-parse", "HEAD")
        git(self.entry, "push", "origin", f"HEAD:refs/heads/{TARGET_BRANCH}")
        tree = git(self.entry, "rev-parse", f"{self.base}^{{tree}}")
        rewritten = git(self.entry, "commit-tree", tree, "-p", self.base, input="replacement remote line\n")
        git(self.entry, "push", "origin", f"{rewritten}:refs/heads/fixture-transfer")
        # Simulate a remote maintenance rewrite entirely inside this fixture.
        git(self.remote, "update-ref", f"refs/heads/{TARGET_BRANCH}", rewritten)
        result = prepare(**self.args)
        self.assertEqual(result["base_commit"], rewritten)
        self.assertEqual(git(self.entry, "rev-parse", "HEAD"), old)
        self.assertEqual(git(self.entry, "rev-parse", f"refs/remotes/origin/{TARGET_BRANCH}"), rewritten)

    def test_existing_resume_still_checks_minimum(self):
        prepare(**self.args)
        with self.assertRaisesRegex(PreparationError, "existing_run_minimum_version_failed"):
            prepare(**{**self.args, "minimum_commit": "b" * 40})

    def test_unregistered_matching_worktree_is_adopted(self):
        self.worktrees.mkdir()
        existing = self.worktrees / "older-run"
        git(self.entry, "worktree", "add", "-b", "codex/automation-4-2026-11-22-old", str(existing), self.base)
        receipt = existing / "docs/run_receipts/2026-11-22_progress.json"
        receipt.parent.mkdir(parents=True)
        receipt.write_text(json.dumps({"business_date": "2026-11-22", "audit": {"status": "running"}}), encoding="utf-8")
        result = prepare(**self.args)
        self.assertEqual(result["action"], "resume_existing")
        self.assertEqual(result["worktree"], str(existing))

    def test_multiple_unfinished_worktrees_block_without_guessing(self):
        self.worktrees.mkdir()
        for n in (1, 2):
            git(self.entry, "worktree", "add", "-b", f"codex/automation-4-2026-11-22-{n}", str(self.worktrees / str(n)), self.base)
            receipt = self.worktrees / str(n) / "docs/run_receipts/2026-11-22_progress.json"
            receipt.parent.mkdir(parents=True)
            receipt.write_text(json.dumps({"business_date": "2026-11-22", "collection": {"status": "complete"}}), encoding="utf-8")
        with self.assertRaisesRegex(PreparationError, "multiple_existing_runs_need_resolution"):
            prepare(**self.args)

    def test_content_arrays_do_not_break_registered_resume(self):
        first = prepare(**self.args)
        directory = Path(first["worktree"]) / "docs/run_receipts"
        directory.mkdir(parents=True)
        (directory / "2026-11-22_comic_review.json").write_text('[{"visual_review":"passed"}]', encoding="utf-8")
        (directory / "2026-11-22_ordered_features.json").write_text('[{"index":1}]', encoding="utf-8")
        self.assertEqual(prepare(**self.args)["action"], "resume_existing")

    def test_unregistered_preflight_only_tree_is_preserved_not_adopted(self):
        self.worktrees.mkdir()
        old = self.worktrees / "old-preflight"
        git(self.entry, "worktree", "add", "-b", "codex/automation-4-2026-11-22-old", str(old), self.base)
        receipt = old / "docs/run_receipts/2026-11-22_preflight.json"
        receipt.parent.mkdir(parents=True)
        receipt.write_text(json.dumps({"business_date": "2026-11-22", "version_gate": "passed", "content": "not_started"}), encoding="utf-8")
        git(self.entry, "commit", "--allow-empty", "-m", "new remote baseline")
        newer = git(self.entry, "rev-parse", "HEAD")
        git(self.entry, "push", "origin", f"HEAD:refs/heads/{TARGET_BRANCH}")
        result = prepare(**self.args)
        self.assertEqual(result["action"], "new_from_verified_remote")
        self.assertNotEqual(result["worktree"], str(old))
        self.assertEqual(result["base_commit"], newer)
        self.assertEqual(git(old, "rev-parse", "HEAD"), self.base)
        self.assertTrue(receipt.is_file())


if __name__ == "__main__":
    unittest.main()
