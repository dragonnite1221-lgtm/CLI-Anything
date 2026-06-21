# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestFiles:
    @patch("cli_anything.rms.core.files.api_get")
    def test_list_files(self, mock_get):
        from cli_anything.rms.core.files import list_files

        mock_get.return_value = {"success": True, "data": [{"id": 1, "name": "fw.bin"}]}
        result = list_files("token")
        mock_get.assert_called_once()
        assert result["data"][0]["name"] == "fw.bin"

    @patch("cli_anything.rms.core.files.api_get")
    def test_get_file(self, mock_get):
        from cli_anything.rms.core.files import get_file

        mock_get.return_value = {
            "success": True,
            "data": {"id": 1, "name": "fw.bin", "size": 1024},
        }
        result = get_file("token", "1")
        assert result["data"]["size"] == 1024

    @patch("cli_anything.rms.core.files.api_delete")
    def test_delete_file(self, mock_delete):
        from cli_anything.rms.core.files import delete_file

        mock_delete.return_value = {"success": True}
        result = delete_file("token", "1")
        assert result["success"] is True


class TestReports:
    @patch("cli_anything.rms.core.reports.api_get")
    def test_list_reports(self, mock_get):
        from cli_anything.rms.core.reports import list_reports

        mock_get.return_value = {"success": True, "data": [{"id": 1}]}
        result = list_reports("token")
        mock_get.assert_called_once()
        assert result["success"] is True

    @patch("cli_anything.rms.core.reports.api_get")
    def test_get_report(self, mock_get):
        from cli_anything.rms.core.reports import get_report

        mock_get.return_value = {"success": True, "data": {"id": 1, "name": "Weekly"}}
        result = get_report("token", "1")
        assert result["data"]["name"] == "Weekly"

    @patch("cli_anything.rms.core.reports.api_post")
    def test_create_report(self, mock_post):
        from cli_anything.rms.core.reports import create_report

        mock_post.return_value = {"success": True, "data": {"id": 2, "name": "Daily"}}
        result = create_report("token", {"name": "Daily"})
        assert result["data"]["name"] == "Daily"

    @patch("cli_anything.rms.core.reports.api_delete")
    def test_delete_report(self, mock_delete):
        from cli_anything.rms.core.reports import delete_report

        mock_delete.return_value = {"success": True}
        result = delete_report("token", "1")
        assert result["success"] is True

    @patch("cli_anything.rms.core.reports.api_get")
    def test_list_templates(self, mock_get):
        from cli_anything.rms.core.reports import list_templates

        mock_get.return_value = {"success": True, "data": [{"id": 1, "name": "tmpl1"}]}
        result = list_templates("token")
        assert len(result["data"]) == 1

    @patch("cli_anything.rms.core.reports.api_post")
    def test_create_template(self, mock_post):
        from cli_anything.rms.core.reports import create_template

        mock_post.return_value = {
            "success": True,
            "data": {"id": 2, "name": "new-tmpl"},
        }
        result = create_template("token", {"name": "new-tmpl"})
        assert result["data"]["name"] == "new-tmpl"
