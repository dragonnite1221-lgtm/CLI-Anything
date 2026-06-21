# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSVGUtils:
    def test_parse_style(self):
        result = parse_style("fill:#ff0000;stroke:#000;stroke-width:2")
        assert result["fill"] == "#ff0000"
        assert result["stroke"] == "#000"
        assert result["stroke-width"] == "2"

    def test_parse_empty_style(self):
        assert parse_style("") == {}
        assert parse_style(None) == {}

    def test_serialize_style(self):
        s = serialize_style({"fill": "#ff0000", "stroke": "#000"})
        assert "fill:#ff0000" in s
        assert "stroke:#000" in s

    def test_serialize_empty_style(self):
        assert serialize_style({}) == ""

    def test_roundtrip_style(self):
        original = "fill:#ff0000;stroke:#000000;stroke-width:2"
        parsed = parse_style(original)
        serialized = serialize_style(parsed)
        reparsed = parse_style(serialized)
        assert reparsed == parsed

    def test_validate_color_hex(self):
        assert validate_color("#ff0000")
        assert validate_color("#fff")
        assert validate_color("#aabbcc")

    def test_validate_color_named(self):
        assert validate_color("red")
        assert validate_color("blue")
        assert validate_color("transparent")
        assert validate_color("none")

    def test_validate_color_rgb(self):
        assert validate_color("rgb(255,0,0)")
        assert validate_color("rgba(255,0,0,0.5)")

    def test_validate_color_invalid(self):
        assert not validate_color("")
        assert not validate_color(None)

    def test_generate_id(self):
        id1 = generate_id("test")
        id2 = generate_id("test")
        assert id1 != id2
        assert id1.startswith("test")

    def test_create_svg_element(self):
        svg = create_svg_element(800, 600, "px")
        assert svg.tag == f"{{{SVG_NS}}}svg"
        assert svg.get("width") == "800px"
        assert svg.get("height") == "600px"

    def test_serialize_svg(self):
        svg = create_svg_element()
        xml_str = serialize_svg(svg)
        assert "<?xml" in xml_str
        assert "svg" in xml_str

    def test_find_defs(self):
        svg = create_svg_element()
        defs = find_defs(svg)
        assert defs is not None
        assert defs.tag == f"{{{SVG_NS}}}defs"
