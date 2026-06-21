# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


def test_layout_create_add_items_and_remove(tmp_path: Path):
    _create_polygon_project(tmp_path, name="layout_demo")

    created = layouts_mod.create_layout("Main", page_size="A4", orientation="portrait")
    assert created["name"] == "Main"

    with_map = layouts_mod.add_map_item("Main", 10, 20, 180, 120)
    assert any(item["type"] == "QgsLayoutItemMap" for item in with_map["items"])

    with_label = layouts_mod.add_label_item(
        "Main", "Demo map", 10, 8, 80, 10, font_size=16
    )
    assert any(item["type"] == "QgsLayoutItemLabel" for item in with_label["items"])

    listing = layouts_mod.list_layouts()
    assert listing["count"] == 1
    assert listing["layouts"][0]["name"] == "Main"

    removed = layouts_mod.remove_layout("Main")
    assert removed["name"] == "Main"
    assert layouts_mod.list_layouts()["count"] == 0
