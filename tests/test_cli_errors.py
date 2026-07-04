import unittest

import httpx

from thinktank_watch.cli import fetch_status_from_http_error


class CliErrorTests(unittest.TestCase):
    def test_fetch_status_from_http_error_includes_status_code(self):
        request = httpx.Request("GET", "https://example.org/report")
        response = httpx.Response(403, request=request)
        error = httpx.HTTPStatusError("forbidden", request=request, response=response)

        self.assertEqual(fetch_status_from_http_error(error), "detail_error:403")


if __name__ == "__main__":
    unittest.main()
