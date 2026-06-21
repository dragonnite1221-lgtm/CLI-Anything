# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestProject:
    def test_new_project(self):
        s = Session()
        result = proj_mod.new_project(s, "letter")
        assert result["action"] == "new_project"
        assert result["preset"] == "letter"
        assert s.is_open

    def test_new_project_all_presets(self):
        for name in proj_mod.PAGE_PRESETS:
            s = Session()
            result = proj_mod.new_project(s, name)
            assert result["action"] == "new_project"
            assert s.is_open

    def test_new_project_invalid_preset(self):
        s = Session()
        with pytest.raises(ValueError, match="Unknown preset"):
            proj_mod.new_project(s, "nonexistent")

    def test_new_project_custom_size(self):
        s = Session()
        result = proj_mod.new_project(s, "custom", width=1920, height=1080)
        assert result["page_size"] == "1920x1080"

    def test_save_and_open(self):
        s = Session()
        proj_mod.new_project(s, "a4")
        shapes_mod.add_shape(s, "rectangle", label="Test")

        with tempfile.NamedTemporaryFile(suffix=".drawio", delete=False) as f:
            path = f.name

        try:
            proj_mod.save_project(s, path)
            assert os.path.exists(path)

            s2 = Session()
            result = proj_mod.open_project(s2, path)
            assert result["action"] == "open_project"
            assert result["shape_count"] == 1
        finally:
            os.unlink(path)

    def test_project_info(self):
        s = Session()
        proj_mod.new_project(s, "letter")
        shapes_mod.add_shape(s, "rectangle", label="A")
        shapes_mod.add_shape(s, "ellipse", label="B")
        info = proj_mod.project_info(s)
        assert len(info["shapes"]) == 2
        assert info["canvas"]["pageWidth"] == "850"

    def test_project_info_no_project(self):
        s = Session()
        with pytest.raises(RuntimeError, match="No project is open"):
            proj_mod.project_info(s)

    def test_list_presets(self):
        presets = proj_mod.list_presets()
        assert "letter" in presets
        assert "a4" in presets
