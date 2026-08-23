from scripts.backfill_viewpoint_china_research_system_nodes import SELECTED_ITEMS


def test_batch_is_bounded_and_technology_first() -> None:
    assert len(SELECTED_ITEMS) == 6
    assert {item["institution_id"] for item in SELECTED_ITEMS} == {"cset", "eu-jrc"}
    assert all("中国" in item["role"] for item in SELECTED_ITEMS)
    assert all("安全" not in item["role"] for item in SELECTED_ITEMS)


def test_selected_ids_are_unique() -> None:
    ids = [item["id"] for item in SELECTED_ITEMS]
    assert len(ids) == len(set(ids))
