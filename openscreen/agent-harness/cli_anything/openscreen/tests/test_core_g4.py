# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSpeed:
    def test_add_speed(self):
        s = Session()
        s.new_project()
        result = tl_mod.add_speed_region(s, 5000, 10000, speed=2.0)
        assert result["speed"] == 2.0

    def test_invalid_speed(self):
        s = Session()
        s.new_project()
        with pytest.raises(ValueError, match="Invalid speed"):
            tl_mod.add_speed_region(s, 1000, 2000, speed=3.0)

    def test_list_and_remove(self):
        s = Session()
        s.new_project()
        r = tl_mod.add_speed_region(s, 1000, 2000, speed=1.5)
        assert len(tl_mod.list_speed_regions(s)) == 1
        tl_mod.remove_speed_region(s, r["id"])
        assert len(tl_mod.list_speed_regions(s)) == 0

    # ── Extra tests from auto version ──────────────────────────────────

    def test_add_speed_all_valid_values(self):
        from cli_anything.openscreen.core.timeline import VALID_SPEEDS

        s = Session()
        s.new_project()
        for speed in VALID_SPEEDS:
            region = tl_mod.add_speed_region(s, 0, 1000, speed=speed)
            assert region["speed"] == speed

    def test_list_speed_sorted(self):
        s = Session()
        s.new_project()
        tl_mod.add_speed_region(s, 5000, 8000, speed=1.5)
        tl_mod.add_speed_region(s, 1000, 3000, speed=2.0)
        regions = tl_mod.list_speed_regions(s)
        starts = [r["startMs"] for r in regions]
        assert starts == sorted(starts)

    def test_remove_speed_nonexistent(self):
        s = Session()
        s.new_project()
        with pytest.raises((ValueError, KeyError)):
            tl_mod.remove_speed_region(s, "nonexistent")


class TestTrim:
    def test_add_trim(self):
        s = Session()
        s.new_project()
        result = tl_mod.add_trim_region(s, 0, 1000)
        assert result["startMs"] == 0
        assert result["endMs"] == 1000

    def test_list_and_remove(self):
        s = Session()
        s.new_project()
        r = tl_mod.add_trim_region(s, 0, 1000)
        assert len(tl_mod.list_trim_regions(s)) == 1
        tl_mod.remove_trim_region(s, r["id"])
        assert len(tl_mod.list_trim_regions(s)) == 0

    # ── Extra tests from auto version ──────────────────────────────────

    def test_add_trim_zero_start(self):
        s = Session()
        s.new_project()
        region = tl_mod.add_trim_region(s, 0, 1000)
        assert region["startMs"] == 0

    def test_list_trim_sorted(self):
        s = Session()
        s.new_project()
        tl_mod.add_trim_region(s, 8000, 10000)
        tl_mod.add_trim_region(s, 1000, 3000)
        regions = tl_mod.list_trim_regions(s)
        starts = [r["startMs"] for r in regions]
        assert starts == sorted(starts)

    def test_remove_trim_nonexistent(self):
        s = Session()
        s.new_project()
        with pytest.raises((ValueError, KeyError)):
            tl_mod.remove_trim_region(s, "fake")
