# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestExport:
    def test_list_presets(self):
        presets = list_presets()
        assert len(presets) > 0
        names = [p["name"] for p in presets]
        assert "png_web" in names
        assert "svg" in names
        assert "pdf" in names

    def test_all_presets_have_format(self):
        for name, preset in EXPORT_PRESETS.items():
            assert "format" in preset
            assert "dpi" in preset
            assert "description" in preset
