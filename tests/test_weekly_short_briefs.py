import unittest
from bs4 import BeautifulSoup
from thinktank_watch.models import ArticleCandidate
from thinktank_watch.brief import render_weekly_magazine_html, render_weekly_reader_markdown


class WeeklyShortBriefTests(unittest.TestCase):
    def test_authored_short_brief_survives_reader_html_and_markdown(self):
        item=ArticleCandidate('source','Institution','think_tank','Original','https://example.org/report',
            priority='P2',chinese_title='一条简讯',chinese_summary='核心观点：这是已复核简讯的完整内容与局限。',published_date='2026-09-27')
        html=render_weekly_magazine_html('2026-09-27',[item])
        soup=BeautifulSoup(html,'html.parser')
        self.assertEqual(soup.select_one('.short-brief a')['href'],item.url)
        self.assertIn('完整内容与局限',soup.select_one('.short-brief').get_text())
        self.assertIn('完整内容与局限',render_weekly_reader_markdown('2026-09-27',[item]))
