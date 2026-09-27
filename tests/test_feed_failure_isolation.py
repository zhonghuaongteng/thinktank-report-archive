from http.client import RemoteDisconnected, IncompleteRead
from unittest.mock import patch
import unittest
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import feedparser
import httpx

from thinktank_watch.fetch import fetch_feed_candidates
from thinktank_watch.models import Institution


class FeedFailureIsolationTests(unittest.TestCase):
    def setUp(self):
        self.client_patch=patch("thinktank_watch.fetch.make_client")
        self.client=self.client_patch.start().return_value.__enter__.return_value
        self.addCleanup(self.client_patch.stop)
        self.client.get.return_value=httpx.Response(200,content=b"",request=httpx.Request('GET','https://example.org/working'))

    def institution(self):
        return Institution(
            slug="example", name="Example", chinese_name="示例",
            country_region="US", institution_type="think_tank", priority="P1",
            batch=1, homepage="https://example.org", parser="generic",
            copyright_boundary="metadata_only",
            feeds=["https://example.org/broken", "https://example.org/working"],
        )

    def successful_feed(self):
        return feedparser.FeedParserDict(entries=[feedparser.FeedParserDict(
            title="A research finding", link="https://example.org/research/finding",
            published="Sun, 27 Sep 2026 06:00:00 GMT",
        )])

    def test_transport_failure_preserves_later_feed_and_reports_exact_source(self):
        for failure in [ConnectionResetError(10054, "reset"),
                        RemoteDisconnected("closed"), IncompleteRead(b"", 10)]:
            with self.subTest(error=type(failure).__name__), patch(
                "thinktank_watch.fetch.feedparser.parse",
                side_effect=[failure, self.successful_feed()],
            ), self.assertLogs("thinktank_watch.fetch", level="WARNING") as logs:
                candidates = fetch_feed_candidates(self.institution())
                self.assertEqual(len(candidates), 1)
                self.assertIn("url=https://example.org/broken", logs.output[0])
                self.assertIn(type(failure).__name__, logs.output[0])

    def test_returned_http_failure_is_not_reported_as_empty_success(self):
        with patch("thinktank_watch.fetch.feedparser.parse", side_effect=[
            feedparser.FeedParserDict(entries=[], status=503), self.successful_feed()
        ]), self.assertLogs("thinktank_watch.fetch", level="WARNING") as logs:
            self.assertEqual(len(fetch_feed_candidates(self.institution())), 1)
            self.assertIn("status=503", logs.output[0])

    def test_unexpected_programming_error_still_propagates(self):
        with patch("thinktank_watch.fetch.feedparser.parse", side_effect=ValueError("bug")):
            with self.assertRaises(ValueError):
                fetch_feed_candidates(self.institution())

    def test_timeout_skips_only_failed_feed_and_resolves_relative_links(self):
        xml=b'<rss version="2.0"><channel><title>Research</title><item><title>Finding</title><link>/research/finding</link></item></channel></rss>'
        response=httpx.Response(200,content=xml,request=httpx.Request('GET','https://example.org/working'))
        self.client.get.side_effect=[httpx.ReadTimeout('timeout'),response]
        with self.assertLogs('thinktank_watch.fetch',level='WARNING') as logs:
            items=fetch_feed_candidates(self.institution())
        self.assertEqual([c.url for c in items],['https://example.org/research/finding'])
        self.assertIn('ReadTimeout',logs.output[0])
        self.assertEqual(self.client.get.call_args_list[0].kwargs['timeout'],30)

    @unittest.skipUnless(os.name=='nt' and shutil.which('powershell'), 'Windows PowerShell integration')
    def test_cli_warning_does_not_abort_powershell_redirected_run(self):
        code='from unittest.mock import patch; from types import SimpleNamespace; import logging; from thinktank_watch.cli import main; p=patch("thinktank_watch.cli.build_parser"); m=p.start(); m.return_value.parse_args.return_value=SimpleNamespace(func=lambda args: logging.getLogger("thinktank_watch.fetch").warning("feed_fetch_failed test") or 0); raise SystemExit(main([]))'
        quote=lambda s:"'"+str(s).replace("'","''")+"'"
        with TemporaryDirectory() as tmp:
            log=Path(tmp)/'run.log'
            script=Path(tmp)/'probe.py'
            script.write_text('import sys,os; sys.path.insert(0,os.getcwd()); '+code,encoding='utf-8')
            command=f"$ErrorActionPreference='Stop'; & {quote(sys.executable)} {quote(script)} *> {quote(log)}; if ($LASTEXITCODE -ne 0) {{ exit $LASTEXITCODE }}; Write-Output 'wrapper_survived'"
            result=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('wrapper_survived',result.stdout)
            self.assertIn('feed_fetch_failed',log.read_text(encoding='utf-16'))
