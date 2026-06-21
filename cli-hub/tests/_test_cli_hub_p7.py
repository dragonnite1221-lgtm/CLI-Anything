# ruff: noqa: F403, F405, E501
from ._test_cli_hub_base import *  # noqa: F403


class TestCLI:
    """Tests for the Click CLI interface."""

    def setup_method(self):
        self.runner = click.testing.CliRunner()
        self.human_detection = {
            "is_agent": False,
            "traffic_type": "human",
            "category": "human",
            "reason": "human",
            "signals": [],
            "stdin_tty": True,
            "is_interactive": True,
        }
        self.agent_detection = {
            "is_agent": True,
            "traffic_type": "agent",
            "category": "agent_tool",
            "reason": "codex-env",
            "signals": ["codex-env"],
            "stdin_tty": False,
            "is_interactive": False,
        }

    @patch("cli_hub.cli.track_first_run")
    @patch("cli_hub.cli.track_visit")
    @patch("cli_hub.cli.detect_invocation_context")
    def test_version(self, mock_detect, mock_visit, mock_first_run):
        mock_detect.return_value = self.human_detection
        result = self.runner.invoke(main, ["--version"])
        assert __version__ in result.output
        assert result.exit_code == 0
        mock_visit.assert_called_once_with(command="--version", detection=self.human_detection)
        mock_first_run.assert_called_once()

    @patch("cli_hub.cli.track_first_run")
    @patch("cli_hub.cli.track_visit")
    @patch("cli_hub.cli.detect_invocation_context")
    def test_help(self, mock_detect, mock_visit, mock_first_run):
        mock_detect.return_value = self.human_detection
        result = self.runner.invoke(main, ["--help"])
        assert "cli-hub" in result.output
        assert result.exit_code == 0

    @patch("cli_hub.cli.track_first_run")
    @patch("cli_hub.cli.track_visit")
    @patch("cli_hub.cli.detect_invocation_context")
    @patch("cli_hub.cli.fetch_all_clis", return_value=SAMPLE_REGISTRY["clis"])
    @patch("cli_hub.cli.list_categories", return_value=["3d", "audio", "image"])
    @patch("cli_hub.cli.get_installed", return_value={})
    def test_list_command(self, mock_installed, mock_categories, mock_fetch, mock_detect, mock_visit, mock_first_run):
        mock_detect.return_value = self.human_detection
        result = self.runner.invoke(main, ["list"])
        assert "gimp" in result.output
        assert "blender" in result.output
        assert result.exit_code == 0

    @patch("cli_hub.cli.track_first_run")
    @patch("cli_hub.cli.track_visit")
    @patch("cli_hub.cli.detect_invocation_context")
    @patch("cli_hub.cli.fetch_all_clis", return_value=SAMPLE_REGISTRY["clis"])
    @patch("cli_hub.cli.list_categories", return_value=["3d", "audio", "image"])
    @patch("cli_hub.cli.get_installed", return_value={})
    def test_list_with_category(self, mock_installed, mock_categories, mock_fetch, mock_detect, mock_visit, mock_first_run):
        mock_detect.return_value = self.human_detection
        result = self.runner.invoke(main, ["list", "-c", "image"])
        assert "gimp" in result.output
        assert "blender" not in result.output

    @patch("cli_hub.cli.track_first_run")
    @patch("cli_hub.cli.track_visit")
    @patch("cli_hub.cli.detect_invocation_context")
    @patch("cli_hub.cli.search_clis", return_value=[SAMPLE_REGISTRY["clis"][0]])
    @patch("cli_hub.cli.get_installed", return_value={})
    def test_search_command(self, mock_installed, mock_search, mock_detect, mock_visit, mock_first_run):
        mock_detect.return_value = self.human_detection
        result = self.runner.invoke(main, ["search", "gimp"])
        assert "gimp" in result.output
        assert result.exit_code == 0

    @patch("cli_hub.cli.track_first_run")
    @patch("cli_hub.cli.track_visit")
    @patch("cli_hub.cli.detect_invocation_context")
    @patch("cli_hub.cli.get_cli", return_value=SAMPLE_REGISTRY["clis"][0])
    @patch("cli_hub.cli.get_installed", return_value={})
    def test_info_command(self, mock_installed, mock_get, mock_detect, mock_visit, mock_first_run):
        mock_detect.return_value = self.human_detection
        result = self.runner.invoke(main, ["info", "gimp"])
        assert "GIMP" in result.output
        assert "image" in result.output
        assert "Install: cli-hub install gimp" in result.output
        assert result.exit_code == 0

    @patch("cli_hub.cli.track_first_run")
    @patch("cli_hub.cli.track_visit")
    @patch("cli_hub.cli.detect_invocation_context")
    @patch("cli_hub.cli.get_cli", return_value=None)
    def test_info_not_found(self, mock_get, mock_detect, mock_visit, mock_first_run):
        mock_detect.return_value = self.human_detection
        result = self.runner.invoke(main, ["info", "nonexistent"])
        assert result.exit_code == 1

    @patch("cli_hub.cli.track_first_run")
    @patch("cli_hub.cli.track_visit")
    @patch("cli_hub.cli.detect_invocation_context")
    @patch("cli_hub.cli.track_install")
    @patch("cli_hub.cli.install_cli", return_value=(True, "Installed GIMP (cli-anything-gimp)"))
    @patch("cli_hub.cli.get_cli", return_value=SAMPLE_REGISTRY["clis"][0])
    def test_install_command(self, mock_get, mock_install, mock_track, mock_detect, mock_visit, mock_first_run):
        mock_detect.return_value = self.human_detection
        result = self.runner.invoke(main, ["install", "gimp"])
        assert result.exit_code == 0
        assert "Installed" in result.output
        mock_track.assert_called_once()

    @patch("cli_hub.cli.track_first_run")
    @patch("cli_hub.cli.track_visit")
    @patch("cli_hub.cli.detect_invocation_context")
    @patch("cli_hub.cli.track_uninstall")
    @patch("cli_hub.cli.uninstall_cli", return_value=(True, "Uninstalled GIMP"))
    def test_uninstall_command(self, mock_uninstall, mock_track, mock_detect, mock_visit, mock_first_run):
        mock_detect.return_value = self.human_detection
        result = self.runner.invoke(main, ["uninstall", "gimp"])
        assert result.exit_code == 0
        mock_track.assert_called_once()

    @patch("cli_hub.cli.track_first_run")
    @patch("cli_hub.cli.track_visit")
    @patch("cli_hub.cli.detect_invocation_context")
    def test_visit_agent_on_invocation(self, mock_detect, mock_visit, mock_first_run):
        """When agent env detected, track_visit is called with the new cli-hub call metadata."""
        mock_detect.return_value = self.agent_detection
        result = self.runner.invoke(main, ["--version"])
        mock_visit.assert_called_once_with(command="--version", detection=self.agent_detection)

    @patch("cli_hub.cli.track_first_run")
    @patch("cli_hub.cli.track_visit")
    @patch("cli_hub.cli.detect_invocation_context")
    @patch("cli_hub.cli.install_cli", return_value=(True, "Installed Jimeng / Dreamina CLI (dreamina)"))
    @patch("cli_hub.cli.get_cli", return_value={**SAMPLE_REGISTRY["clis"][0], "entry_point": "dreamina", "name": "jimeng", "display_name": "Jimeng / Dreamina CLI", "version": "latest", "_source": "public"})
    @patch("cli_hub.cli.track_install")
    def test_install_shows_launch_hint(self, mock_track, mock_get, mock_install, mock_detect, mock_visit, mock_first_run):
        """Post-install output includes both entry point and cli-hub launch hint."""
        mock_detect.return_value = self.human_detection
        result = self.runner.invoke(main, ["install", "jimeng"])
        assert result.exit_code == 0
        assert "dreamina" in result.output
        assert "cli-hub launch jimeng" in result.output

    @patch("cli_hub.cli.track_first_run")
    @patch("cli_hub.cli.track_visit")
    @patch("cli_hub.cli.detect_invocation_context")
    @patch("cli_hub.cli.shutil.which", return_value="/usr/bin/dreamina")
    @patch("cli_hub.cli.os.execvp")
    @patch("cli_hub.cli.get_cli", return_value=JIMENG_CLI)
    def test_launch_execs_entry_point(self, mock_get, mock_execvp, mock_which, mock_detect, mock_visit, mock_first_run):
        """launch execs the CLI entry point, passing through extra args."""
        mock_detect.return_value = self.human_detection
        result = self.runner.invoke(main, ["launch", "jimeng", "login"])
        mock_execvp.assert_called_once_with("dreamina", ["dreamina", "login"])

    @patch("cli_hub.cli.track_first_run")
    @patch("cli_hub.cli.track_visit")
    @patch("cli_hub.cli.detect_invocation_context")
    @patch("cli_hub.cli.shutil.which", return_value=None)
    @patch("cli_hub.cli.get_cli", return_value=JIMENG_CLI)
    def test_launch_not_on_path_shows_install_hint(self, mock_get, mock_which, mock_detect, mock_visit, mock_first_run):
        """launch fails gracefully when entry point not on PATH."""
        mock_detect.return_value = self.human_detection
        result = self.runner.invoke(main, ["launch", "jimeng"])
        assert result.exit_code == 1
        assert "cli-hub install jimeng" in result.output

    @patch("cli_hub.cli.track_first_run")
    @patch("cli_hub.cli.track_visit")
    @patch("cli_hub.cli.detect_invocation_context")
    @patch("cli_hub.cli.get_cli", return_value=None)
    def test_launch_unknown_cli(self, mock_get, mock_detect, mock_visit, mock_first_run):
        """launch with an unknown CLI name exits with error."""
        mock_detect.return_value = self.human_detection
        result = self.runner.invoke(main, ["launch", "nonexistent"])
        assert result.exit_code == 1
        assert "not found" in result.output
