# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCliBootstrap:
    def test_nonexistent_project_path_bootstraps_new_document(self, tmp_path):
        project_path = tmp_path / "fresh.inkscape-cli.json"
        inkscape_cli._session = None
        runner = CliRunner()
        result = runner.invoke(
            inkscape_cli.cli,
            ["--project", str(project_path), "document", "save"],
        )
        assert result.exit_code == 0, result.output
        loaded = open_document(str(project_path))
        assert loaded["name"] == "fresh"
