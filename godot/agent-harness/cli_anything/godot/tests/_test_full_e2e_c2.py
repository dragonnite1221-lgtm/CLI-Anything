# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import _invoke_json  # noqa: F401,E501


class _TestE2EDemoGamePipelineMixin2:
    def test_10_list_project_assets(self):
        """After creating scenes and scripts, verify asset listing commands."""
        _invoke_json(
            self.runner,
            ["project", "create", str(self.project_dir), "--name", "Demo Platformer"],
        )

        # Create two scenes
        self._pj(["scene", "create", "scenes/Main.tscn", "--root-type", "Node2D"])
        self._pj(["scene", "create", "scenes/Player.tscn", "--root-type", "CharacterBody2D"])

        # Write a script
        scripts_dir = self.project_dir / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        (scripts_dir / "player.gd").write_text(
            "extends CharacterBody2D\n", encoding="utf-8",
        )

        # Write a resource file
        (self.project_dir / "icon.tres").write_text(
            '[gd_resource type="CompressedTexture2D"]\n', encoding="utf-8",
        )

        # Verify scene listing
        data = self._pj(["project", "scenes"])
        scene_paths = [s if isinstance(s, str) else s.get("path", "") for s in data["scenes"]]
        assert len(scene_paths) >= 2

        # Verify script listing
        data = self._pj(["project", "scripts"])
        assert data["count"] >= 1

        # Verify resource listing
        data = self._pj(["project", "resources"])
        assert data["count"] >= 1
    def test_11_export_presets_empty(self):
        """A fresh project has no export presets."""
        _invoke_json(
            self.runner,
            ["project", "create", str(self.project_dir), "--name", "Demo Platformer"],
        )
        data = self._pj(["export", "presets"])
        assert data["status"] == "ok"
        assert data["count"] == 0
    def test_12_export_presets_parsed(self):
        """Write an export_presets.cfg and verify it gets parsed correctly."""
        _invoke_json(
            self.runner,
            ["project", "create", str(self.project_dir), "--name", "Demo Platformer"],
        )
        (self.project_dir / "export_presets.cfg").write_text(textwrap.dedent("""\
            [preset.0]
            name="Windows Desktop"
            platform="Windows Desktop"
            export_path="build/game.exe"

            [preset.0.options]

            [preset.1]
            name="Linux/X11"
            platform="Linux/X11"
            export_path="build/game.x86_64"

            [preset.1.options]
        """), encoding="utf-8")

        data = self._pj(["export", "presets"])
        assert data["status"] == "ok"
        assert data["count"] == 2
        preset_names = {p["name"] for p in data["presets"]}
        assert preset_names == {"Windows Desktop", "Linux/X11"}
        preset_platforms = {p["platform"] for p in data["presets"]}
        assert preset_platforms == {"Windows Desktop", "Linux/X11"}
    def test_13_export_build_without_presets_fails(self):
        """Export build on a project without presets should return an error."""
        _invoke_json(
            self.runner,
            ["project", "create", str(self.project_dir), "--name", "Demo Platformer"],
        )
        result = self.runner.invoke(cli, [
            "--json", "-p", str(self.project_dir), "export", "build",
        ])
        data = json.loads(result.output)
        assert data["status"] == "error"
        assert "export_presets.cfg" in data["message"]
