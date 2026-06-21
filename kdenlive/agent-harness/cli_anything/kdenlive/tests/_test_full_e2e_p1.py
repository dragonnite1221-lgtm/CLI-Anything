# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class TestFormatValidation:
    def test_json_roundtrip(self):
        proj = create_project(name="roundtrip")
        import_clip(proj, "/a.mp4", name="A", duration=10.0)
        add_track(proj)
        add_clip_to_track(proj, 0, "clip0", out_point=10.0)
        add_guide(proj, 5.0, label="Mid")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
        try:
            save_project(proj, path)
            loaded = open_project(path)
            assert loaded["name"] == "roundtrip"
            assert len(loaded["bin"]) == 1
            assert len(loaded["tracks"]) == 1
            assert len(loaded["tracks"][0]["clips"]) == 1
            assert len(loaded["guides"]) == 1
        finally:
            os.unlink(path)

    def test_json_has_all_required_keys(self):
        proj = create_project()
        required = ["version", "name", "profile", "bin", "tracks",
                     "transitions", "guides", "metadata"]
        for key in required:
            assert key in proj, f"Missing key: {key}"

    def test_profile_has_all_required_fields(self):
        proj = create_project()
        profile_keys = ["name", "width", "height", "fps_num", "fps_den",
                        "progressive", "dar_num", "dar_den"]
        for key in profile_keys:
            assert key in proj["profile"], f"Missing profile key: {key}"

    def test_clip_entry_has_required_fields(self):
        proj = create_project()
        import_clip(proj, "/a.mp4", name="A", duration=10.0)
        clip = proj["bin"][0]
        for key in ["id", "name", "source", "duration", "type"]:
            assert key in clip, f"Missing clip key: {key}"

    def test_track_entry_has_required_fields(self):
        proj = create_project()
        add_track(proj)
        track = proj["tracks"][0]
        for key in ["id", "name", "type", "mute", "hide", "locked", "clips"]:
            assert key in track, f"Missing track key: {key}"

    def test_timeline_clip_entry_has_required_fields(self):
        proj = create_project()
        import_clip(proj, "/a.mp4", name="A", duration=10.0)
        add_track(proj)
        add_clip_to_track(proj, 0, "clip0", out_point=5.0)
        entry = proj["tracks"][0]["clips"][0]
        for key in ["clip_id", "in", "out", "position", "filters"]:
            assert key in entry, f"Missing timeline clip key: {key}"

    def test_xml_well_formed_basic(self):
        proj = create_project()
        import_clip(proj, "/a.mp4", name="A", duration=10.0)
        add_track(proj)
        add_clip_to_track(proj, 0, "clip0", out_point=5.0)
        root = ET.fromstring(generate_kdenlive_xml(proj))
        assert root.tag == "mlt"

    def test_xml_chain_count_for_bin_clips(self):
        proj = create_project()
        import_clip(proj, "/a.mp4", name="A", duration=10.0)
        import_clip(proj, "/b.mp4", name="B", duration=20.0)
        add_track(proj)
        add_clip_to_track(proj, 0, "clip0", out_point=10.0)
        root = ET.fromstring(generate_kdenlive_xml(proj))
        # 1 track chain for clip0 + 2 bin chains (clip0 and clip1)
        chains = root.findall("chain")
        assert len(chains) >= 3


class TestMeltBackend:
    """Tests that verify melt is installed and accessible."""

    def test_melt_is_installed(self):
        from cli_anything.kdenlive.utils.melt_backend import find_melt
        path = find_melt()
        assert os.path.exists(path)
        print(f"\n  melt binary: {path}")

    def test_melt_version(self):
        from cli_anything.kdenlive.utils.melt_backend import get_melt_version
        version = get_melt_version()
        assert version
        print(f"\n  melt version: {version}")
