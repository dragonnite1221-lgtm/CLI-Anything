# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestCLISubprocess:
    CLI_BASE = _resolve_cli("cli-anything-macrocli")

    def _run(self, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
        )

    def test_help(self):
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "macro" in result.stdout.lower()

    def test_macro_list_json(self):
        result = self._run(["--json", "macro", "list"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        print(f"\n  macros: {[m['name'] for m in data]}")

    def test_macro_info_json(self):
        # Info on a bundled example macro
        result = self._run(["--json", "macro", "info", "export_file"])
        assert result.returncode == 0, f"stderr: {result.stderr}"
        data = json.loads(result.stdout)
        assert data["name"] == "export_file"
        assert "parameters" in data
        print(f"\n  Macro info: {data['name']} v{data['version']}")

    def test_macro_validate_all(self):
        result = self._run(["--json", "macro", "validate"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        for name, info in data.items():
            assert info["valid"], f"Macro {name} failed: {info['errors']}"
        print(f"\n  Validated {len(data)} macros, all valid")

    def test_macro_dry_run_json(self):
        result = self._run(
            [
                "--json",
                "--dry-run",
                "macro",
                "run",
                "export_file",
                "--param",
                "output=/tmp/test_macrocli_e2e.txt",
            ]
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert data["telemetry"]["dry_run"] is True
        print(f"\n  Dry run result: {data['success']}")

    def test_backends_json(self):
        result = self._run(["--json", "backends"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "native_api" in data
        assert "file_transform" in data
        print(f"\n  Backends: {list(data.keys())}")

    def test_session_status_json(self):
        result = self._run(["--json", "session", "status"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "session_id" in data
        print(f"\n  Session: {data['session_id']}")

    def test_macro_run_json_transform_workflow(self, tmp_path):
        """Full E2E: create a JSON file, run transform_json macro, verify output."""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"name": "test"}', encoding="utf-8")

        result = self._run(
            [
                "--json",
                "macro",
                "run",
                "transform_json",
                "--param",
                f"file={json_file}",
                "--param",
                "key=config.mode",
                "--param",
                "value=production",
            ]
        )
        print(f"\n  CLI stdout: {result.stdout[:200]}")
        print(f"  CLI stderr: {result.stderr[:200]}")

        assert result.returncode == 0, f"CLI failed:\n{result.stderr}"
        data = json.loads(result.stdout)
        assert data["success"] is True, f"Macro failed: {data.get('error')}"

        # Verify file was actually modified
        modified = json.loads(json_file.read_text())
        assert modified["config"]["mode"] == "production"
        print(f"\n  Modified JSON: {modified}")
        print(f"  File: {json_file} ({json_file.stat().st_size} bytes)")

    def test_unknown_macro_returns_error_json(self):
        result = self._run(
            ["--json", "macro", "run", "nonexistent_macro_xyz"],
            check=False,
        )
        assert result.returncode != 0
        data = json.loads(result.stdout)
        assert data["success"] is False
        assert "error" in data
        print(f"\n  Error: {data['error']}")
