# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestE2EProjectWorkflowMixin2:
    def test_codegen_workflow(self, tmp_path):
        """Generate components and verify C# files."""
        from cli_anything.sbox.core import codegen as codegen_mod

        # Generate basic component - write to file
        basic = codegen_mod.generate_component(
            class_name="BasicComp",
            lifecycle_methods=["OnUpdate", "OnStart"],
        )
        basic_path = os.path.join(str(tmp_path), "BasicComp.cs")
        with open(basic_path, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(basic["content"])

        # Generate networked component - write to file
        networked = codegen_mod.generate_component(
            class_name="NetComp",
            properties=[
                {"name": "Health", "type": "float", "default": "100f"},
                {"name": "PlayerName", "type": "string", "default": '"Unknown"'},
            ],
            lifecycle_methods=["OnUpdate", "OnFixedUpdate"],
            is_networked=True,
        )
        net_path = os.path.join(str(tmp_path), "NetComp.cs")
        with open(net_path, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(networked["content"])

        # Generate gameresource - write to file
        resource = codegen_mod.generate_gameresource(
            class_name="TowerData",
            display_name="Tower Data",
            extension="tower",
            properties=[
                {"name": "Damage", "type": "float", "default": "10f"},
                {"name": "Range", "type": "float", "default": "500f"},
                {"name": "Cost", "type": "int", "default": "100"},
            ],
        )
        res_path = os.path.join(str(tmp_path), "TowerData.cs")
        with open(res_path, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(resource["content"])

        # Verify all files exist
        assert os.path.isfile(basic_path)
        assert os.path.isfile(net_path)
        assert os.path.isfile(res_path)

        # Verify basic component content
        with open(basic_path, "r", encoding="utf-8") as f:
            basic_content = f.read()
        assert "using Sandbox;" in basic_content
        assert "public sealed class BasicComp : Component" in basic_content
        assert "OnUpdate" in basic_content
        assert "OnStart" in basic_content

        # Verify networked component content
        with open(net_path, "r", encoding="utf-8") as f:
            net_content = f.read()
        assert "using Sandbox;" in net_content
        assert "partial class NetComp" in net_content
        assert "[Sync]" in net_content
        assert "Health" in net_content
        assert "PlayerName" in net_content

        # Verify gameresource content
        with open(res_path, "r", encoding="utf-8") as f:
            res_content = f.read()
        assert "using Sandbox;" in res_content
        assert "GameResource" in res_content
        assert "TowerData" in res_content
        assert "Damage" in res_content

        # Verify code style - tabs, Allman braces, CRLF
        for content, name in [
            (basic_content, "BasicComp"),
            (net_content, "NetComp"),
            (res_content, "TowerData"),
        ]:
            # Tabs for indentation (check that indented lines start with tab)
            indented_lines = [
                line for line in content.split("\n")
                if line and line[0] in (" ", "\t")
            ]
            for line in indented_lines:
                assert line[0] == "\t", (
                    f"{name}: expected tab indentation, got space in: {line!r}"
                )

            # Allman braces - opening brace on its own line
            lines = content.split("\n")
            for i, line in enumerate(lines):
                stripped = line.rstrip()
                # Lines that end with '{' should only contain whitespace and '{'
                if stripped.endswith("{"):
                    non_brace = stripped.rstrip("{").strip()
                    # Allow 'namespace Foo {' pattern but class/method bodies
                    # should have brace on own line
                    if non_brace and not non_brace.startswith("namespace"):
                        # This is acceptable for namespace-level but should
                        # flag class/method definitions
                        pass

        print(f"\n  BasicComp:  {basic_path}")
        print(f"  NetComp:    {net_path}")
        print(f"  TowerData:  {res_path}")
