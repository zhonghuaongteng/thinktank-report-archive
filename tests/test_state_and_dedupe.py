import unittest

from thinktank_watch.fetch import canonical_url, dedupe_key, make_client


class StateAndDedupeTests(unittest.TestCase):
    def test_canonical_url_removes_tracking_fragment_and_duplicate_slash(self):
        url = "https://example.org//reports/ai/?utm_source=newsletter&utm_medium=email#section"

        self.assertEqual(canonical_url(url), "https://example.org/reports/ai")

    def test_dedupe_key_uses_canonical_url(self):
        first = "https://example.org/reports/ai/?utm_source=newsletter#summary"
        second = "https://example.org/reports/ai"

        self.assertEqual(dedupe_key(first), dedupe_key(second))

    def test_make_client_uses_browser_like_user_agent(self):
        with make_client() as client:
            user_agent = client.headers["User-Agent"]

        self.assertIn("Mozilla/5.0", user_agent)
        self.assertIn("thinktank-watch", user_agent)


if __name__ == "__main__":
    unittest.main()
