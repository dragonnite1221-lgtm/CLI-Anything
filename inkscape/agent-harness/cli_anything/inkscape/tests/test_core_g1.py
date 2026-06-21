# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestDocument:
    def test_create_default(self):
        proj = create_document()
        assert proj["document"]["width"] == 1920
        assert proj["document"]["height"] == 1080
        assert proj["document"]["units"] == "px"
        assert proj["version"] == "1.0"

    def test_create_with_dimensions(self):
        proj = create_document(width=800, height=600)
        assert proj["document"]["width"] == 800
        assert proj["document"]["height"] == 600

    def test_create_with_profile(self):
        proj = create_document(profile="a4_portrait")
        assert proj["document"]["width"] == 210
        assert proj["document"]["height"] == 297
        assert proj["document"]["units"] == "mm"

    def test_create_with_icon_profile(self):
        proj = create_document(profile="icon_256")
        assert proj["document"]["width"] == 256
        assert proj["document"]["height"] == 256

    def test_create_invalid_units(self):
        with pytest.raises(ValueError, match="Invalid units"):
            create_document(units="em")

    def test_create_invalid_dimensions(self):
        with pytest.raises(ValueError, match="must be positive"):
            create_document(width=0, height=100)

    def test_create_has_default_layer(self):
        proj = create_document()
        assert len(proj["layers"]) == 1
        assert proj["layers"][0]["name"] == "Layer 1"

    def test_save_and_open(self):
        proj = create_document(name="test_doc")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            save_document(proj, path)
            loaded = open_document(path)
            assert loaded["name"] == "test_doc"
            assert loaded["document"]["width"] == 1920
        finally:
            os.unlink(path)

    def test_open_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            open_document("/nonexistent/path.json")

    def test_get_info(self):
        proj = create_document(name="info_test")
        info = get_document_info(proj)
        assert info["name"] == "info_test"
        assert info["counts"]["objects"] == 0
        assert info["counts"]["layers"] == 1

    def test_set_canvas_size(self):
        proj = create_document()
        result = set_canvas_size(proj, 800, 600)
        assert proj["document"]["width"] == 800
        assert proj["document"]["height"] == 600
        assert "old_size" in result

    def test_set_canvas_size_invalid(self):
        proj = create_document()
        with pytest.raises(ValueError, match="must be positive"):
            set_canvas_size(proj, 0, 0)

    def test_set_units(self):
        proj = create_document()
        result = set_units(proj, "mm")
        assert proj["document"]["units"] == "mm"
        assert result["old_units"] == "px"

    def test_set_units_invalid(self):
        proj = create_document()
        with pytest.raises(ValueError, match="Invalid units"):
            set_units(proj, "em")

    def test_list_profiles(self):
        profiles = list_profiles()
        assert len(profiles) > 0
        names = [p["name"] for p in profiles]
        assert "default" in names
        assert "a4_portrait" in names
        assert "hd1080p" in names

    def test_all_valid_units(self):
        for unit in VALID_UNITS:
            proj = create_document(units=unit)
            assert proj["document"]["units"] == unit

    def test_project_to_svg(self):
        proj = create_document(name="svg_test", width=800, height=600)
        svg = project_to_svg(proj)
        assert svg.tag == f"{{{SVG_NS}}}svg"
        assert "800" in svg.get("width", "")

    def test_project_to_svg_wrapped_text_uses_tspans(self):
        proj = create_document(name="svg_text_wrap", width=800, height=600)
        add_text(
            proj,
            text="Real capture plus Veo cold open plus Gemini score",
            x=20,
            y=40,
            box_width=140,
            font_size=20,
        )
        svg = project_to_svg(proj)
        text_nodes = list(svg.iter(f"{{{SVG_NS}}}text"))
        assert len(text_nodes) == 1
        tspans = list(text_nodes[0].iter(f"{{{SVG_NS}}}tspan"))
        assert len(tspans) > 1
