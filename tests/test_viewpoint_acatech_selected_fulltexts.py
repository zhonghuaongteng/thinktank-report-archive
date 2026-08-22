import unittest

from scripts.extend_viewpoint_acatech_selected_fulltexts import SELECTED, SELECTED_IDS, selected_slice


class AcatechSelectedFulltextsTests(unittest.TestCase):
    def test_selection_covers_engineering_science_and_technology_innovation(self):
        titles = " ".join(item[2] for item in SELECTED).lower()
        for signal in ("engineering", "industrie 4.0", "quantentechnologien", "biotechnologie", "kernfusion", "ki-standortanalyse"):
            self.assertIn(signal, titles)
        self.assertEqual(len(SELECTED_IDS), 12)

    def test_selection_contains_direct_china_comparison_without_security_led_titles(self):
        titles = " ".join(item[2] for item in SELECTED).lower()
        self.assertIn("globalen kontext", titles)
        for signal in ("sicherheit", "militär", "verteidigung", "souveränität", "resilienz"):
            self.assertNotIn(signal, titles)

    def test_slice_keeps_german_science_and_innovation_mechanisms(self):
        source = (
            "Forschung und Entwicklung verbinden wissenschaftliche Kompetenz, Engineering und Technologietransfer.\n\n"
            "Dieser lange Verwaltungsabsatz enthält absichtlich keinen einschlägigen Mechanismus und soll nicht aufgenommen werden."
        )
        output = selected_slice("Engineering", source)
        self.assertIn("科学技术创新定向摘录", output)
        self.assertIn("Forschung und Entwicklung", output)
        self.assertNotIn("Verwaltungsabsatz", output)


if __name__ == "__main__":
    unittest.main()
