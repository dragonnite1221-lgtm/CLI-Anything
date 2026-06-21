# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSystem:
    """Tests for system commands."""

    @patch("cli_anything.pm2.core.system.backend_version")
    def test_version_json(self, mock_ver):
        mock_ver.return_value = "5.3.0"
        from cli_anything.pm2.core.system import version

        result = version(as_json=True)
        assert result["version"] == "5.3.0"

    @patch("cli_anything.pm2.core.system.backend_save")
    def test_save_success(self, mock_save):
        mock_save.return_value = {
            "success": True,
            "returncode": 0,
            "stdout": "saved",
            "stderr": "",
        }
        from cli_anything.pm2.core.system import save

        result = save(as_json=False)
        assert result["success"] is True
        assert "saved" in result["message"].lower()


class TestOutputFormatting:
    """Tests for the _output helper in pm2_cli."""

    def test_output_json_string(self, capsys):
        from cli_anything.pm2.pm2_cli import _output

        _output("hello", as_json=True)
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["result"] == "hello"

    def test_output_json_dict(self, capsys):
        from cli_anything.pm2.pm2_cli import _output

        _output({"key": "val"}, as_json=True)
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["key"] == "val"

    def test_output_human_string(self, capsys):
        from cli_anything.pm2.pm2_cli import _output

        _output("hello world", as_json=False)
        captured = capsys.readouterr()
        assert "hello world" in captured.out

    def test_output_human_dict_with_message(self, capsys):
        from cli_anything.pm2.pm2_cli import _output

        _output({"success": True, "message": "Done"}, as_json=False)
        captured = capsys.readouterr()
        assert "[OK] Done" in captured.out

    def test_output_human_error_message(self, capsys):
        from cli_anything.pm2.pm2_cli import _output

        _output({"success": False, "message": "Oops"}, as_json=False)
        captured = capsys.readouterr()
        assert "[ERROR] Oops" in captured.out


class TestFormatBytes:
    """Tests for the byte formatting utility."""

    def test_zero_bytes(self):
        from cli_anything.pm2.core.processes import _format_bytes

        assert _format_bytes(0) == "0 B"

    def test_megabytes(self):
        from cli_anything.pm2.core.processes import _format_bytes

        result = _format_bytes(52428800)  # 50 MB
        assert "MB" in result
        assert "50.0" in result
