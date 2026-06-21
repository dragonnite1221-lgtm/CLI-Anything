# ruff: noqa: F403, F405, E501
from .test_exit_codes_helpers import *  # noqa: F403


class TestOneShotFailureExitsNonZero:
    """Failure exits 1 in both human and JSON modes, success exits 0."""

    def test_help_exits_zero(self):
        result = _run(["--help"])
        assert result.returncode == 0

    def test_scene_info_missing_file_exits_one_human_mode(self, tmp_path):
        """Missing file raises FileNotFoundError -> exit 1, error on stderr."""
        result = _run(["scene", "info", str(tmp_path / "missing.scene")])
        assert result.returncode == 1
        assert "Error" in result.stderr

    def test_scene_info_missing_file_exits_one_json_mode(self, tmp_path):
        """JSON mode emits {"error": ...} on stdout AND exits 1."""
        result = _run(["--json", "scene", "info", str(tmp_path / "missing.scene")])
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "error" in data
        assert "missing.scene" in data["error"]

    def test_project_info_outside_project_exits_one(self, tmp_path):
        """Running project info from a directory with no .sbproj exits 1."""
        result = _run(["project", "info"], cwd=str(tmp_path))
        assert result.returncode == 1

    def test_project_info_explicit_missing_path_exits_one(self):
        """--project pointing at a missing path exits 1."""
        result = _run(
            ["--project", "/definitely/nonexistent/sbox/project", "project", "info"]
        )
        assert result.returncode == 1

    def test_localization_get_missing_key_exits_one(self, tmp_path):
        """Querying a missing key emits an error and exits 1."""
        loc_path = tmp_path / "en.json"
        loc_path.write_text(json.dumps({"existing": "value"}), encoding="utf-8")
        result = _run(["localization", "get", str(loc_path), "--key", "missing_key"])
        assert result.returncode == 1

    def test_scene_remove_object_missing_args_exits_one(self, tmp_path):
        """remove-object with no --name or --guid raises ClickException -> exit 1."""
        scene_path = tmp_path / "stub.scene"
        scene_path.write_text(json.dumps({"GameObjects": []}), encoding="utf-8")
        result = _run(["scene", "remove-object", str(scene_path)])
        assert result.returncode == 1

    def test_codegen_invalid_json_properties_exits_one(self):
        """Invalid JSON in --properties triggers JSONDecodeError -> exit 1."""
        result = _run(
            [
                "codegen",
                "component",
                "--name",
                "Bad",
                "--properties",
                "not-json",
            ]
        )
        assert result.returncode == 1

    def test_asset_compile_missing_sbox_exits_one(self, tmp_path):
        """asset compile with no s&box install (or missing file) exits 1.

        Either find_executable raises (no install) or the missing file path
        triggers FileNotFoundError. Both paths must exit 1.
        """
        result = _run(["asset", "compile", str(tmp_path / "nope.vmat")])
        assert result.returncode == 1

    def test_scene_list_missing_file_exits_one(self, tmp_path):
        """scene list on a missing file: bare except Exception path.

        Direct gate of the _output_error sys.exit fix - this handler does
        ``except Exception as exc: _output_error(ctx, str(exc))`` with no
        ClickException re-raise short-circuit, so without the fix the
        FileNotFoundError would print and exit 0.
        """
        result = _run(["scene", "list", str(tmp_path / "missing.scene")])
        assert result.returncode == 1

    def test_asset_info_corrupt_json_exits_one(self, tmp_path):
        """asset info on a corrupt .scene surfaces _parse_json_asset's error
        and exits 1, instead of burying the error in nested json_info."""
        bad_scene = tmp_path / "broken.scene"
        bad_scene.write_text("{not valid json", encoding="utf-8")
        result = _run(["asset", "info", str(bad_scene)])
        assert result.returncode == 1


class TestOneShotSuccessExitsZero:
    """Successful one-shot commands still exit 0 after the fix."""

    def test_project_new_exits_zero(self, tmp_path):
        result = _run(
            [
                "--json",
                "project",
                "new",
                "--name",
                "exit_test",
                "--output-dir",
                str(tmp_path),
            ]
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "exit_test"

    def test_project_info_on_valid_project_exits_zero(self, tmp_path):
        _run(
            [
                "--json",
                "project",
                "new",
                "--name",
                "info_test",
                "--output-dir",
                str(tmp_path),
            ]
        )
        result = _run(
            [
                "--json",
                "--project",
                str(tmp_path),
                "project",
                "info",
            ]
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["title"] == "info_test"
