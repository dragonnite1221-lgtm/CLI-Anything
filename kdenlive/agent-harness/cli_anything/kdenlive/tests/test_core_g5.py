# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestGuides:
    def _make_project(self):
        return create_project()

    def test_add_guide(self):
        proj = self._make_project()
        g = add_guide(proj, 10.0, label="Intro")
        assert g["position"] == 10.0
        assert g["label"] == "Intro"

    def test_add_guide_types(self):
        proj = self._make_project()
        for gt in GUIDE_TYPES:
            g = add_guide(proj, 1.0, guide_type=gt)
            assert g["type"] == gt

    def test_add_guide_invalid_type(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Invalid guide type"):
            add_guide(proj, 1.0, guide_type="invalid")

    def test_add_guide_negative_position(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="non-negative"):
            add_guide(proj, -1.0)

    def test_guides_sorted_by_position(self):
        proj = self._make_project()
        add_guide(proj, 20.0, label="B")
        add_guide(proj, 5.0, label="A")
        guides = proj["guides"]
        assert guides[0]["position"] <= guides[1]["position"]

    def test_remove_guide(self):
        proj = self._make_project()
        g = add_guide(proj, 10.0)
        removed = remove_guide(proj, g["id"])
        assert removed["position"] == 10.0
        assert len(proj["guides"]) == 0

    def test_remove_guide_not_found(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Guide not found"):
            remove_guide(proj, 999)

    def test_list_guides(self):
        proj = self._make_project()
        add_guide(proj, 5.0, label="A")
        add_guide(proj, 10.0, label="B")
        guides = list_guides(proj)
        assert len(guides) == 2


class TestTimecodeUtils:
    def test_seconds_to_timecode_zero(self):
        assert seconds_to_timecode(0) == "00:00:00.000"

    def test_seconds_to_timecode_simple(self):
        assert seconds_to_timecode(65.5) == "00:01:05.500"

    def test_seconds_to_timecode_hours(self):
        assert seconds_to_timecode(3661.123) == "01:01:01.123"

    def test_seconds_to_timecode_negative(self):
        with pytest.raises(ValueError, match="non-negative"):
            seconds_to_timecode(-1.0)

    def test_timecode_to_seconds_simple(self):
        assert timecode_to_seconds("00:01:05.500") == 65.5

    def test_timecode_to_seconds_hours(self):
        result = timecode_to_seconds("01:01:01.123")
        assert abs(result - 3661.123) < 0.001

    def test_timecode_to_seconds_plain_float(self):
        assert timecode_to_seconds("30.5") == 30.5

    def test_timecode_to_seconds_invalid(self):
        with pytest.raises(ValueError, match="Invalid timecode"):
            timecode_to_seconds("invalid")

    def test_roundtrip_timecode(self):
        for val in [0.0, 1.5, 60.0, 3600.0, 7261.789]:
            tc = seconds_to_timecode(val)
            back = timecode_to_seconds(tc)
            assert abs(back - val) < 0.002

    def test_seconds_to_frames(self):
        assert seconds_to_frames(1.0, 30, 1) == 30
        assert seconds_to_frames(2.0, 25, 1) == 50

    def test_frames_to_seconds(self):
        assert frames_to_seconds(30, 30, 1) == 1.0
        assert frames_to_seconds(50, 25, 1) == 2.0

    def test_xml_escape(self):
        assert xml_escape('a<b>c&d"e') == "a&lt;b&gt;c&amp;d&quot;e"

    def test_xml_escape_apostrophe(self):
        assert xml_escape("it's") == "it&apos;s"
