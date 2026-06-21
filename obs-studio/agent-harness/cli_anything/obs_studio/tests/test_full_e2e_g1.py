# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestSourceManipulation:
    """Test source manipulation workflows."""

    def test_source_layering(self):
        proj = create_project()

        # Create layered scene
        add_source(proj, "display_capture", name="Game")
        add_source(proj, "image", name="Frame Overlay", position={"x": 0, "y": 0})
        add_source(
            proj,
            "video_capture",
            name="Webcam",
            position={"x": 1500, "y": 800},
            size={"width": 400, "height": 300},
        )
        add_source(
            proj,
            "text",
            name="Now Playing",
            position={"x": 10, "y": 10},
            settings={"text": "Currently streaming!"},
        )

        sources = list_sources(proj)
        assert len(sources) == 4
        assert sources[2]["position"]["x"] == 1500

    def test_source_transform_workflow(self):
        proj = create_project()
        add_source(proj, "video_capture", name="Camera")

        # Position and resize
        transform_source(
            proj, 0, position={"x": 100, "y": 100}, size={"width": 640, "height": 480}
        )

        # Crop
        transform_source(proj, 0, crop={"top": 50, "bottom": 50, "left": 0, "right": 0})

        # Rotate
        transform_source(proj, 0, rotation=15.0)

        src = proj["scenes"][0]["sources"][0]
        assert src["position"]["x"] == 100
        assert src["size"]["width"] == 640
        assert src["crop"]["top"] == 50
        assert src["rotation"] == 15.0

    def test_duplicate_and_modify_source(self):
        proj = create_project()
        add_source(proj, "text", name="Alert", settings={"text": "New follower!"})
        dup = duplicate_source(proj, 0)

        # Modify the duplicate
        set_source_property(proj, 1, "visible", "false")

        assert proj["scenes"][0]["sources"][0]["visible"] is True
        assert proj["scenes"][0]["sources"][1]["visible"] is False

    def test_source_visibility_toggle(self):
        proj = create_project()
        add_source(proj, "image", name="Logo")

        set_source_property(proj, 0, "visible", "false")
        assert proj["scenes"][0]["sources"][0]["visible"] is False

        set_source_property(proj, 0, "visible", "true")
        assert proj["scenes"][0]["sources"][0]["visible"] is True


class TestSceneWorkflow:
    """Test scene management workflows."""

    def test_multi_scene_setup(self):
        proj = create_project()

        # Set up multiple scenes
        add_scene(proj, name="Gaming")
        add_scene(proj, name="Just Chatting")
        add_scene(proj, name="BRB")

        # Add sources to different scenes
        add_source(proj, "display_capture", scene_index=0, name="Desktop")
        add_source(proj, "video_capture", scene_index=1, name="Camera")
        add_source(proj, "image", scene_index=2, name="Chatting BG")
        add_source(proj, "video_capture", scene_index=2, name="Cam2")
        add_source(proj, "image", scene_index=3, name="BRB Screen")

        scenes = list_scenes(proj)
        assert len(scenes) == 4
        assert scenes[0]["source_count"] == 1
        assert scenes[2]["source_count"] == 2

    def test_scene_switching(self):
        proj = create_project()
        add_scene(proj, name="BRB")

        assert proj["active_scene"] == 0
        set_active_scene(proj, 1)
        assert proj["active_scene"] == 1

    def test_duplicate_scene_with_sources(self):
        proj = create_project()
        add_source(proj, "image", scene_index=0, name="BG")
        add_source(proj, "text", scene_index=0, name="Title")

        dup = duplicate_scene(proj, 0)
        assert len(dup["sources"]) == 2
        # Sources should be independent copies
        dup["sources"][0]["name"] = "Modified"
        assert proj["scenes"][0]["sources"][0]["name"] == "BG"

    def test_remove_scene_keeps_others(self):
        proj = create_project()
        add_scene(proj, name="A")
        add_scene(proj, name="B")
        assert len(proj["scenes"]) == 3

        remove_scene(proj, 1)
        assert len(proj["scenes"]) == 2
        assert proj["scenes"][1]["name"] == "B"
