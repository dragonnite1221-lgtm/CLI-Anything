# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestServerModule:
    @patch("cli_anything.obsidian.core.server.api_get")
    def test_server_status(self, mock_api):
        from cli_anything.obsidian.core.server import server_status

        mock_api.return_value = {"status": "OK", "authenticated": True}
        result = server_status("https://localhost:27124", "test-key")
        assert result["status"] == "OK"
        mock_api.assert_called_once_with("https://localhost:27124", "/", "test-key")


class TestVaultModule:
    @patch("cli_anything.obsidian.core.vault.api_get")
    def test_list_files_root(self, mock_api):
        from cli_anything.obsidian.core.vault import list_files

        mock_api.return_value = {"files": ["note1.md", "folder/note2.md"]}
        result = list_files("https://localhost:27124", "test-key")
        assert len(result["files"]) == 2
        mock_api.assert_called_once_with(
            "https://localhost:27124", "/vault/", "test-key"
        )

    @patch("cli_anything.obsidian.core.vault.api_get")
    def test_list_files_subfolder(self, mock_api):
        from cli_anything.obsidian.core.vault import list_files

        mock_api.return_value = {"files": ["note2.md"]}
        result = list_files("https://localhost:27124", "test-key", path="folder")
        mock_api.assert_called_once_with(
            "https://localhost:27124", "/vault/folder/", "test-key"
        )

    @patch("cli_anything.obsidian.core.vault.api_get")
    def test_read_note(self, mock_api):
        from cli_anything.obsidian.core.vault import read_note

        mock_api.return_value = {"content": "# Hello\nWorld"}
        result = read_note("https://localhost:27124", "test-key", "note.md")
        assert result["content"] == "# Hello\nWorld"

    @patch("cli_anything.obsidian.core.vault.api_put")
    def test_create_note(self, mock_api):
        from cli_anything.obsidian.core.vault import create_note

        mock_api.return_value = {"status": "ok"}
        result = create_note("https://localhost:27124", "test-key", "new.md", "# New")
        assert result["status"] == "ok"
        mock_api.assert_called_once_with(
            "https://localhost:27124", "/vault/new.md", "test-key", content="# New"
        )

    @patch("cli_anything.obsidian.core.vault.api_put")
    def test_update_note(self, mock_api):
        from cli_anything.obsidian.core.vault import update_note

        mock_api.return_value = {"status": "ok"}
        result = update_note(
            "https://localhost:27124", "test-key", "note.md", "# Updated"
        )
        assert result["status"] == "ok"

    @patch("cli_anything.obsidian.core.vault.api_delete")
    def test_delete_note(self, mock_api):
        from cli_anything.obsidian.core.vault import delete_note

        mock_api.return_value = {"status": "ok"}
        result = delete_note("https://localhost:27124", "test-key", "note.md")
        assert result["status"] == "ok"

    @patch("cli_anything.obsidian.core.vault.api_put")
    @patch("cli_anything.obsidian.core.vault.api_get")
    def test_append_note(self, mock_get, mock_put):
        from cli_anything.obsidian.core.vault import append_note

        mock_get.return_value = {"content": "# Existing"}
        mock_put.return_value = {"status": "ok"}
        result = append_note(
            "https://localhost:27124",
            "test-key",
            "note.md",
            "\nnew content",
            position="end",
        )
        assert result["status"] == "ok"
        mock_put.assert_called_once_with(
            "https://localhost:27124",
            "/vault/note.md",
            "test-key",
            content="# Existing\nnew content",
        )


class TestSearchModule:
    @patch("cli_anything.obsidian.core.search.api_post")
    def test_search_query(self, mock_api):
        from cli_anything.obsidian.core.search import search_query

        mock_api.return_value = [{"filename": "note.md", "score": 0.9}]
        result = search_query("https://localhost:27124", "test-key", "test query")
        mock_api.assert_called_once_with(
            "https://localhost:27124",
            "/search/",
            "test-key",
            data={"query": "test query"},
        )

    @patch("cli_anything.obsidian.core.search.api_post")
    def test_search_simple(self, mock_api):
        from cli_anything.obsidian.core.search import search_simple

        mock_api.return_value = [{"filename": "note.md", "matches": []}]
        result = search_simple(
            "https://localhost:27124", "test-key", "hello", context_length=50
        )
        mock_api.assert_called_once_with(
            "https://localhost:27124",
            "/search/simple/",
            "test-key",
            params={"query": "hello", "contextLength": 50},
        )


class TestNoteModule:
    @patch("cli_anything.obsidian.core.note.api_get")
    def test_get_active(self, mock_api):
        from cli_anything.obsidian.core.note import get_active

        mock_api.return_value = {"content": "# Active Note"}
        result = get_active("https://localhost:27124", "test-key")
        assert result["content"] == "# Active Note"

    @patch("cli_anything.obsidian.core.note.api_put")
    def test_open_note(self, mock_api):
        from cli_anything.obsidian.core.note import open_note

        mock_api.return_value = {"status": "ok"}
        result = open_note("https://localhost:27124", "test-key", "folder/note.md")
        assert result["status"] == "ok"


class TestCommandModule:
    @patch("cli_anything.obsidian.core.command.api_get")
    def test_list_commands(self, mock_api):
        from cli_anything.obsidian.core.command import list_commands

        mock_api.return_value = {
            "commands": [{"id": "editor:toggle-bold", "name": "Bold"}]
        }
        result = list_commands("https://localhost:27124", "test-key")
        assert len(result["commands"]) == 1

    @patch("cli_anything.obsidian.core.command.api_post")
    def test_execute_command(self, mock_api):
        from cli_anything.obsidian.core.command import execute_command

        mock_api.return_value = {"status": "ok"}
        result = execute_command(
            "https://localhost:27124", "test-key", "editor:toggle-bold"
        )
        assert result["status"] == "ok"
        mock_api.assert_called_once_with(
            "https://localhost:27124", "/commands/editor:toggle-bold/", "test-key"
        )
