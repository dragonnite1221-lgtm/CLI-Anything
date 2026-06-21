# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCLIParsing:
    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Obsidian CLI" in result.output

    def test_vault_help(self, runner):
        result = runner.invoke(cli, ["vault", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "read" in result.output
        assert "create" in result.output
        assert "update" in result.output
        assert "delete" in result.output
        assert "append" in result.output

    def test_search_help(self, runner):
        result = runner.invoke(cli, ["search", "--help"])
        assert result.exit_code == 0
        assert "query" in result.output
        assert "simple" in result.output

    def test_note_help(self, runner):
        result = runner.invoke(cli, ["note", "--help"])
        assert result.exit_code == 0
        assert "active" in result.output
        assert "open" in result.output

    def test_command_help(self, runner):
        result = runner.invoke(cli, ["command", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "execute" in result.output

    def test_server_help(self, runner):
        result = runner.invoke(cli, ["server", "--help"])
        assert result.exit_code == 0
        assert "status" in result.output

    def test_session_help(self, runner):
        result = runner.invoke(cli, ["session", "--help"])
        assert result.exit_code == 0
        assert "status" in result.output

    def test_json_flag(self, runner):
        result = runner.invoke(
            cli, ["--json", "--api-key", "test", "session", "status"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "host" in data

    def test_api_key_flag(self, runner):
        result = runner.invoke(
            cli, ["--json", "--api-key", "my-key", "session", "status"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["api_key_set"] is True

    def test_host_flag(self, runner):
        result = runner.invoke(
            cli,
            [
                "--host",
                "https://example:1234",
                "--api-key",
                "k",
                "--json",
                "session",
                "status",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["host"] == "https://example:1234"


class TestSessionState:
    def test_session_status_defaults(self, runner):
        result = runner.invoke(
            cli, ["--json", "--api-key", "test", "session", "status"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["api_key_set"] is True


class TestVaultCommands:
    @patch("cli_anything.obsidian.core.vault.api_get")
    def test_vault_list_json(self, mock_api, runner):
        mock_api.return_value = {"files": ["note1.md", "folder/note2.md"]}
        result = runner.invoke(cli, ["--json", "--api-key", "k", "vault", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "files" in data

    @patch("cli_anything.obsidian.core.vault.api_get")
    def test_vault_read_json(self, mock_api, runner):
        mock_api.return_value = {"content": "# Hello"}
        result = runner.invoke(
            cli, ["--json", "--api-key", "k", "vault", "read", "note.md"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["content"] == "# Hello"

    @patch("cli_anything.obsidian.core.vault.api_put")
    def test_vault_create_json(self, mock_api, runner):
        mock_api.return_value = {"status": "ok"}
        result = runner.invoke(
            cli,
            [
                "--json",
                "--api-key",
                "k",
                "vault",
                "create",
                "new.md",
                "--content",
                "# New Note",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "ok"

    @patch("cli_anything.obsidian.core.vault.api_delete")
    def test_vault_delete_json(self, mock_api, runner):
        mock_api.return_value = {"status": "ok"}
        result = runner.invoke(
            cli, ["--json", "--api-key", "k", "vault", "delete", "old.md"]
        )
        assert result.exit_code == 0

    @patch("cli_anything.obsidian.core.vault.api_put")
    @patch("cli_anything.obsidian.core.vault.api_get")
    def test_vault_append_json(self, mock_get, mock_put, runner):
        mock_get.return_value = {"content": "existing"}
        mock_put.return_value = {"status": "ok"}
        result = runner.invoke(
            cli,
            [
                "--json",
                "--api-key",
                "k",
                "vault",
                "append",
                "note.md",
                "--content",
                "extra text",
            ],
        )
        assert result.exit_code == 0


class TestSearchCommands:
    @patch("cli_anything.obsidian.core.search.api_post")
    def test_search_query_json(self, mock_api, runner):
        mock_api.return_value = [{"filename": "note.md", "score": 0.9}]
        result = runner.invoke(
            cli, ["--json", "--api-key", "k", "search", "query", "test"]
        )
        assert result.exit_code == 0

    @patch("cli_anything.obsidian.core.search.api_post")
    def test_search_simple_json(self, mock_api, runner):
        mock_api.return_value = [{"filename": "note.md", "matches": []}]
        result = runner.invoke(
            cli, ["--json", "--api-key", "k", "search", "simple", "hello"]
        )
        assert result.exit_code == 0
