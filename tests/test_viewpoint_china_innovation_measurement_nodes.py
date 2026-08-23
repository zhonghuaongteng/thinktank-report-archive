from scripts.backfill_viewpoint_china_innovation_measurement_nodes import SELECTED_ITEMS


def test_batch_is_bounded_and_technology_first() -> None:
    assert len(SELECTED_ITEMS) == 6
    assert {item["institution_id"] for item in SELECTED_ITEMS} == {"eu-jrc", "csis-rai"}
    assert all("中国" in item["role"] for item in SELECTED_ITEMS)
    assert all("军事" not in item["role"] and "制裁" not in item["role"] for item in SELECTED_ITEMS)


def test_selected_assets_are_unique() -> None:
    ids = [item["id"] for item in SELECTED_ITEMS]
    assert len(ids) == len(set(ids))
    assert sum(item["asset_type"] == "pdf" for item in SELECTED_ITEMS) == 5
