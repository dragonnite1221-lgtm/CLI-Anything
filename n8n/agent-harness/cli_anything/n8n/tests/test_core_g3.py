# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestNodes:
    @patch("cli_anything.n8n.core.nodes.requests.get")
    def test_search_nodes(self, mock_get):
        from cli_anything.n8n.core import nodes as nd

        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "total": 100,
            "objects": [
                {
                    "package": {
                        "name": "n8n-nodes-test",
                        "version": "1.0.0",
                        "description": "Test",
                        "publisher": {"username": "dev"},
                    }
                }
            ],
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        result = nd.search_nodes("test")
        assert result["total"] == 100

    @patch("cli_anything.n8n.core.nodes.requests.get")
    def test_get_node_info(self, mock_get):
        from cli_anything.n8n.core import nodes as nd

        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "name": "n8n-nodes-test",
            "description": "Test pkg",
            "dist-tags": {"latest": "1.0.0"},
            "versions": {
                "1.0.0": {
                    "license": "MIT",
                    "n8n": {"nodes": [{"type": "testNode"}], "credentials": []},
                    "keywords": [],
                }
            },
            "author": {"name": "dev"},
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        result = nd.get_node_info("n8n-nodes-test")
        assert result["name"] == "n8n-nodes-test"
        assert len(result["n8n_nodes"]) == 1


class TestScaffolds:
    def test_list_patterns(self):
        from cli_anything.n8n.core.scaffolds import list_patterns

        patterns = list_patterns()
        assert len(patterns) == 5
        names = {p["name"] for p in patterns}
        assert "webhook" in names
        assert "ai-agent" in names

    def test_get_scaffold(self):
        from cli_anything.n8n.core.scaffolds import get_scaffold

        wf = get_scaffold("webhook")
        assert wf["name"] == "Webhook Processing"
        assert len(wf["nodes"]) > 0
        assert "connections" in wf

    def test_get_scaffold_custom_name(self):
        from cli_anything.n8n.core.scaffolds import get_scaffold

        wf = get_scaffold("api", name="My API Flow")
        assert wf["name"] == "My API Flow"

    def test_get_scaffold_invalid(self):
        from cli_anything.n8n.core.scaffolds import get_scaffold

        with pytest.raises(ValueError, match="Unknown pattern"):
            get_scaffold("nonexistent")


class TestExpressions:
    def test_valid_expression(self):
        from cli_anything.n8n.core.expressions import validate_expression

        result = validate_expression("={{$json.name}}")
        assert result.valid
        assert len(result.issues) == 0

    def test_mismatched_braces(self):
        from cli_anything.n8n.core.expressions import validate_expression

        result = validate_expression("={{$json.name}")
        assert not result.valid
        assert any("Mismatched" in i for i in result.issues)

    def test_missing_equals_prefix(self):
        from cli_anything.n8n.core.expressions import validate_expression

        result = validate_expression("{{$json.name}}")
        assert result.valid  # valid but with warning
        assert any("prefix" in w for w in result.warnings)

    def test_json_bracket_without_quotes(self):
        from cli_anything.n8n.core.expressions import validate_expression

        result = validate_expression("={{$json[key]}}")
        assert any("quotes" in i for i in result.issues)


class TestTemplates:
    @patch("cli_anything.n8n.core.templates.requests.get")
    def test_search_templates(self, mock_get):
        from cli_anything.n8n.core import templates as tmpl

        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "totalWorkflows": 5,
            "workflows": [{"id": 1, "name": "Test"}],
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        result = tmpl.search_templates("telegram")
        assert result["totalWorkflows"] == 5

    @patch("cli_anything.n8n.core.templates.requests.get")
    def test_get_template(self, mock_get):
        from cli_anything.n8n.core import templates as tmpl

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"workflow": {"name": "My Template", "nodes": []}}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        result = tmpl.get_template(123)
        assert result["workflow"]["name"] == "My Template"
