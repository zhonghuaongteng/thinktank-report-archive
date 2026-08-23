from scripts.backfill_viewpoint_science_mobility_transfer_nodes import SELECTED_ITEMS


def test_batch_is_bounded_and_science_innovation_first() -> None:
    assert len(SELECTED_ITEMS) == 6
    assert {item["institution_id"] for item in SELECTED_ITEMS} == {"eu-jrc", "jp-rieti"}
    assert all(any(term in item["axes"] for term in ("科学", "研发", "产业创新", "科技人才")) for item in SELECTED_ITEMS)
    assert not any(any(term in item["title"].lower() for term in ("military", "export control", "security", "supply chain")) for item in SELECTED_ITEMS)


def test_selected_assets_are_unique_official_pdfs() -> None:
    ids = [item["id"] for item in SELECTED_ITEMS]
    assert len(ids) == len(set(ids))
    assert all(item["asset_url"].startswith("https://") and item["asset_url"].endswith(".pdf") for item in SELECTED_ITEMS)
