# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCLIHelp:
    """Test that CLI help works without renderdoc installed."""

    def test_main_help(self):
        from click.testing import CliRunner
        from cli_anything.renderdoc.renderdoc_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "RenderDoc CLI" in result.output

    def test_capture_help(self):
        from click.testing import CliRunner
        from cli_anything.renderdoc.renderdoc_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["capture", "--help"])
        assert result.exit_code == 0
        assert "info" in result.output

    def test_actions_help(self):
        from click.testing import CliRunner
        from cli_anything.renderdoc.renderdoc_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["actions", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output

    def test_textures_help(self):
        from click.testing import CliRunner
        from cli_anything.renderdoc.renderdoc_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["textures", "--help"])
        assert result.exit_code == 0
        assert "save" in result.output

    def test_pipeline_help(self):
        from click.testing import CliRunner
        from cli_anything.renderdoc.renderdoc_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["pipeline", "--help"])
        assert result.exit_code == 0
        assert "state" in result.output

    def test_resources_help(self):
        from click.testing import CliRunner
        from cli_anything.renderdoc.renderdoc_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["resources", "--help"])
        assert result.exit_code == 0
        assert "buffers" in result.output

    def test_mesh_help(self):
        from click.testing import CliRunner
        from cli_anything.renderdoc.renderdoc_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["mesh", "--help"])
        assert result.exit_code == 0
        assert "inputs" in result.output

    def test_counters_help(self):
        from click.testing import CliRunner
        from cli_anything.renderdoc.renderdoc_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["counters", "--help"])
        assert result.exit_code == 0
        assert "fetch" in result.output


class TestCLISubprocess:
    """Test CLI via subprocess from agent-harness root (namespace on cwd)."""

    def test_cli_help_subprocess(self):
        import subprocess

        harness_root = Path(__file__).resolve().parents[3]
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "cli_anything.renderdoc.renderdoc_cli",
                    "--help",
                ],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(harness_root),
            )
            assert result.returncode == 0
            assert "RenderDoc CLI" in result.stdout
        except FileNotFoundError:
            pytest.skip("CLI not installed")
