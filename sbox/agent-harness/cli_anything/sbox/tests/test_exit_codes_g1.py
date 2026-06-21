# ruff: noqa: F403, F405, E501
from .test_exit_codes_helpers import *  # noqa: F403


class TestProjectValidateExitsNonZero:
    """project validate must exit 1 when ok=False so CI can gate on it."""

    def test_validate_clean_project_exits_zero(self, tmp_path):
        _run(
            [
                "--json",
                "project",
                "new",
                "--name",
                "clean",
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
                "validate",
            ]
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["ok"] is True

    def test_validate_broken_ref_exits_one(self, tmp_path):
        """A scene that references a missing prefab makes ok=False -> exit 1."""
        _run(
            [
                "--json",
                "project",
                "new",
                "--name",
                "brokenproj",
                "--output-dir",
                str(tmp_path),
            ]
        )
        scene_path = tmp_path / "Assets" / "scenes" / "minimal.scene"
        scene_data = json.loads(scene_path.read_text(encoding="utf-8"))
        scene_data["GameObjects"].append(
            {
                "__guid": "11111111-1111-1111-1111-111111111111",
                "Name": "BrokenRef",
                "Position": "0,0,0",
                "Tags": "",
                "Components": [
                    {
                        "__guid": "22222222-2222-2222-2222-222222222222",
                        "__type": "Sandbox.PrefabScene",
                        "PrefabSource": "missing/prefab/path.prefab",
                    }
                ],
            }
        )
        scene_path.write_text(json.dumps(scene_data), encoding="utf-8")

        result = _run(
            [
                "--json",
                "--project",
                str(tmp_path),
                "project",
                "validate",
            ]
        )
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["ok"] is False
        assert data["issue_count"] >= 1


class TestAuditedFailurePaths:
    """Coverage for failure paths added during the silent-failure audit.

    These paths return dicts (not exceptions) on failure, so the standard
    ``except Exception`` path doesn't catch them. The audit added explicit
    success/error checks to surface them; these tests pin those checks.
    """

    def test_asset_compile_returns_success_false_exits_one(self, monkeypatch):
        """asset compile sees ``success=False`` from run_resource_compiler
        and exits 1 with the compiler's stderr in the error message."""
        from click.testing import CliRunner
        from cli_anything.sbox import sbox_cli
        from cli_anything.sbox.utils import sbox_backend

        def fake_compile(asset_path):
            return {
                "success": False,
                "return_code": 1,
                "stdout": "",
                "stderr": "mock compiler error: bad shader",
                "asset_path": asset_path,
                "compiler_path": "/fake/resourcecompiler",
            }

        monkeypatch.setattr(sbox_backend, "run_resource_compiler", fake_compile)

        runner = CliRunner()
        result = runner.invoke(sbox_cli.cli, ["asset", "compile", "/fake/path.vmat"])

        assert result.exit_code == 1
        # The error message includes both rc and stderr context.
        assert "Resource compilation failed" in result.output
        assert "mock compiler error" in result.output

    def test_server_info_version_error_exits_one(self, monkeypatch):
        """server info sees ``error`` field in get_sbox_version() and exits 1
        instead of reporting "version: unknown" with exit 0."""
        from click.testing import CliRunner
        from cli_anything.sbox import sbox_cli
        from cli_anything.sbox.utils import sbox_backend

        monkeypatch.setattr(
            sbox_backend, "find_executable", lambda name: "/fake/sbox-server.exe"
        )
        monkeypatch.setattr(
            sbox_backend,
            "get_sbox_version",
            lambda: {
                "version": "unknown",
                "error": "mock: .version file unreadable",
            },
        )

        runner = CliRunner()
        result = runner.invoke(sbox_cli.cli, ["server", "info"])

        assert result.exit_code == 1
        assert "Failed to read s&box version" in result.output
