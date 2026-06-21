# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestExportPresets:
    def test_no_presets_file(self, runner, tmp_project):
        result = runner.invoke(
            cli, ["--json", "-p", str(tmp_project), "export", "presets"]
        )
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert data["count"] == 0

    def test_parse_presets(self, runner, tmp_project):
        presets_file = tmp_project / "export_presets.cfg"
        presets_file.write_text(
            "[preset.0]\n\n"
            'name="Windows Desktop"\n'
            'platform="Windows Desktop"\n'
            'export_path="build/game.exe"\n\n'
            "[preset.1]\n\n"
            'name="Linux"\n'
            'platform="Linux/X11"\n'
            'export_path="build/game.x86_64"\n',
            encoding="utf-8",
        )
        result = runner.invoke(
            cli, ["--json", "-p", str(tmp_project), "export", "presets"]
        )
        data = json.loads(result.output)
        assert data["count"] == 2
        assert data["presets"][0]["name"] == "Windows Desktop"
        assert data["presets"][1]["platform"] == "Linux/X11"


class TestEngineStatus:
    def test_engine_status_no_godot(self, runner):
        with mock.patch(
            "cli_anything.godot.utils.godot_backend.find_godot_binary",
            return_value=None,
        ):
            result = runner.invoke(cli, ["--json", "engine", "status"])
            data = json.loads(result.output)
            assert data["available"] is False

    def test_engine_status_found(self, runner):
        with mock.patch(
            "cli_anything.godot.godot_cli.find_godot_binary",
            return_value="/usr/bin/godot",
        ):
            with mock.patch(
                "cli_anything.godot.godot_cli.is_available",
                return_value=True,
            ):
                result = runner.invoke(cli, ["--json", "engine", "status"])
                data = json.loads(result.output)
                assert data["available"] is True
                assert data["binary"] == "/usr/bin/godot"


class TestBackend:
    def test_validate_project(self, tmp_project):
        from cli_anything.godot.utils.godot_backend import validate_project

        assert validate_project(str(tmp_project)) is True

    def test_validate_non_project(self, tmp_path):
        from cli_anything.godot.utils.godot_backend import validate_project

        assert validate_project(str(tmp_path)) is False

    def test_find_godot_binary_env(self):
        from cli_anything.godot.utils.godot_backend import find_godot_binary

        with mock.patch.dict(os.environ, {"GODOT_BIN": "python"}):
            # python is guaranteed to be on PATH
            result = find_godot_binary()
            assert result is not None


class TestCLIRoot:
    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "cli-anything-godot" in result.output

    def test_no_args_shows_help(self, runner):
        result = runner.invoke(cli, [])
        assert "cli-anything-godot" in result.output

    def test_json_flag(self, runner, tmp_project):
        result = runner.invoke(
            cli, ["--json", "-p", str(tmp_project), "project", "info"]
        )
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_human_output(self, runner, tmp_project):
        result = runner.invoke(cli, ["-p", str(tmp_project), "project", "info"])
        assert "TestGame" in result.output
