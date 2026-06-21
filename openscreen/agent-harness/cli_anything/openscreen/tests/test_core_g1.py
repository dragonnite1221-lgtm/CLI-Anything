# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestProject:
    def test_new_project(self):
        s = Session()
        result = proj_mod.new_project(s)
        assert result["status"] == "created"
        assert s.is_open

    def test_info(self):
        s = Session()
        s.new_project()
        result = proj_mod.info(s)
        assert result["version"] == 2
        assert result["aspect_ratio"] == "16:9"
        assert result["zoom_regions"] == 0

    def test_info_without_project(self):
        s = Session()
        with pytest.raises(RuntimeError, match="No project"):
            proj_mod.info(s)

    def test_set_setting(self):
        s = Session()
        s.new_project()
        result = proj_mod.set_setting(s, "padding", 30)
        assert result["value"] == 30
        assert s.editor["padding"] == 30

    def test_set_invalid_setting(self):
        s = Session()
        s.new_project()
        with pytest.raises(ValueError, match="Unknown setting"):
            proj_mod.set_setting(s, "nonexistent_key", 42)

    # ── Extra tests from auto version ──────────────────────────────────

    def test_set_setting_aspectRatio(self):
        s = Session()
        s.new_project()
        proj_mod.set_setting(s, "aspectRatio", "9:16")
        assert s.editor["aspectRatio"] == "9:16"

    def test_set_setting_invalid_aspectRatio(self):
        s = Session()
        s.new_project()
        with pytest.raises(ValueError):
            proj_mod.set_setting(s, "aspectRatio", "invalid")

    def test_set_setting_exportQuality(self):
        s = Session()
        s.new_project()
        proj_mod.set_setting(s, "exportQuality", "source")
        assert s.editor["exportQuality"] == "source"

    def test_set_setting_exportFormat(self):
        s = Session()
        s.new_project()
        proj_mod.set_setting(s, "exportFormat", "gif")
        assert s.editor["exportFormat"] == "gif"

    def test_set_setting_invalid_exportFormat(self):
        s = Session()
        s.new_project()
        with pytest.raises(ValueError):
            proj_mod.set_setting(s, "exportFormat", "avi")

    def test_set_setting_padding_valid(self):
        s = Session()
        s.new_project()
        proj_mod.set_setting(s, "padding", 30)
        assert s.editor["padding"] == 30

    def test_set_setting_padding_too_large(self):
        s = Session()
        s.new_project()
        with pytest.raises(ValueError):
            proj_mod.set_setting(s, "padding", 101)

    def test_set_setting_calls_checkpoint(self):
        s = Session()
        s.new_project()
        proj_mod.set_setting(s, "padding", 10)
        assert len(s._undo_stack) >= 1

    def test_crop_region_validation_in_settings(self):
        s = Session()
        s.new_project()
        valid_crop = {"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.8}
        proj_mod.set_setting(s, "cropRegion", valid_crop)
        assert s.editor["cropRegion"] == valid_crop

    def test_crop_region_overflow_raises(self):
        s = Session()
        s.new_project()
        with pytest.raises(ValueError):
            proj_mod.set_setting(
                s, "cropRegion", {"x": 0.5, "y": 0.0, "width": 0.8, "height": 1.0}
            )
