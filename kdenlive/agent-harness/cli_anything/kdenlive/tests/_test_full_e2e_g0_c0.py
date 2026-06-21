# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestWorkflowE2EMixin0:
    def test_basic_edit_workflow(self):
        proj = create_project(name="BasicEdit", profile="hd1080p30")
        import_clip(proj, "/footage/scene1.mp4", name="Scene1", duration=60.0)
        add_track(proj, track_type="video")
        add_clip_to_track(proj, 0, "clip0", position=0.0, out_point=30.0)
        root = ET.fromstring(generate_kdenlive_xml(proj))
        sources = [c.find("property[@name='resource']").text for c in root.findall("chain") if c.find("property[@name='resource']") is not None]
        assert any("scene1.mp4" in s for s in sources)
        entries = root.findall(".//playlist/entry")
        assert len(entries) > 0
    def test_multicam_workflow(self):
        proj = create_project(name="Multicam")
        import_clip(proj, "/cam1.mp4", name="Cam1", duration=60.0)
        import_clip(proj, "/cam2.mp4", name="Cam2", duration=60.0)
        add_track(proj, name="V1", track_type="video")
        add_track(proj, name="V2", track_type="video")
        add_clip_to_track(proj, 0, "clip0", position=0.0, out_point=30.0)
        add_clip_to_track(proj, 1, "clip1", position=0.0, out_point=30.0)
        tracks = list_tracks(proj)
        assert len(tracks) == 2
        root = ET.fromstring(generate_kdenlive_xml(proj))
        playlist_ids = [p.get("id") for p in root.findall("playlist")]
        assert "playlist0" in playlist_ids
        assert "playlist1" in playlist_ids
    def test_audio_video_workflow(self):
        proj = create_project(name="AV")
        import_clip(proj, "/video.mp4", name="Video", duration=60.0)
        import_clip(proj, "/music.mp3", name="Music", duration=180.0, clip_type="audio")
        add_track(proj, track_type="video")
        add_track(proj, track_type="audio")
        add_clip_to_track(proj, 0, "clip0", out_point=60.0)
        add_clip_to_track(proj, 1, "clip1", out_point=60.0)
        root = ET.fromstring(generate_kdenlive_xml(proj))
        sources = [c.find("property[@name='resource']").text for c in root.findall("chain") if c.find("property[@name='resource']") is not None]
        assert any("video.mp4" in s for s in sources)
        assert any("music.mp3" in s for s in sources)
    def test_trim_and_split_workflow(self):
        proj = create_project()
        import_clip(proj, "/long.mp4", name="Long", duration=120.0)
        add_track(proj)
        add_clip_to_track(proj, 0, "clip0", out_point=120.0)
        trim_clip(proj, 0, 0, new_in=10.0, new_out=110.0)
        parts = split_clip(proj, 0, 0, split_at=50.0)
        assert len(parts) == 2
        assert len(proj["tracks"][0]["clips"]) == 2
    def test_filter_chain_workflow(self):
        proj = create_project()
        import_clip(proj, "/video.mp4", name="V", duration=30.0)
        add_track(proj)
        add_clip_to_track(proj, 0, "clip0", out_point=30.0)

        add_filter(proj, 0, 0, "brightness", {"level": 1.3})
        add_filter(proj, 0, 0, "contrast", {"level": 1.1})
        add_filter(proj, 0, 0, "saturation", {"saturation": 1.5})

        filters = list_filters(proj, 0, 0)
        assert len(filters) == 3

        root = ET.fromstring(generate_kdenlive_xml(proj))
        user_filters = root.findall(".//entry/filter")
        assert len(user_filters) == 3
    def test_transition_workflow(self):
        proj = create_project()
        import_clip(proj, "/a.mp4", name="A", duration=30.0)
        import_clip(proj, "/b.mp4", name="B", duration=30.0)
        add_track(proj, track_type="video")
        add_track(proj, track_type="video")
        add_clip_to_track(proj, 0, "clip0", position=0.0, out_point=15.0)
        add_clip_to_track(proj, 1, "clip1", position=10.0, out_point=15.0)
        add_transition(proj, "dissolve", 0, 1, position=10.0, duration=5.0)

        transitions = list_transitions(proj)
        assert len(transitions) == 1
        root = ET.fromstring(generate_kdenlive_xml(proj))
        seq = _find_sequence(root)
        assert seq is not None
        user_trans = [t for t in seq.findall("transition") if t.find("property[@name='internal_added']") is None]
        assert len(user_trans) >= 1
    def test_guide_workflow(self):
        proj = create_project()
        add_guide(proj, 0.0, label="Intro")
        add_guide(proj, 30.0, label="Main Content")
        add_guide(proj, 120.0, label="Outro")

        guides = list_guides(proj)
        assert len(guides) == 3

        root = ET.fromstring(generate_kdenlive_xml(proj))
        seq = _find_sequence(root)
        assert seq is not None
        guides_prop = seq.find("property[@name='kdenlive:sequenceproperties.guides']")
        assert guides_prop is not None
        data = json.loads(guides_prop.text)
        assert len(data) == 3
        assert data[0]["comment"] == "Intro"
        assert data[1]["comment"] == "Main Content"
        assert data[2]["comment"] == "Outro"
