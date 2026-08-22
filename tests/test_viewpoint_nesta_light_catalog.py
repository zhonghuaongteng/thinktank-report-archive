from __future__ import annotations

import unittest

from scripts.extend_viewpoint_nesta_light_catalog import (
    eligible_for_science_innovation_catalog,
    parse_report_page,
    parse_sitemap,
    science_innovation_themes,
)


class NestaLightCatalogTests(unittest.TestCase):
    def test_parse_sitemap_keeps_canonical_report_pages(self) -> None:
        source = """
        <urlset>
          <url><loc>https://www.nesta.org.uk/report/</loc></url>
          <url><loc>https://www.nesta.org.uk/report/how-innovation-agencies-work/</loc></url>
          <url><loc>https://www.nesta.org.uk/blog/a-post/</loc></url>
          <url><loc>https://www.nesta.org.uk/report/how-innovation-agencies-work/chapter/</loc></url>
        </urlset>
        """
        self.assertEqual(
            parse_sitemap(source),
            ["https://www.nesta.org.uk/report/how-innovation-agencies-work/"],
        )

    def test_parse_report_page_extracts_official_metadata_and_download(self) -> None:
        source = """
        <html><head>
        <script type="application/ld+json">{
          "@type": "WebPage",
          "name": "How innovation agencies work",
          "description": "How governments design and run innovation agencies."
        }</script></head><body>
        <script>dataLayer.push({
          'areasOfWork': 'Innovation policy',
          'publishDate': '2016-05-23'
        });</script>
        <div class="page-heading__downloads">
          <a href="/documents/123/innovation_agencies.pdf">Full report</a>
        </div>
        </body></html>
        """
        row = parse_report_page(
            source,
            "https://www.nesta.org.uk/report/how-innovation-agencies-work/",
        )
        self.assertEqual(row.title, "How innovation agencies work")
        self.assertEqual(row.published_date.isoformat(), "2016-05-23")
        self.assertEqual(row.categories, ("Innovation policy",))
        self.assertEqual(
            row.pdf_urls,
            ("https://www.nesta.org.uk/documents/123/innovation_agencies.pdf",),
        )

    def test_science_and_technology_signals_qualify_without_security_terms(self) -> None:
        themes = science_innovation_themes(
            "Innovating UK Innovation Policy",
            "A mission-led advanced research funding body for breakthrough technologies.",
            ("Innovation policy",),
        )
        self.assertIn("科学体系与基础研究", themes)
        self.assertIn("技术创新与关键技术", themes)
        self.assertIn("创新政策与研发治理", themes)

    def test_security_alone_does_not_qualify(self) -> None:
        themes = science_innovation_themes(
            "Security for resilient public services",
            "A governance framework for public-sector resilience.",
            ("Government innovation",),
        )
        self.assertEqual(themes, ())

    def test_generic_research_and_social_innovation_do_not_qualify(self) -> None:
        generic_research = parse_report_page(
            """<script type="application/ld+json">{"name":"School readiness","description":"A new research report on childhood."}</script>
            <script>dataLayer.push({'publishDate':'2024-02-01','areasOfWork':'Education'});</script>""",
            "https://www.nesta.org.uk/report/school-readiness/",
        )
        social_innovation = parse_report_page(
            """<script type="application/ld+json">{"name":"Scaling social innovation","description":"Community approaches to wellbeing."}</script>
            <script>dataLayer.push({'publishDate':'2020-02-01','areasOfWork':'Innovation policy'});</script>""",
            "https://www.nesta.org.uk/report/scaling-social-innovation/",
        )
        self.assertFalse(eligible_for_science_innovation_catalog(generic_research))
        self.assertFalse(eligible_for_science_innovation_catalog(social_innovation))

    def test_date_window_and_theme_are_both_required(self) -> None:
        in_scope = parse_report_page(
            """<script type="application/ld+json">{"name":"R&amp;D policy","description":"Research funding"}</script>
            <script>dataLayer.push({'publishDate':'2024-02-01','areasOfWork':'Innovation policy'});</script>""",
            "https://www.nesta.org.uk/report/rd-policy/",
        )
        old = parse_report_page(
            """<script type="application/ld+json">{"name":"R&amp;D policy","description":"Research funding"}</script>
            <script>dataLayer.push({'publishDate':'2013-02-01','areasOfWork':'Innovation policy'});</script>""",
            "https://www.nesta.org.uk/report/old-rd-policy/",
        )
        self.assertTrue(eligible_for_science_innovation_catalog(in_scope))
        self.assertFalse(eligible_for_science_innovation_catalog(old))

    def test_makerspaces_are_treated_as_technology_innovation_infrastructure(self) -> None:
        report = parse_report_page(
            """<script type="application/ld+json">{"name":"Made in China: Makerspaces and the search for mass innovation","description":"A survey of almost 100 makerspaces in China."}</script>
            <script>dataLayer.push({'publishDate':'2016-03-29','areasOfWork':'Innovation policy'});</script>""",
            "https://www.nesta.org.uk/report/made-in-china-makerspaces-and-the-search-for-mass-innovation/",
        )
        self.assertTrue(eligible_for_science_innovation_catalog(report))
        self.assertIn(
            "技术创新与关键技术",
            science_innovation_themes(report.title, report.description, report.categories),
        )


if __name__ == "__main__":
    unittest.main()
