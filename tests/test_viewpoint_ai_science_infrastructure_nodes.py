from scripts.backfill_viewpoint_ai_science_infrastructure_nodes import SELECTED_ITEMS


def test_batch_is_bounded_and_ai_science_infrastructure_first() -> None:
    assert len(SELECTED_ITEMS) == 5
    assert {item["institution_id"] for item in SELECTED_ITEMS} == {"oecd-sti", "us-nasem", "eu-jrc"}
    assert all(any(term in item["axes"] for term in ("AI for Science", "科学体系", "科研")) for item in SELECTED_ITEMS)
    assert not any(any(term in item["title"].lower() for term in ("military", "export control", "supply chain")) for item in SELECTED_ITEMS)


def test_selected_assets_are_unique_and_official() -> None:
    ids = [item["id"] for item in SELECTED_ITEMS]
    assert len(ids) == len(set(ids))
    assert all(item["landing_url"].startswith("https://") for item in SELECTED_ITEMS)
    assert all(item["asset_url"].startswith("https://") for item in SELECTED_ITEMS)
    assert sum(item["kind"] == "pdf" for item in SELECTED_ITEMS) == 3
    assert sum(item["kind"] == "nasem" for item in SELECTED_ITEMS) == 2
