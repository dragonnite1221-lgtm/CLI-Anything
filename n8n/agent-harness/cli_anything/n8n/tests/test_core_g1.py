# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCredentials:
    @patch("cli_anything.n8n.core.credentials.api_post")
    def test_create_credential(self, mock_post):
        mock_post.return_value = {"id": "c1"}
        result = credentials.create_credential(
            {"name": "test", "type": "httpBasicAuth", "data": {}},
            base_url=BASE,
            api_key=KEY,
        )
        assert result["id"] == "c1"

    @patch("cli_anything.n8n.core.credentials.api_get")
    def test_get_schema(self, mock_get):
        mock_get.return_value = {"properties": {}}
        result = credentials.get_credential_schema(
            "telegramApi", base_url=BASE, api_key=KEY
        )
        assert "properties" in result

    @patch("cli_anything.n8n.core.credentials.api_delete")
    def test_delete_credential(self, mock_del):
        mock_del.return_value = {}
        credentials.delete_credential("c1", base_url=BASE, api_key=KEY)
        mock_del.assert_called_once()

    @patch("cli_anything.n8n.core.credentials.api_put")
    def test_transfer_credential(self, mock_put):
        mock_put.return_value = {}
        credentials.transfer_credential("c1", "proj-1", base_url=BASE, api_key=KEY)
        mock_put.assert_called_once()


class TestVariables:
    @patch("cli_anything.n8n.core.variables.api_get")
    def test_list_variables(self, mock_get):
        mock_get.return_value = [{"id": "1", "key": "FOO", "value": "bar"}]
        result = variables.list_variables(base_url=BASE, api_key=KEY)
        assert result[0]["key"] == "FOO"

    @patch("cli_anything.n8n.core.variables.api_post")
    def test_create_variable(self, mock_post):
        mock_post.return_value = {"id": "2", "key": "BAZ", "value": "qux"}
        result = variables.create_variable("BAZ", "qux", base_url=BASE, api_key=KEY)
        assert result["key"] == "BAZ"


class TestTags:
    @patch("cli_anything.n8n.core.tags.api_get")
    def test_list_tags(self, mock_get):
        mock_get.return_value = {"data": [{"id": "1", "name": "prod"}]}
        result = tags.list_tags(base_url=BASE, api_key=KEY)
        assert result["data"][0]["name"] == "prod"

    @patch("cli_anything.n8n.core.tags.api_post")
    def test_create_tag(self, mock_post):
        mock_post.return_value = {"id": "2", "name": "dev"}
        result = tags.create_tag("dev", base_url=BASE, api_key=KEY)
        assert result["name"] == "dev"


class TestProject:
    @patch.dict(
        "os.environ",
        {"N8N_BASE_URL": "https://env.example.com", "N8N_API_KEY": "env-key"},
    )
    def test_load_config_env_override(self):
        cfg = project.load_config()
        assert cfg["base_url"] == "https://env.example.com"
        assert cfg["api_key"] == "env-key"

    def test_get_connection_explicit_args(self):
        url, key = project.get_connection("https://arg.com", "arg-key")
        assert url == "https://arg.com"
        assert key == "arg-key"


class TestLoadJsonArg:
    def test_parse_inline_json(self):
        from cli_anything.n8n.n8n_cli import _load_json_arg

        result = _load_json_arg('{"name": "test"}')
        assert result == {"name": "test"}

    def test_invalid_json_raises(self):
        from cli_anything.n8n.n8n_cli import _load_json_arg

        with pytest.raises(ValueError, match="Invalid JSON"):
            _load_json_arg("not json")

    def test_file_not_found_raises(self):
        from cli_anything.n8n.n8n_cli import _load_json_arg

        with pytest.raises(ValueError, match="File not found"):
            _load_json_arg("@/nonexistent/file.json")

    def test_load_from_file(self, tmp_path):
        from cli_anything.n8n.n8n_cli import _load_json_arg

        f = tmp_path / "test.json"
        f.write_text('{"name": "from_file"}')
        result = _load_json_arg(f"@{f}")
        assert result == {"name": "from_file"}


class TestCLICommands:
    def test_export_import_roundtrip(self, tmp_path):
        """Test that export strips server fields using the REAL _clean_for_api."""
        from cli_anything.n8n.n8n_cli import _clean_for_api, _load_json_arg

        # Simulate export data (what get_workflow returns)
        server_data = {
            "id": "abc123",
            "name": "Test WF",
            "nodes": [{"type": "n8n-nodes-base.manualTrigger"}],
            "connections": {},
            "settings": {},
            "createdAt": "2026-01-01",
            "updatedAt": "2026-01-02",
            "versionId": "v1",
            "shared": [{"role": "owner"}],
        }
        # Use the REAL function, not a reimplementation
        export_data = _clean_for_api(server_data)
        assert "id" not in export_data
        assert "createdAt" not in export_data
        assert "name" in export_data
        assert "nodes" in export_data

        # Write and read back
        out = tmp_path / "export.json"
        out.write_text(json.dumps(export_data, indent=2))
        loaded = _load_json_arg(f"@{out}")
        assert loaded["name"] == "Test WF"
        assert "id" not in loaded
