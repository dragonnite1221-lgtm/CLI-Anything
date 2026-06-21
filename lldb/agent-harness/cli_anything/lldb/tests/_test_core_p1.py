# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestCLIJsonErrors:
    @patch("cli_anything.lldb.lldb_cli._get_session")
    def test_target_info_no_target_json(self, mock_get_session):
        from cli_anything.lldb.lldb_cli import cli

        fake_session = MagicMock()
        fake_session.target = None
        mock_get_session.return_value = fake_session

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "target", "info"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "error" in data

    @patch("cli_anything.lldb.lldb_cli._get_session")
    def test_thread_info_no_selected_thread_json(self, mock_get_session):
        from cli_anything.lldb.lldb_cli import cli

        fake_session = MagicMock()
        fake_session.session_status.return_value = {"has_target": True, "has_process": True}
        fake_session.threads.return_value = {"threads": [{"id": 1, "selected": False}]}
        mock_get_session.return_value = fake_session

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "thread", "info"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["error"] == "No selected thread"

    @patch("cli_anything.lldb.lldb_cli._get_session")
    def test_process_info_uses_public_session_api(self, mock_get_session):
        from cli_anything.lldb.lldb_cli import cli

        fake_session = MagicMock()
        fake_session.session_status.return_value = {"has_target": True, "has_process": True}
        fake_session.process_info.return_value = {"pid": 1234, "state": "stopped", "num_threads": 1}
        fake_session._process_info.side_effect = AssertionError("private API should not be used")
        mock_get_session.return_value = fake_session

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "process", "info"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["pid"] == 1234
        fake_session.process_info.assert_called_once_with()

    @patch("cli_anything.lldb.lldb_cli._get_session")
    def test_process_info_no_process_json(self, mock_get_session):
        from cli_anything.lldb.lldb_cli import cli

        fake_session = MagicMock()
        fake_session.target = object()
        fake_session.process = None
        mock_get_session.return_value = fake_session

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "process", "info"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "error" in data


class TestBackend:
    @patch("cli_anything.lldb.utils.lldb_backend.subprocess.run")
    @patch("cli_anything.lldb.utils.lldb_backend.os.path.isdir", return_value=False)
    def test_backend_probe_failure(self, _mock_isdir, mock_run):
        from cli_anything.lldb.utils import lldb_backend

        mock_run.return_value = MagicMock(stdout="", stderr="not found")
        with patch("builtins.__import__", side_effect=ImportError()):
            with pytest.raises(RuntimeError):
                lldb_backend.ensure_lldb_importable()

    @patch("cli_anything.lldb.utils.lldb_backend.subprocess.run", side_effect=FileNotFoundError())
    def test_backend_no_lldb_binary(self, _mock_run):
        from cli_anything.lldb.utils import lldb_backend

        with patch("builtins.__import__", side_effect=ImportError()):
            with pytest.raises(RuntimeError) as exc:
                lldb_backend.ensure_lldb_importable()
        assert "LLDB not found" in str(exc.value)


class TestSessionDaemonSecurity:
    def test_state_file_is_written_with_restrictive_mode(self, tmp_path):
        from cli_anything.lldb.utils.session_server import _write_state_file

        state_file = tmp_path / "secure" / "session.json"
        _write_state_file(state_file, ("127.0.0.1", 1234), b"secret")

        data = json.loads(state_file.read_text(encoding="utf-8"))
        assert data["host"] == "127.0.0.1"
        assert data["port"] == 1234
        assert data["token"]
        if os.name != "nt":
            assert stat.S_IMODE(state_file.parent.stat().st_mode) == 0o700
            assert stat.S_IMODE(state_file.stat().st_mode) == 0o600

    def test_session_server_rejects_unknown_methods(self):
        from cli_anything.lldb.utils.session_server import SessionServer

        server = SessionServer()
        response, should_stop = server.handle({"method": "__getattribute__", "args": ["debugger"], "kwargs": {}})

        assert should_stop is False
        assert response["ok"] is False
        assert "Unsupported session method" in response["error"]
