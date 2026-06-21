# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


def _make_project(**overrides):
    """Create a minimal valid project dict, applying any overrides."""
    proj = create_document(name="TestProject")
    proj.update(overrides)
    return proj


def _make_wrapper_script(path: Path) -> Path:
    path.write_text(
        "#!/bin/bash\n"
        "SCRIPT_MODE=1\n"
        "xvfb-run freecadcmd \"$@\"\n",
        encoding="utf-8",
    )
    return path


class TestDocument:
    """Tests for the document module."""

    def test_create_default(self):
        proj = create_document()
        assert proj["name"] == "Untitled"
        assert proj["units"] == "mm"
        assert proj["version"] == "1.0"
        assert proj["parts"] == []
        assert proj["sketches"] == []
        assert proj["bodies"] == []
        assert proj["materials"] == []
        assert "created" in proj["metadata"]
        assert "modified" in proj["metadata"]
        assert "software" in proj["metadata"]

    def test_create_with_profile(self):
        proj = create_document(name="ImperialProject", profile="imperial")
        assert proj["units"] == "in"
        assert proj["name"] == "ImperialProject"

        proj2 = create_document(profile="metric_large")
        assert proj2["units"] == "m"

    def test_create_invalid_profile(self):
        with pytest.raises(ValueError, match="Unknown profile"):
            create_document(profile="nonexistent_profile")

    def test_save_and_open(self, tmp_path):
        proj = create_document(name="RoundTrip", units="mm")
        add_part(proj, "box", name="TestBox")

        filepath = str(tmp_path / "roundtrip.json")
        abs_path = save_document(proj, filepath)
        assert os.path.isfile(abs_path)

        loaded = open_document(filepath)
        assert loaded["name"] == "RoundTrip"
        assert loaded["units"] == "mm"
        assert len(loaded["parts"]) == 1
        assert loaded["parts"][0]["name"] == "TestBox"

    def test_open_nonexistent(self, tmp_path):
        missing = str(tmp_path / "does_not_exist.json")
        with pytest.raises(FileNotFoundError):
            open_document(missing)

    def test_get_info(self):
        proj = create_document(name="InfoTest")
        info = get_document_info(proj)
        assert info["name"] == "InfoTest"
        assert info["units"] == "mm"
        assert info["parts_count"] == 0
        assert info["sketches_count"] == 0
        assert info["bodies_count"] == 0
        assert info["materials_count"] == 0
        assert info["motions_count"] == 0

    def test_get_info_with_data(self):
        proj = create_document(name="DataTest")
        add_part(proj, "box")
        add_part(proj, "cylinder")
        create_sketch(proj)

        info = get_document_info(proj)
        assert info["parts_count"] == 2
        assert info["sketches_count"] == 1

    def test_list_profiles(self):
        profiles = list_profiles()
        assert isinstance(profiles, list)
        assert len(profiles) == len(PROFILES)
        names = {p["name"] for p in profiles}
        assert "default" in names
        assert "imperial" in names
        for p in profiles:
            assert "name" in p
            assert "units" in p
            assert "description" in p
