# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCodegenRazor:
    """Tests for Razor UI generation and RPC support."""

    def test_generate_razor_basic(self):
        result = generate_razor("HudPanel")
        assert result["filename"] == "HudPanel.razor"
        assert result["scss_filename"] == "HudPanel.razor.scss"
        assert "@using Sandbox;" in result["content"]
        assert "@using Sandbox.UI;" in result["content"]
        assert "@inherits PanelComponent" in result["content"]
        assert 'class="hud-panel"' in result["content"]

    def test_generate_razor_with_properties(self):
        result = generate_razor(
            "ScoreBoard",
            properties=[
                {"name": "Score", "type": "int", "default": "0"},
                {"name": "PlayerName", "type": "string"},
            ],
        )
        assert "[Property] public int Score" in result["content"]
        assert "[Property] public string PlayerName" in result["content"]
        assert "BuildHash" in result["content"]
        assert "System.HashCode.Combine" in result["content"]

    def test_generate_razor_scss(self):
        result = generate_razor("MyWidget", root_class="custom-widget")
        assert ".custom-widget" in result["scss_content"]
        assert "flex-direction: column;" in result["scss_content"]

    def test_generate_component_with_rpc(self):
        result = generate_component(
            "NetPlayer",
            rpc_methods=[
                {"name": "FireBullet", "type": "Broadcast"},
                {"name": "TakeDamage", "type": "Host"},
            ],
        )
        content = result["content"]
        assert "public partial class NetPlayer" in content
        assert "[Rpc.Broadcast]" in content
        assert "[Rpc.Host]" in content
        assert "public void FireBullet()" in content
        assert "public void TakeDamage()" in content

    def test_generate_component_net_collections(self):
        result = generate_component(
            "Inventory",
            is_networked=True,
            properties=[
                {"name": "Items", "type": "NetList<string>"},
                {"name": "Score", "type": "int", "default": "0"},
            ],
        )
        content = result["content"]
        # NetList should NOT have [Sync]
        # Score should have [Sync]
        lines = content.split("\r\n")
        for i, line in enumerate(lines):
            if "NetList<string>" in line:
                # Check previous lines don't have [Sync]
                prev = lines[max(0, i - 1)].strip() if i > 0 else ""
                prev2 = lines[max(0, i - 2)].strip() if i > 1 else ""
                assert "[Sync]" not in prev, "NetList should not have [Sync]"
                assert "[Sync]" not in prev2, "NetList should not have [Sync]"
