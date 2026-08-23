from __future__ import annotations

import unittest

from scripts.extend_viewpoint_fraunhofer_isi_selected_fulltexts import SELECTED_ITEMS, selected_ids


class FraunhoferIsiSelectedFulltextsTests(unittest.TestCase):
    def test_batch_is_exactly_the_four_bounded_innovation_mechanism_reports(self) -> None:
        self.assertEqual(
            selected_ids(),
            {
                "C-FRAUNHOFER-ISI-DP-51",
                "C-FRAUNHOFER-ISI-DP-53",
                "C-FRAUNHOFER-ISI-DP-65",
                "C-FRAUNHOFER-ISI-DP-83",
            },
        )
        self.assertEqual(len(SELECTED_ITEMS), 4)

    def test_security_language_does_not_define_the_batch(self) -> None:
        titles = " ".join(item["title"] for item in SELECTED_ITEMS)
        self.assertNotRegex(titles.lower(), r"security|supply chain|export control|military|defen[cs]e")


if __name__ == "__main__":
    unittest.main()
