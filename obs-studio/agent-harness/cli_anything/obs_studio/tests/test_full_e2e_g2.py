# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestFilterChains:
    """Test filter chain workflows."""

    def test_audio_filter_chain(self):
        proj = create_project()
        add_source(proj, "audio_input", name="Mic")

        add_filter(proj, "noise_suppress", 0, params={"method": "rnnoise"})
        add_filter(proj, "noise_gate", 0, params={"open_threshold": -26.0})
        add_filter(proj, "compressor", 0, params={"ratio": 10.0, "threshold": -18.0})
        add_filter(proj, "gain", 0, params={"db": 3.0})
        add_filter(proj, "limiter", 0, params={"threshold": -3.0})

        filters = list_filters(proj, 0)
        assert len(filters) == 5
        assert filters[0]["type"] == "noise_suppress"
        assert filters[4]["type"] == "limiter"

    def test_video_filter_chain(self):
        proj = create_project()
        add_source(proj, "video_capture", name="Camera")

        add_filter(proj, "chroma_key", 0, params={"key_color_type": "green"})
        add_filter(proj, "color_correction", 0, params={"saturation": 1.5})
        add_filter(proj, "sharpen", 0, params={"sharpness": 0.1})

        filters = list_filters(proj, 0)
        assert len(filters) == 3

    def test_modify_filter_in_chain(self):
        proj = create_project()
        add_source(proj, "video_capture", name="Camera")
        add_filter(proj, "color_correction", 0, params={"brightness": 0.0})

        set_filter_param(proj, 0, "brightness", 0.3, 0)
        assert (
            proj["scenes"][0]["sources"][0]["filters"][0]["params"]["brightness"] == 0.3
        )

    def test_remove_filter_from_chain(self):
        proj = create_project()
        add_source(proj, "audio_input", name="Mic")
        add_filter(proj, "gain", 0)
        add_filter(proj, "compressor", 0)
        add_filter(proj, "limiter", 0)

        remove_filter(proj, 1, 0)  # remove compressor
        filters = list_filters(proj, 0)
        assert len(filters) == 2
        assert filters[0]["type"] == "gain"
        assert filters[1]["type"] == "limiter"


class TestTransitionWorkflow:
    """Test transition workflows."""

    def test_transition_setup(self):
        proj = create_project()

        add_transition(proj, "stinger", name="My Stinger", duration=1500)
        add_transition(proj, "slide", duration=700)

        transitions = list_transitions(proj)
        assert len(transitions) == 4  # 2 default + 2 added

    def test_transition_duration_change(self):
        proj = create_project()
        set_duration(proj, 1, 500)  # Change Fade duration
        assert proj["transitions"][1]["duration"] == 500


class TestOutputConfiguration:
    """Test output configuration workflows."""

    def test_full_output_config(self):
        proj = create_project()

        # Configure streaming
        set_streaming(proj, service="youtube", server="auto", key="stream_key_here")

        # Configure recording
        set_recording(proj, path="/recordings/", fmt="mp4", quality="high")

        # Configure encoding
        set_output_settings(
            proj, output_width=1920, output_height=1080, fps=60, video_bitrate=8000
        )

        info = get_output_info(proj)
        assert info["streaming"]["service"] == "youtube"
        assert info["recording"]["format"] == "mp4"
        assert info["settings"]["fps"] == 60

    def test_preset_then_override(self):
        proj = create_project()
        set_output_settings(proj, preset="quality")
        assert proj["settings"]["video_bitrate"] == 8000

        # Override single setting
        set_output_settings(proj, video_bitrate=10000)
        assert proj["settings"]["video_bitrate"] == 10000
        # Encoder should still be from preset
        assert proj["settings"]["encoder"] == "x264"
