import unittest
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

import httpx

from thinktank_watch.cli import evaluate, fetch_status_from_http_error
from thinktank_watch.models import ArticleCandidate, Institution


class CliErrorTests(unittest.TestCase):
    def test_fetch_status_from_http_error_includes_status_code(self):
        request = httpx.Request("GET", "https://example.org/report")
        response = httpx.Response(403, request=request)
        error = httpx.HTTPStatusError("forbidden", request=request, response=response)

        self.assertEqual(fetch_status_from_http_error(error), "detail_error:403")

    def test_evaluate_prints_detail_error_status(self):
        institution = Institution(
            slug="ceps",
            name="Centre for European Policy Studies",
            chinese_name="欧洲政策研究中心",
            country_region="European Union",
            institution_type="think_tank",
            priority="P0",
            batch=2,
            homepage="https://www.ceps.eu/ceps-topics/",
            parser="generic",
            copyright_boundary="private_archive",
        )
        candidate = ArticleCandidate(
            institution_slug="ceps",
            institution_name="Centre for European Policy Studies",
            institution_type="think_tank",
            title="Shared gains, secure links",
            url="https://www.ceps.eu/ceps-publications/shared-gains-secure-links-rethinking-eu-asia-digital-cooperation/",
            published_date="2026-06-01",
            priority="P3",
            score=1,
            fetch_status="detail_error:403",
        )
        args = SimpleNamespace(batch=None, institution="ceps", limit=5, no_details=False, backfill=True)
        output = StringIO()

        with (
            patch("thinktank_watch.cli._load_config", return_value=([institution], [], object())),
            patch("thinktank_watch.cli.collect_candidates", return_value=[candidate]),
            patch("thinktank_watch.cli.score_candidate", side_effect=lambda item, topics, priorities: item),
            redirect_stdout(output),
        ):
            evaluate(args)

        self.assertIn("status: detail_error:403", output.getvalue())


if __name__ == "__main__":
    unittest.main()
