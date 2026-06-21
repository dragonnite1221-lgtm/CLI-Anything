# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestSaveLoadRoundtrip:
    """Test save/load roundtrips."""

    def test_full_roundtrip(self):
        proj = create_project(name="roundtrip_test")
        add_scene(proj, name="Extra")
        add_source(proj, "video_capture", scene_index=0, name="Camera")
        add_source(proj, "image", scene_index=1, name="BG")
        add_filter(proj, "chroma_key", 0, scene_index=0)
        add_audio_source(proj, name="Mic")
        add_transition(proj, "fade", duration=500)
        set_streaming(proj, service="youtube")
        set_recording(proj, fmt="mp4")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            save_project(proj, path)
            loaded = open_project(path)

            assert loaded["name"] == "roundtrip_test"
            assert len(loaded["scenes"]) == 2
            assert len(loaded["scenes"][0]["sources"]) == 1
            assert len(loaded["scenes"][0]["sources"][0]["filters"]) == 1
            assert len(loaded["audio_sources"]) == 1
            assert len(loaded["transitions"]) == 3
            assert loaded["streaming"]["service"] == "youtube"
            assert loaded["recording"]["format"] == "mp4"
        finally:
            os.unlink(path)

    def test_save_load_preserves_source_transforms(self):
        proj = create_project()
        add_source(
            proj,
            "image",
            name="Logo",
            position={"x": 100, "y": 200},
            size={"width": 300, "height": 300},
        )
        transform_source(proj, 0, crop={"top": 10, "bottom": 10, "left": 5, "right": 5})

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            save_project(proj, path)
            loaded = open_project(path)
            src = loaded["scenes"][0]["sources"][0]
            assert src["position"]["x"] == 100
            assert src["size"]["width"] == 300
            assert src["crop"]["top"] == 10
        finally:
            os.unlink(path)
