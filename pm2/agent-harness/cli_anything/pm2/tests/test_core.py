# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestFindPm2:
    """Tests for pm2 binary discovery."""

    @patch("shutil.which", return_value="/opt/homebrew/bin/pm2")
    def test_find_pm2_found(self, mock_which):
        from cli_anything.pm2.utils.pm2_backend import _find_pm2

        assert _find_pm2() == "/opt/homebrew/bin/pm2"

    @patch("shutil.which", return_value=None)
    def test_find_pm2_not_found_raises(self, mock_which):
        from cli_anything.pm2.utils.pm2_backend import _find_pm2

        with pytest.raises(RuntimeError, match="pm2 not found"):
            _find_pm2()


class TestRunPm2:
    """Tests for the core run_pm2 subprocess wrapper."""

    @patch("cli_anything.pm2.utils.pm2_backend._get_pm2", return_value="/usr/bin/pm2")
    @patch("subprocess.run")
    def test_run_pm2_success(self, mock_run, mock_get):
        mock_run.return_value = _make_run_result(stdout="OK\n", returncode=0)
        from cli_anything.pm2.utils.pm2_backend import run_pm2

        result = run_pm2("save")
        assert result["success"] is True
        assert result["returncode"] == 0
        assert "OK" in result["stdout"]

    @patch("cli_anything.pm2.utils.pm2_backend._get_pm2", return_value="/usr/bin/pm2")
    @patch("subprocess.run")
    def test_run_pm2_failure(self, mock_run, mock_get):
        mock_run.return_value = _make_run_result(stderr="error", returncode=1)
        from cli_anything.pm2.utils.pm2_backend import run_pm2

        result = run_pm2("restart", "ghost")
        assert result["success"] is False
        assert result["returncode"] == 1

    @patch("cli_anything.pm2.utils.pm2_backend._get_pm2", return_value="/usr/bin/pm2")
    @patch("subprocess.run")
    def test_run_pm2_json_parsing(self, mock_run, mock_get):
        mock_run.return_value = _make_run_result(stdout=FAKE_JLIST, returncode=0)
        from cli_anything.pm2.utils.pm2_backend import run_pm2

        result = run_pm2("jlist", capture_json=True)
        assert result["success"] is True
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2
        assert result["data"][0]["name"] == "seaclip-dev"

    @patch("cli_anything.pm2.utils.pm2_backend._get_pm2", return_value="/usr/bin/pm2")
    @patch("subprocess.run")
    def test_run_pm2_json_with_preamble(self, mock_run, mock_get):
        """JSON extraction works even with non-JSON text before the array."""
        preamble = "PM2 info line\n" + FAKE_JLIST
        mock_run.return_value = _make_run_result(stdout=preamble, returncode=0)
        from cli_anything.pm2.utils.pm2_backend import run_pm2

        result = run_pm2("jlist", capture_json=True)
        assert result["data"] is not None
        assert isinstance(result["data"], list)

    @patch("cli_anything.pm2.utils.pm2_backend._get_pm2", return_value="/usr/bin/pm2")
    @patch(
        "subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="pm2", timeout=30)
    )
    def test_run_pm2_timeout(self, mock_run, mock_get):
        from cli_anything.pm2.utils.pm2_backend import run_pm2

        result = run_pm2("jlist", timeout=30)
        assert result["success"] is False
        assert "timed out" in result["stderr"]

    @patch(
        "cli_anything.pm2.utils.pm2_backend._get_pm2", return_value="/nonexistent/pm2"
    )
    @patch("subprocess.run", side_effect=FileNotFoundError())
    def test_run_pm2_binary_missing(self, mock_run, mock_get):
        from cli_anything.pm2.utils.pm2_backend import run_pm2

        result = run_pm2("jlist")
        assert result["success"] is False
        assert "not found" in result["stderr"]
