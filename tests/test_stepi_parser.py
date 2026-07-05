import unittest

import httpx

from thinktank_watch.fetch import fetch_detail
from thinktank_watch.models import ArticleCandidate, Institution
from thinktank_watch.parsers.stepi import extract_stepi_publication_candidates, parse_stepi_detail


def stepi_institution() -> Institution:
    return Institution(
        slug="stepi",
        name="Science and Technology Policy Institute Korea",
        chinese_name="韩国科学技术政策研究院",
        country_region="Korea",
        institution_type="government_research_institute",
        priority="P1",
        batch=3,
        homepage="https://www.stepi.re.kr/site/stepien/main.do",
        parser="generic",
        copyright_boundary="private_archive",
    )


class StepiParserTests(unittest.TestCase):
    def test_extract_stepi_publication_candidates_from_board_rows(self):
        html = """
        <ul>
          <li>
            <em class="cate cate3">STEPI Insight</em>
            <span class="title">Role and Challenges of Small Businesses from the Perspective of Transformative Innovation Policy</span>
            <ul class="info">
              <li><b>BY :</b>Jieun Seong·Hyejin Jo</li>
              <li><b>DATE :</b>2026-04-27</li>
              <li><b>HIT :</b>904</li>
            </ul>
            <div class="boardBtn">
              <a href="/common/report/Download.do?
                reIdx=134
                &amp;cateCont=A0508
                &amp;streFileNm=example.pdf">Download PDF</a>
            </div>
          </li>
        </ul>
        """

        candidates = extract_stepi_publication_candidates(
            html,
            "https://www.stepi.re.kr/site/stepien/ex/bbs/List.do?cbIdx=1303",
            stepi_institution(),
            limit=5,
        )

        self.assertEqual(len(candidates), 1)
        self.assertEqual(
            candidates[0].title,
            "Role and Challenges of Small Businesses from the Perspective of Transformative Innovation Policy",
        )
        self.assertEqual(candidates[0].published_date, "2026-04-27")
        self.assertEqual(candidates[0].authors, ["Jieun Seong", "Hyejin Jo"])
        self.assertEqual(candidates[0].subjects, ["STEPI Insight"])
        self.assertEqual(
            candidates[0].url,
            "https://www.stepi.re.kr/site/stepien/ex/bbs/publicationView.do?pageIndex=1&cbIdx=1303&reIdx=134&cateCont=A0508",
        )
        self.assertEqual(
            candidates[0].pdf_url,
            "https://www.stepi.re.kr/common/report/Download.do?reIdx=134&cateCont=A0508&streFileNm=example.pdf",
        )

    def test_parse_stepi_detail_uses_board_view_instead_of_breadcrumb_title(self):
        html = """
        <html><head><title>Publications &gt; Publications</title></head>
        <body>
          <div class="boardView">
            <h4 class="title">A Framework for Legislative Impact Assessment For the Science and Technology Innovation Transition</h4>
            <p class="info">
              <span><b>BY :</b>Jieun Jeon</span>
              <span><b>DATE :</b>2026-04-20</span>
              <span><b>HIT :</b>756</span>
            </p>
            <div class="viewCon"><p>Science and technology innovation transition text.</p></div>
          </div>
        </body></html>
        """

        detail = parse_stepi_detail(
            html,
            "https://www.stepi.re.kr/site/stepien/ex/bbs/publicationView.do?pageIndex=1&cbIdx=1303&reIdx=131&cateCont=A0508",
            stepi_institution(),
        )

        self.assertEqual(
            detail.title,
            "A Framework for Legislative Impact Assessment For the Science and Technology Innovation Transition",
        )
        self.assertEqual(detail.published_date, "2026-04-20")
        self.assertEqual(detail.authors, ["Jieun Jeon"])
        self.assertEqual(detail.detail_text, "Science and technology innovation transition text.")

    def test_fetch_detail_preserves_stepi_pdf_url_from_list_candidate(self):
        url = "https://www.stepi.re.kr/site/stepien/ex/bbs/publicationView.do?pageIndex=1&cbIdx=1303&reIdx=131&cateCont=A0508"
        html = """
        <html><body>
          <div class="boardView">
            <h4 class="title">A Framework for Legislative Impact Assessment For the Science and Technology Innovation Transition</h4>
            <p class="info"><span><b>DATE :</b>2026-04-20</span></p>
            <div class="viewCon"><p><br /></p></div>
          </div>
        </body></html>
        """

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text=html, request=request)

        candidate = ArticleCandidate(
            institution_slug="stepi",
            institution_name="Science and Technology Policy Institute Korea",
            institution_type="government_research_institute",
            title="A Framework for Legislative Impact Assessment For the Science and Technology Innovation Transition",
            url=url,
            published_date="2026-04-20",
            content_type="report",
            pdf_url="https://www.stepi.re.kr/common/report/Download.do?reIdx=131&cateCont=A0508&streFileNm=example.pdf",
        )
        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            detail = fetch_detail(client, stepi_institution(), candidate)

        self.assertEqual(detail.pdf_url, candidate.pdf_url)
        self.assertEqual(detail.source_completeness, "full_text")


if __name__ == "__main__":
    unittest.main()
