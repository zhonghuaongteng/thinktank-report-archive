import unittest
from scripts.check_weekly_volume import validate

def fixture(features=6, briefs=10):
    items = [{'url': f'https://example.org/{i}', 'priority': 'P1' if i < features else 'P2',
              'highlights_markdown': '完整解读', 'chinese_summary': '具体简讯'} for i in range(features+briefs)]
    rows = [{'URL': x['url'], '最终处置': '重点' if x['priority']=='P1' else '简讯'} for x in items]
    return items, rows

class WeeklyVolumeTests(unittest.TestCase):
    def test_minimum_and_more(self):
        self.assertTrue(validate(*fixture())['passed'])
        self.assertTrue(validate(*fixture(7, 11))['passed'])
    def test_categories_cannot_offset(self):
        self.assertFalse(validate(*fixture(5, 20))['passed'])
        self.assertFalse(validate(*fixture(20, 9))['passed'])
    def test_duplicate_does_not_count(self):
        items, rows = fixture()
        items[-1] = items[-2].copy()
        self.assertFalse(validate(items, rows)['passed'])
    def test_decisions_and_content_match(self):
        items, rows = fixture()
        rows[-1]['最终处置'] = '排除'
        self.assertFalse(validate(items, rows)['passed'])
        items, rows = fixture()
        items[0]['highlights_markdown'] = ''
        self.assertFalse(validate(items, rows)['passed'])
