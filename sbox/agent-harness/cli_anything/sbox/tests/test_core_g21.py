# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCodegenPanelComponent:
    """Tests for codegen.generate_panel_component."""

    def test_panel_component_basic(self):
        result = generate_panel_component("HudPanel")
        assert result["filename"] == "HudPanel.razor"
        assert result["scss_filename"] == "HudPanel.razor.scss"
        assert "@inherits PanelComponent" in result["content"]
        assert "scene_snippet" in result
        # The snippet must be valid JSON describing one GameObject
        snippet = json.loads(result["scene_snippet"])
        assert snippet["Name"] == "HudPanel"

    def test_panel_component_includes_screen_panel(self):
        result = generate_panel_component("Crosshair")
        snippet = json.loads(result["scene_snippet"])
        types = [c["__type"] for c in snippet["Components"]]
        assert "Sandbox.ScreenPanel" in types
        assert "Crosshair" in types  # The PanelComponent type
        assert len(snippet["Components"]) == 2

    def test_panel_component_with_namespace(self):
        result = generate_panel_component("Bar", namespace="MyGame.UI")
        snippet = json.loads(result["scene_snippet"])
        types = [c["__type"] for c in snippet["Components"]]
        assert "MyGame.UI.Bar" in types

    def test_panel_component_with_properties(self):
        result = generate_panel_component(
            "Score",
            properties=[{"name": "Points", "type": "int", "default": "0"}],
        )
        assert "[Property] public int Points" in result["content"]
        assert "BuildHash()" in result["content"]

    def test_panel_component_unique_guids(self):
        result = generate_panel_component("Foo")
        guids = {
            result["screen_panel_guid"],
            result["panel_component_guid"],
            result["object_guid"],
        }
        assert len(guids) == 3
