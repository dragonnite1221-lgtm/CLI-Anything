# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestZoom:
    def test_add_zoom(self):
        s = Session()
        s.new_project()
        result = tl_mod.add_zoom_region(
            s, 1000, 5000, depth=3, focus_x=0.5, focus_y=0.5
        )
        assert result["startMs"] == 1000
        assert result["endMs"] == 5000
        assert result["depth"] == 3
        assert "id" in result

    def test_list_zoom(self):
        s = Session()
        s.new_project()
        assert len(tl_mod.list_zoom_regions(s)) == 0
        tl_mod.add_zoom_region(s, 1000, 2000)
        assert len(tl_mod.list_zoom_regions(s)) == 1

    def test_remove_zoom(self):
        s = Session()
        s.new_project()
        z = tl_mod.add_zoom_region(s, 1000, 2000)
        tl_mod.remove_zoom_region(s, z["id"])
        assert len(tl_mod.list_zoom_regions(s)) == 0

    def test_remove_nonexistent_zoom(self):
        s = Session()
        s.new_project()
        with pytest.raises(ValueError, match="not found"):
            tl_mod.remove_zoom_region(s, "nonexistent_id")

    def test_invalid_depth(self):
        s = Session()
        s.new_project()
        with pytest.raises(ValueError, match="Invalid depth"):
            tl_mod.add_zoom_region(s, 1000, 2000, depth=7)

    def test_invalid_focus(self):
        s = Session()
        s.new_project()
        with pytest.raises(ValueError, match="Focus coordinates"):
            tl_mod.add_zoom_region(s, 1000, 2000, focus_x=1.5)

    def test_invalid_time_range(self):
        s = Session()
        s.new_project()
        with pytest.raises(ValueError, match="end_ms.*must be"):
            tl_mod.add_zoom_region(s, 5000, 1000)

    def test_zoom_undo(self):
        s = Session()
        s.new_project()
        tl_mod.add_zoom_region(s, 1000, 2000)
        assert len(tl_mod.list_zoom_regions(s)) == 1
        s.undo()
        assert len(tl_mod.list_zoom_regions(s)) == 0

    # ── Extra tests from auto version ──────────────────────────────────

    def test_add_zoom_focus(self):
        s = Session()
        s.new_project()
        region = tl_mod.add_zoom_region(s, 0, 2000, depth=3, focus_x=0.3, focus_y=0.7)
        assert region["focus"]["cx"] == 0.3
        assert region["focus"]["cy"] == 0.7

    def test_list_zoom_sorted(self):
        s = Session()
        s.new_project()
        tl_mod.add_zoom_region(s, 5000, 8000, depth=1)
        tl_mod.add_zoom_region(s, 1000, 3000, depth=2)
        regions = tl_mod.list_zoom_regions(s)
        starts = [r["startMs"] for r in regions]
        assert starts == sorted(starts)

    def test_update_zoom_region(self):
        s = Session()
        s.new_project()
        region = tl_mod.add_zoom_region(s, 1000, 3000, depth=1)
        updated = tl_mod.update_zoom_region(s, region["id"], depth=4, focus_x=0.8)
        assert updated["depth"] == 4
        assert updated["focus"]["cx"] == 0.8

    def test_update_zoom_nonexistent(self):
        s = Session()
        s.new_project()
        with pytest.raises((ValueError, KeyError)):
            tl_mod.update_zoom_region(s, "fake-id")

    def test_zoom_depth_map_values(self):
        # ZOOM_DEPTHS maps depth int -> scale factor
        from cli_anything.openscreen.core.timeline import ZOOM_DEPTHS

        assert ZOOM_DEPTHS[1] == 1.25
        assert ZOOM_DEPTHS[6] == 5.0

    def test_add_zoom_calls_checkpoint(self):
        s = Session()
        s.new_project()
        initial = len(s._undo_stack)
        tl_mod.add_zoom_region(s, 0, 1000, depth=2)
        assert len(s._undo_stack) > initial
