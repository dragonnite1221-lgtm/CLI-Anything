# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestIntegration:
    def test_full_workflow(self):
        """Test a complete project workflow: create, edit, save, reopen."""
        s = Session()
        s.new_project()

        # Set settings
        proj_mod.set_setting(s, "aspectRatio", "16:9")
        proj_mod.set_setting(s, "wallpaper", "gradient_dark")
        proj_mod.set_setting(s, "padding", 40)

        # Add regions
        z1 = tl_mod.add_zoom_region(s, 2000, 5000, depth=3, focus_x=0.7, focus_y=0.3)
        z2 = tl_mod.add_zoom_region(s, 8000, 12000, depth=4, focus_x=0.5, focus_y=0.5)
        sp = tl_mod.add_speed_region(s, 15000, 20000, speed=2.0)
        tr = tl_mod.add_trim_region(s, 0, 500)
        ann = tl_mod.add_text_annotation(s, 5000, 7000, "Click here!")
        tl_mod.set_crop(s, 0, 0, 1, 1)

        # Verify counts
        info = proj_mod.info(s)
        assert info["zoom_regions"] == 2
        assert info["speed_regions"] == 1
        assert info["trim_regions"] == 1
        assert info["annotations"] == 1

        # Save and reopen
        with tempfile.NamedTemporaryFile(suffix=".openscreen", delete=False) as f:
            path = f.name
        try:
            s.save_project(path)

            s2 = Session()
            s2.open_project(path)
            info2 = proj_mod.info(s2)
            assert info2["zoom_regions"] == 2
            assert info2["speed_regions"] == 1
            assert info2["annotations"] == 1
        finally:
            os.unlink(path)

    def test_export_presets(self):
        """Test that export presets are available."""
        presets = export_mod.list_presets()
        assert len(presets) > 0
        assert any(p["name"] == "mp4_good" for p in presets)

    # ── Extra tests from auto version ──────────────────────────────────

    def test_undo_redo_zoom_workflow(self):
        s = Session()
        s.new_project()
        tl_mod.add_zoom_region(s, 1000, 3000, depth=2)
        assert len(tl_mod.list_zoom_regions(s)) == 1

        s.undo()
        assert len(tl_mod.list_zoom_regions(s)) == 0

        s.redo()
        assert len(tl_mod.list_zoom_regions(s)) == 1

    def test_multiple_undo_levels(self):
        s = Session()
        s.new_project()
        for i in range(5):
            tl_mod.add_zoom_region(s, i * 1000, (i + 1) * 1000, depth=1)

        assert len(tl_mod.list_zoom_regions(s)) == 5
        for _ in range(5):
            s.undo()
        assert len(tl_mod.list_zoom_regions(s)) == 0

    def test_timeline_boundaries(self):
        s = Session()
        s.new_project()
        tl_mod.add_zoom_region(s, 1000, 3000, depth=1)
        tl_mod.add_speed_region(s, 2000, 5000, speed=1.5)
        tl_mod.add_trim_region(s, 4000, 6000)

        boundaries = tl_mod.get_timeline_boundaries(s)
        assert 0 in boundaries
        assert 1000 in boundaries
        assert 2000 in boundaries
        assert 3000 in boundaries
        assert 4000 in boundaries
        assert 5000 in boundaries
        assert 6000 in boundaries

    def test_active_regions_at(self):
        s = Session()
        s.new_project()
        tl_mod.add_zoom_region(s, 1000, 5000, depth=2)
        tl_mod.add_speed_region(s, 2000, 4000, speed=1.5)
        tl_mod.add_trim_region(s, 6000, 8000)

        active = tl_mod.get_active_regions_at(s, 3000)
        assert len(active["zoom"]) == 1
        assert len(active["speed"]) == 1
        assert len(active["trim"]) == 0

        active2 = tl_mod.get_active_regions_at(s, 7000)
        assert len(active2["trim"]) == 1
        assert len(active2["zoom"]) == 0

    def test_project_set_triggers_undo(self):
        s = Session()
        s.new_project()
        proj_mod.set_setting(s, "padding", 10)
        proj_mod.set_setting(s, "padding", 30)
        assert s.editor["padding"] == 30
        s.undo()
        assert s.editor["padding"] == 10
