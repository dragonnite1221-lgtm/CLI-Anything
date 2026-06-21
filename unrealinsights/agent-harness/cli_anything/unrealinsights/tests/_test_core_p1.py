# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import _make_fake_binary  # noqa: F401,E501


class TestBackendDiscovery:
    @patch("cli_anything.unrealinsights.utils.unrealinsights_backend._read_windows_product_version", return_value="5.5.4")
    def test_explicit_path_precedence(self, _mock_version, tmp_path, monkeypatch):
        from cli_anything.unrealinsights.utils.unrealinsights_backend import resolve_unrealinsights_exe

        explicit = tmp_path / "explicit" / "UnrealInsights.exe"
        explicit.parent.mkdir(parents=True)
        explicit.write_text("x", encoding="utf-8")

        env_binary = tmp_path / "env" / "UnrealInsights.exe"
        env_binary.parent.mkdir(parents=True)
        env_binary.write_text("x", encoding="utf-8")
        monkeypatch.setenv("UNREALINSIGHTS_EXE", str(env_binary))

        auto_root = tmp_path / "Epic Games"
        _make_fake_binary(auto_root, "UnrealInsights.exe")

        result = resolve_unrealinsights_exe(str(explicit), search_roots=[auto_root])
        assert result["source"] == "explicit"
        assert result["path"] == str(explicit.resolve())

    @patch("cli_anything.unrealinsights.utils.unrealinsights_backend._read_windows_product_version", return_value="5.5.4")
    def test_env_path_precedence(self, _mock_version, tmp_path, monkeypatch):
        from cli_anything.unrealinsights.utils.unrealinsights_backend import resolve_unrealinsights_exe

        env_binary = tmp_path / "env" / "UnrealInsights.exe"
        env_binary.parent.mkdir(parents=True)
        env_binary.write_text("x", encoding="utf-8")
        monkeypatch.setenv("UNREALINSIGHTS_EXE", str(env_binary))

        auto_root = tmp_path / "Epic Games"
        _make_fake_binary(auto_root, "UnrealInsights.exe")

        result = resolve_unrealinsights_exe(search_roots=[auto_root])
        assert result["source"] == "env:UNREALINSIGHTS_EXE"
        assert result["path"] == str(env_binary.resolve())

    @patch("cli_anything.unrealinsights.utils.unrealinsights_backend._read_windows_product_version", return_value="5.5.4")
    def test_auto_discovery(self, _mock_version, tmp_path, monkeypatch):
        from cli_anything.unrealinsights.utils.unrealinsights_backend import resolve_unrealinsights_exe

        monkeypatch.delenv("UNREALINSIGHTS_EXE", raising=False)
        auto_root = tmp_path / "Epic Games"
        auto_binary = _make_fake_binary(auto_root, "UnrealInsights.exe")

        result = resolve_unrealinsights_exe(search_roots=[auto_root])
        assert result["source"].startswith("auto:")
        assert result["path"] == str(auto_binary.resolve())

    def test_missing_explicit_path_fails(self, tmp_path):
        from cli_anything.unrealinsights.utils.unrealinsights_backend import resolve_unrealinsights_exe

        with pytest.raises(RuntimeError):
            resolve_unrealinsights_exe(str(tmp_path / "missing.exe"))

    def test_build_insights_command(self, tmp_path):
        from cli_anything.unrealinsights.utils.unrealinsights_backend import build_insights_command

        command = build_insights_command(
            str(tmp_path / "UnrealInsights.exe"),
            str(tmp_path / "trace.utrace"),
            'TimingInsights.ExportThreads "D:\\out\\threads.csv"',
            str(tmp_path / "threads.log"),
        )
        assert any(part.startswith("-OpenTraceFile=") for part in command)
        assert any(part.startswith("-ExecOnAnalysisCompleteCmd=") for part in command)

    def test_build_insights_command_line(self, tmp_path):
        from cli_anything.unrealinsights.utils.unrealinsights_backend import build_insights_command_line

        command = build_insights_command_line(
            str(tmp_path / "UnrealInsights.exe"),
            str(tmp_path / "trace.utrace"),
            'TimingInsights.ExportThreads D:\\out\\threads.csv',
            str(tmp_path / "threads.log"),
        )
        assert "-ExecOnAnalysisCompleteCmd=" in command
        assert command.startswith('"')

    @patch("cli_anything.unrealinsights.utils.unrealinsights_backend._read_windows_product_version", return_value="5.3.0")
    def test_resolve_binary_from_engine_root(self, _mock_version, tmp_path):
        from cli_anything.unrealinsights.utils.unrealinsights_backend import resolve_binary_from_engine_root

        binary = _make_fake_binary(tmp_path, "UnrealInsights.exe")
        result = resolve_binary_from_engine_root("UnrealInsights.exe", str(tmp_path / "UE_5.5"))
        assert result["path"] == str(binary.resolve())
        assert result["source"] == "engine:UE_5.5"

    @patch("cli_anything.unrealinsights.utils.unrealinsights_backend.subprocess.run")
    def test_build_engine_program(self, mock_run, tmp_path):
        from cli_anything.unrealinsights.utils.unrealinsights_backend import build_engine_program

        build_bat = tmp_path / "UE_5.5" / "Engine" / "Build" / "BatchFiles" / "Build.bat"
        build_bat.parent.mkdir(parents=True, exist_ok=True)
        build_bat.write_text("echo build", encoding="utf-8")

        mock_run.return_value = type("Result", (), {"stdout": "ok", "stderr": "", "returncode": 0})()
        result = build_engine_program(str(tmp_path / "UE_5.5"), "UnrealInsights")
        assert result["succeeded"] is True
        assert Path(result["log_path"]).is_file()

    @patch("cli_anything.unrealinsights.utils.unrealinsights_backend._read_windows_product_version", return_value="5.3.0")
    @patch("cli_anything.unrealinsights.utils.unrealinsights_backend.build_engine_program")
    def test_ensure_engine_unrealinsights_builds_when_missing(self, mock_build, _mock_version, tmp_path):
        from cli_anything.unrealinsights.utils.unrealinsights_backend import ensure_engine_unrealinsights

        engine_root = tmp_path / "UE_5.5"
        (engine_root / "Engine" / "Binaries" / "Win64").mkdir(parents=True, exist_ok=True)
        (engine_root / "Engine" / "Build" / "BatchFiles").mkdir(parents=True, exist_ok=True)
        (engine_root / "Engine" / "Build" / "BatchFiles" / "Build.bat").write_text("echo build", encoding="utf-8")
        built_exe = engine_root / "Engine" / "Binaries" / "Win64" / "UnrealInsights.exe"
        built_exe.write_text("x", encoding="utf-8")
        mock_build.return_value = {
            "command": ["Build.bat"],
            "cwd": str(engine_root),
            "log_path": str(engine_root / "build.log"),
            "exit_code": 0,
            "timed_out": False,
            "stdout": "",
            "stderr": "",
            "succeeded": True,
        }

        result = ensure_engine_unrealinsights(str(engine_root))
        assert result["insights"]["path"] == str(built_exe.resolve())

    def test_ensure_engine_unrealinsights_no_build_errors_when_missing(self, tmp_path):
        from cli_anything.unrealinsights.utils.unrealinsights_backend import ensure_engine_unrealinsights

        engine_root = tmp_path / "UE_5.5"
        (engine_root / "Engine" / "Binaries" / "Win64").mkdir(parents=True, exist_ok=True)
        with pytest.raises(RuntimeError):
            ensure_engine_unrealinsights(str(engine_root), build_if_missing=False)
