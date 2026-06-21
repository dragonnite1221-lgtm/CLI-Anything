# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestStreamSetupWorkflow:
    """Test setting up a complete streaming configuration."""

    def test_full_stream_setup(self):
        # Create project
        proj = create_project(
            name="my_stream", output_width=1920, output_height=1080, fps=30
        )
        assert proj["name"] == "my_stream"

        # Add scenes
        add_scene(proj, name="Starting Soon")
        add_scene(proj, name="BRB")
        add_scene(proj, name="Ending")
        assert len(proj["scenes"]) == 4  # default + 3

        # Add sources to main scene
        cam = add_source(proj, "video_capture", scene_index=0, name="Webcam")
        assert cam["type"] == "video_capture"

        game = add_source(proj, "display_capture", scene_index=0, name="Game Capture")
        assert game["type"] == "display_capture"

        overlay = add_source(
            proj,
            "image",
            scene_index=0,
            name="Overlay",
            settings={"file": "/path/to/overlay.png"},
        )
        assert overlay["settings"]["file"] == "/path/to/overlay.png"

        # Add sources to BRB scene
        brb_img = add_source(proj, "image", scene_index=2, name="BRB Image")
        assert len(proj["scenes"][2]["sources"]) == 1

        # Configure streaming
        set_streaming(proj, service="twitch", server="auto", key="live_abc123")
        assert proj["streaming"]["key"] == "live_abc123"

        # Configure output
        set_output_settings(proj, preset="balanced")
        assert proj["settings"]["video_bitrate"] == 6000

        # Verify final state
        info = get_project_info(proj)
        assert info["counts"]["scenes"] == 4
        assert info["counts"]["total_sources"] == 4

    def test_camera_with_filters(self):
        proj = create_project()
        add_source(proj, "video_capture", name="Camera")

        # Add green screen setup
        add_filter(proj, "chroma_key", 0, params={"similarity": 400})
        add_filter(
            proj, "color_correction", 0, params={"brightness": 0.1, "contrast": 0.2}
        )

        filters = list_filters(proj, 0)
        assert len(filters) == 2
        assert filters[0]["type"] == "chroma_key"
        assert filters[1]["type"] == "color_correction"

    def test_audio_mixer_setup(self):
        proj = create_project()

        # Add audio sources
        mic = add_audio_source(proj, name="Microphone", audio_type="input")
        desktop = add_audio_source(proj, name="Desktop Audio", audio_type="output")

        # Adjust volumes
        set_volume(proj, 0, 1.0)
        set_volume(proj, 1, 0.7)

        # Add monitoring
        set_monitor(proj, 0, "monitor_and_output")

        # Check state
        audio = list_audio(proj)
        assert len(audio) == 2
        assert audio[0]["volume"] == 1.0
        assert audio[1]["volume"] == 0.7
