import unittest

from thinktank_watch.parsers.rand import parse_rand_detail


RAND_COMMENTARY_HTML = """
<html><head>
<meta property="og:title" content="Will We Know if AI Takes Over? Q&amp;A with Benjamin Boudreaux">
<meta name="citation_online_date" content="2026/6/10">
<meta name="keywords" content="Artificial Intelligence, Emerging Technologies, Modeling and Simulation">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Article","headline":"Will We Know if AI Takes Over? Q&A with Benjamin Boudreaux","datePublished":"2026-06-10","author":[{"@type":"Person","name":"Benjamin Boudreaux"}],"description":"AI could erode human agency over time."}
</script>
</head><body><main><p>Agency is the capacity that lets us set and pursue every other value.</p></main></body></html>
"""


RAND_REPORT_HTML = """
<html><head>
<meta name="citation_title" content="Insights from table-top exercises in Europe on AI safety and cyber misuse">
<meta name="citation_publication_date" content="2026/7/1">
<meta name="citation_author" content="Shamir, Afek">
<meta name="citation_author" content="Zakaria, Sana">
<meta name="citation_pdf_url" content="www.rand.org/content/dam/rand/pubs/research_reports/RRA5000/RRA5082-1/RAND_RRA5082-1.pdf">
<meta name="DC.Subject" content="Cybersecurity">
<meta name="DC.Subject" content="Artificial Intelligence">
<meta name="keywords" content="Day After Methodology, Cybersecurity, Artificial Intelligence">
</head><body><main><p>This report presents findings from table-top exercises.</p></main></body></html>
"""


class RandParserTests(unittest.TestCase):
    def test_commentary_uses_json_ld_author_and_online_date(self):
        detail = parse_rand_detail(
            RAND_COMMENTARY_HTML,
            "https://www.rand.org/pubs/commentary/2026/06/will-we-know-if-ai-takes-over.html",
        )

        self.assertEqual(detail.title, "Will We Know if AI Takes Over? Q&A with Benjamin Boudreaux")
        self.assertEqual(detail.published_date, "2026-06-10")
        self.assertEqual(detail.authors, ["Benjamin Boudreaux"])
        self.assertIn("Artificial Intelligence", detail.keywords)
        self.assertEqual(detail.content_type, "commentary")
        self.assertEqual(detail.source_completeness, "full_text")

    def test_report_uses_citation_metadata_and_pdf_url(self):
        detail = parse_rand_detail(
            RAND_REPORT_HTML,
            "https://www.rand.org/pubs/research_reports/RRA5082-1.html",
        )

        self.assertEqual(detail.title, "Insights from table-top exercises in Europe on AI safety and cyber misuse")
        self.assertEqual(detail.published_date, "2026-07-01")
        self.assertEqual(detail.authors, ["Shamir, Afek", "Zakaria, Sana"])
        self.assertEqual(
            detail.pdf_url,
            "https://www.rand.org/content/dam/rand/pubs/research_reports/RRA5000/RRA5082-1/RAND_RRA5082-1.pdf",
        )
        self.assertIn("Artificial Intelligence", detail.subjects)
        self.assertEqual(detail.content_type, "rand_report")


if __name__ == "__main__":
    unittest.main()
