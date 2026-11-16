"""Prepare or resume one weekly run without changing its entry worktree.

Only Git metadata, a newly created isolated worktree, and the external run
registry are written. This helper never collects, renders, publishes, or mails.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

TARGET_BRANCH = "codex/backfill-govai-interface-oecd"
EXPECTED_REMOTE = "https://github.com/zhonghuaongteng/thinktank-report-archive.git"
MINIMUM_COMMIT = "cc1de1d48e10480f7eb311f7a2b7d3cac6ccd817"
PROTECTED_MAIN = Path.home() / "OneDrive/知识库/智库信息爬虫"


class PreparationError(RuntimeError):
    def __init__(self, code: str, operation: str = ""):
        self.code, self.operation = code, operation
        super().__init__(code)


def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def within(path: Path, root: Path):
    return path.resolve().is_relative_to(root.resolve())


def git(repo: Path, *args: str, timeout: int = 90, check: bool = True):
    # Never print captured stderr: a configured remote or helper may include
    # authentication data. The caller receives an operation name and exit code.
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "never"
    try:
        result = subprocess.run(
            ["git", "-c", "gc.auto=0", "-c", "maintenance.auto=false", "-C", str(repo), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=env, timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise PreparationError("git_timeout", args[0]) from exc
    except OSError as exc:
        raise PreparationError("git_unavailable", args[0]) from exc
    if check and result.returncode:
        raise PreparationError("git_operation_failed", f"{args[0]}:exit_{result.returncode}")
    return result


def common_dir(repo: Path):
    return Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()).resolve()


def minimum_verified(repo: Path, minimum: str):
    if not re.fullmatch(r"[0-9a-fA-F]{40,64}", minimum):
        raise PreparationError("invalid_minimum_commit")
    return git(repo, "merge-base", "--is-ancestor", minimum, "HEAD", check=False).returncode == 0


def read_json(path: Path):
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise PreparationError("invalid_run_record", path.name) from exc
    if not isinstance(value, dict):
        raise PreparationError("invalid_run_record", path.name)
    return value


def checkpoint(repo: Path, date: str):
    result = {"sent_verified": False, "work_started": False, "receipts": []}
    for path in sorted((repo / "docs/run_receipts").glob(f"{date}*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            raise PreparationError("invalid_run_record", path.name) from exc
        # Content inventories (for example comic_review and ordered_features)
        # are valid JSON arrays but are not run-state checkpoints.
        if isinstance(value, list):
            continue
        if not isinstance(value, dict):
            raise PreparationError("invalid_run_record", path.name)
        recorded_date = value.get("business_date", value.get("date", value.get("issue_date")))
        if recorded_date not in (None, date):
            raise PreparationError("checkpoint_date_mismatch", path.name)
        result["receipts"].append(str(path.relative_to(repo)))
        delivery = value.get("delivery", {})
        status = delivery.get("status") if isinstance(delivery, dict) else delivery
        completion = value.get("completion", {})
        if status == "sent_verified" or (isinstance(completion, dict) and completion.get("delivery") == "complete_sent_verified"):
            result["sent_verified"] = True
        for name in ("audit", "collection", "content", "editorial"):
            state = value.get(name)
            if isinstance(state, dict):
                if state.get("complete") or state.get("status") not in (None, "not_started", "not_completed"):
                    result["work_started"] = True
            elif state not in (None, "not_started", "not_completed"):
                result["work_started"] = True
    return result


def listed_worktrees(repo: Path):
    result = []
    for block in git(repo, "worktree", "list", "--porcelain").stdout.split("\n\n"):
        row = {}
        for line in block.splitlines():
            key, _, value = line.partition(" ")
            row[key] = value
        if row.get("worktree"):
            result.append(row)
    return result


def atomic_json(path: Path, value: dict):
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


@contextlib.contextmanager
def registry_lock(path: Path):
    # Lock a stable file rather than deleting stale PID files. A dead process
    # releases the OS lock automatically, including on Windows.
    with path.open("a+b") as handle:
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise PreparationError("bootstrap_already_running") from exc
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def prepare(*, entry: Path, date: str, worktree_root: Path, state_dir: Path,
            expected_remote: str = EXPECTED_REMOTE, minimum_commit: str = MINIMUM_COMMIT,
            target_branch: str = TARGET_BRANCH, timeout: int = 90):
    try:
        if dt.date.fromisoformat(date).isoformat() != date:
            raise ValueError
    except ValueError as exc:
        raise PreparationError("invalid_business_date") from exc
    entry, worktree_root, state_dir = entry.resolve(), worktree_root.resolve(), state_dir.resolve()
    if not re.fullmatch(r"[0-9a-fA-F]{40,64}", minimum_commit):
        raise PreparationError("invalid_minimum_commit")
    if within(worktree_root, PROTECTED_MAIN) or within(state_dir, PROTECTED_MAIN):
        raise PreparationError("protected_main_destination")
    repository = common_dir(entry)
    actual_remote = git(entry, "remote", "get-url", "origin").stdout.strip()
    if actual_remote != expected_remote:
        raise PreparationError("unexpected_remote")
    if git(entry, "check-ref-format", f"refs/heads/{target_branch}", check=False).returncode:
        raise PreparationError("invalid_target_branch")
    initial_head = git(entry, "rev-parse", "HEAD").stdout.strip()
    initial_status = git(entry, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout
    state_dir.mkdir(parents=True, exist_ok=True)
    worktree_root.mkdir(parents=True, exist_ok=True)
    registry_path = state_dir / f"{date}_workspace.json"
    with registry_lock(state_dir / f"{date}_bootstrap.lock"):
        registered = None
        if registry_path.exists():
            registered = read_json(registry_path)
            if registered.get("business_date") != date or Path(registered.get("repository_common_dir", "")).resolve() != repository:
                raise PreparationError("registry_repository_or_date_mismatch")
            path = Path(registered.get("worktree", "")).resolve()
            if not path.is_dir() or not within(path, worktree_root) or within(path, PROTECTED_MAIN):
                raise PreparationError("registered_worktree_missing_or_outside_root")
        candidates = []
        rejected = []
        prefix = f"refs/heads/codex/automation-4-{date}"
        for row in listed_worktrees(entry):
            path = Path(row["worktree"]).resolve()
            if not path.is_dir() or not within(path, worktree_root) or within(path, PROTECTED_MAIN):
                continue
            is_registered = registered is not None and path == Path(registered["worktree"]).resolve()
            branch = row.get("branch", "")
            branch_matches = branch == prefix or branch.startswith(prefix + "-")
            if not is_registered and not branch_matches:
                continue
            if common_dir(path) != repository:
                raise PreparationError("candidate_repository_mismatch")
            checks = checkpoint(path, date)
            if not minimum_verified(path, minimum_commit):
                if checks["work_started"] or checks["sent_verified"] or is_registered:
                    raise PreparationError("existing_run_minimum_version_failed", path.name)
                rejected.append({"worktree": str(path), "reason": "old_entry_without_started_work"})
                continue
            if not is_registered and not checks["work_started"] and not checks["sent_verified"]:
                rejected.append({"worktree": str(path), "reason": "unregistered_preflight_only_entry"})
                continue
            candidates.append({"worktree": str(path), "branch": branch.removeprefix("refs/heads/"),
                               "head": git(path, "rev-parse", "HEAD").stdout.strip(),
                               "registered": is_registered, **checks})
        if registered and not any(x["registered"] for x in candidates):
            raise PreparationError("registered_worktree_not_listed")
        sent = [x for x in candidates if x["sent_verified"]]
        if len(sent) > 1:
            raise PreparationError("multiple_sent_worktrees_verify_mail")
        if sent:
            chosen, action = sent[0], "verify_already_sent"
        elif len(candidates) == 1:
            chosen, action = candidates[0], "resume_existing"
        elif len(candidates) > 1:
            raise PreparationError("multiple_existing_runs_need_resolution")
        else:
            chosen = None
        if chosen:
            result = {"status": "ready", "action": action, "business_date": date,
                      "repository_common_dir": str(repository), "worktree": chosen["worktree"],
                      "branch": chosen["branch"], "head": chosen["head"], "minimum_version_verified": True,
                      "entry": str(entry), "entry_head": initial_head, "entry_dirty": bool(initial_status),
                      "collection_must_not_restart": True, "mail_must_be_checked_before_send": True,
                      "receipts": chosen["receipts"], "rejected_old_entries": rejected, "updated_at": utc_now()}
            if registered and registered.get("base_commit"):
                result["base_commit"] = registered["base_commit"]
            atomic_json(registry_path, result)
            return result

        remote_ref = f"refs/remotes/origin/{target_branch}"
        base = None
        for _ in range(2):
            # The plus updates only the remote-tracking cache after a server
            # rewrite. It never resets a local branch or force-pushes anything.
            git(entry, "fetch", "--no-tags", "origin", f"+refs/heads/{target_branch}:{remote_ref}", timeout=timeout)
            fetched = git(entry, "rev-parse", remote_ref).stdout.strip()
            advertised = git(entry, "ls-remote", "--exit-code", "origin", f"refs/heads/{target_branch}", timeout=timeout).stdout.split()
            if len(advertised) == 2 and advertised[0] == fetched and advertised[1] == f"refs/heads/{target_branch}":
                base = fetched
                break
        if base is None:
            raise PreparationError("remote_changed_during_verification")
        if git(entry, "merge-base", "--is-ancestor", minimum_commit, base, check=False).returncode:
            raise PreparationError("remote_minimum_version_failed")
        counts = git(entry, "rev-list", "--left-right", "--count", f"{initial_head}...{base}").stdout.split()
        suffix = uuid.uuid4().hex[:10]
        branch = f"codex/automation-4-{date}-{suffix}"
        destination = worktree_root / f"automation-4-{date}-{suffix}"
        if destination.exists() or not within(destination, worktree_root):
            raise PreparationError("new_worktree_destination_not_empty")
        git(entry, "worktree", "add", "-b", branch, str(destination), base, timeout=timeout)
        git(destination, "branch", "--set-upstream-to", f"origin/{target_branch}", branch)
        if git(destination, "rev-parse", "HEAD").stdout.strip() != base or git(destination, "status", "--porcelain=v1").stdout:
            raise PreparationError("new_worktree_verification_failed")
        if git(entry, "rev-parse", "HEAD").stdout.strip() != initial_head or git(entry, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout != initial_status:
            raise PreparationError("entry_changed_during_preparation")
        result = {"status": "ready", "action": "new_from_verified_remote", "business_date": date,
                  "repository_common_dir": str(repository), "worktree": str(destination), "branch": branch,
                  "head": base, "base_commit": base, "minimum_version_verified": True, "remote_live_verified": True,
                  "entry": str(entry), "entry_head": initial_head, "entry_dirty": bool(initial_status),
                  "entry_local_only_commits": int(counts[0]), "remote_only_commits": int(counts[1]),
                  "entry_preserved": True, "collection_must_not_restart": False,
                  "mail_must_be_checked_before_send": True, "rejected_old_entries": rejected, "updated_at": utc_now()}
        atomic_json(registry_path, result)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entry", type=Path, required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--worktree-root", type=Path, default=Path.home() / ".codex/worktrees")
    parser.add_argument("--state-dir", type=Path, default=Path.home() / ".codex/automations/automation-4/runs")
    parser.add_argument("--expected-remote", default=EXPECTED_REMOTE)
    parser.add_argument("--minimum-commit", default=MINIMUM_COMMIT)
    parser.add_argument("--target-branch", default=TARGET_BRANCH)
    parser.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args()
    try:
        result = prepare(**vars(args))
    except PreparationError as exc:
        print(json.dumps({"status": "blocked", "code": exc.code, "operation": exc.operation}, ensure_ascii=False))
        return 2
    except OSError:
        print(json.dumps({"status": "blocked", "code": "filesystem_operation_failed"}))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
