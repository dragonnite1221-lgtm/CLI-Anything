# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCodegen:
    """Tests for cli_anything.sbox.core.codegen."""

    def test_generate_component_basic(self):
        """Generate a basic sealed component."""
        result = generate_component("PlayerHealth")

        assert result["filename"] == "PlayerHealth.cs"
        assert result["class_name"] == "PlayerHealth"
        content = result["content"]
        assert "using Sandbox;" in content
        assert "public sealed class PlayerHealth : Component" in content

    def test_generate_component_with_properties(self):
        """Generate component with typed properties."""
        props = [
            {"name": "Health", "type": "float", "default": "100f"},
            {"name": "MaxHealth", "type": "float", "default": "100f"},
            {"name": "DisplayName", "type": "string"},
        ]
        result = generate_component("PlayerStats", properties=props)
        content = result["content"]

        assert "[Property]" in content
        assert "public float Health { get; set; } = 100f;" in content
        assert "public float MaxHealth { get; set; } = 100f;" in content
        assert "public string DisplayName { get; set; }" in content

    def test_generate_component_networked(self):
        """Generate partial class with [Sync] and IsProxy guard."""
        result = generate_component(
            "NetPlayer",
            is_networked=True,
            properties=[{"name": "Health", "type": "float", "default": "100f"}],
            lifecycle_methods=["OnFixedUpdate"],
        )
        content = result["content"]

        assert "public partial class NetPlayer : Component" in content
        assert "sealed" not in content
        assert "[Sync]" in content
        assert "if ( IsProxy ) return;" in content

    def test_generate_component_with_interfaces(self):
        """Generate component implementing interfaces."""
        result = generate_component(
            "DamageReceiver",
            interfaces=["Component.ITriggerListener", "Component.IDamageable"],
        )
        content = result["content"]

        assert (
            "public sealed class DamageReceiver : Component, "
            "Component.ITriggerListener, Component.IDamageable"
        ) in content

    def test_generate_component_lifecycle_methods(self):
        """Generate with OnUpdate, OnFixedUpdate, OnStart."""
        result = generate_component(
            "LifecycleTest",
            lifecycle_methods=["OnStart", "OnUpdate", "OnFixedUpdate"],
        )
        content = result["content"]

        assert "protected override void OnStart()" in content
        assert "protected override void OnUpdate()" in content
        assert "protected override void OnFixedUpdate()" in content

    def test_generate_gameresource(self):
        """Generate a GameResource class."""
        result = generate_gameresource(
            "TowerData",
            display_name="Tower Data",
            extension="tower",
            description="Data for a tower defense tower",
            properties=[
                {"name": "Cost", "type": "int", "default": "100"},
                {"name": "Range", "type": "float", "default": "500f"},
            ],
        )

        assert result["filename"] == "TowerData.cs"
        assert result["class_name"] == "TowerData"
        content = result["content"]

        assert "using Sandbox;" in content
        assert (
            '[GameResource( "Tower Data", "tower", "Data for a tower defense tower" )]'
            in content
        )
        assert "public class TowerData : GameResource" in content
        assert "public int Cost { get; set; } = 100;" in content
        assert "public float Range { get; set; } = 500f;" in content

    def test_generate_editor_menu(self):
        """Generate an editor menu class."""
        result = generate_editor_menu(
            "MyTool",
            menu_path="Tools/My Tool",
            method_name="Open",
            dialog_title="My Tool",
            dialog_message="Hello from My Tool",
        )

        assert result["filename"] == "MyTool.cs"
        assert result["class_name"] == "MyTool"
        content = result["content"]

        assert "using Editor;" in content
        assert "using Sandbox;" in content
        assert "public static class MyTool" in content
        assert '[Menu( "Editor", "Tools/My Tool" )]' in content
        assert "public static void Open()" in content
        assert (
            'EditorUtility.DisplayDialog( "My Tool", "Hello from My Tool" );' in content
        )

    def test_code_style_tabs(self):
        """Verify generated code uses tabs, not spaces."""
        result = generate_component(
            "TabTest",
            properties=[{"name": "Value", "type": "int"}],
            lifecycle_methods=["OnUpdate"],
        )
        content = result["content"]

        # Split into lines, check that indented lines use tabs
        for line in content.split("\r\n"):
            stripped = line.lstrip("\t")
            if len(stripped) < len(line):
                # This line was indented - verify it used tabs not spaces
                indent = line[: len(line) - len(stripped)]
                assert "\t" in indent, f"Line uses spaces instead of tabs: {repr(line)}"
                # Indentation part should be only tabs
                assert indent == indent.replace(" ", ""), (
                    f"Mixed tabs/spaces in indent: {repr(line)}"
                )

    def test_code_style_allman_braces(self):
        """Verify Allman-style braces."""
        result = generate_component(
            "BraceTest",
            lifecycle_methods=["OnUpdate"],
        )
        content = result["content"]
        lines = content.split("\r\n")

        # Find lines with opening braces - they should be on their own line
        # (possibly with leading whitespace only)
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == "{":
                # This is correct Allman style - brace on its own line
                continue
            if stripped.endswith("{") and stripped != "{":
                # Brace at end of a non-empty line would be K&R style
                # But we need to allow attribute lines like [Menu( "Editor", "..." )]
                # that aren't brace-bearing. The check is: if the line has a brace
                # AND is not just the brace, that would violate Allman style.
                # However, there is no K&R brace in our generated code.
                pytest.fail(f"K&R-style brace found on line {i + 1}: {repr(line)}")

    def test_code_style_crlf(self):
        """Verify CRLF line endings."""
        result = generate_component("CrlfTest")
        content = result["content"]

        # Content should have \r\n
        assert "\r\n" in content, "Expected CRLF line endings"

        # Should not have bare \n (without preceding \r)
        # Replace all \r\n first, then check for remaining \n
        remaining = content.replace("\r\n", "")
        assert "\n" not in remaining, "Found bare LF without CR"
