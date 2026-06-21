# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


def _skip_if_no_n8n():
    if not N8N_URL or not N8N_KEY:
        pytest.skip("N8N_BASE_URL and N8N_API_KEY required for E2E tests")


def _resolve_cli() -> list[str]:
    import shutil
    if shutil.which("cli-anything-n8n"):
        return ["cli-anything-n8n"]
    return [sys.executable, "-m", "cli_anything.n8n"]


class TestWorkflowsE2E:
    def test_list_workflows(self):
        _skip_if_no_n8n()
        result = workflows.list_workflows(base_url=N8N_URL, api_key=N8N_KEY, limit=5)
        assert "data" in result

    def test_workflow_crud(self):
        _skip_if_no_n8n()
        wf = workflows.create_workflow(
            {"name": "CLI-Anything Test WF", "nodes": [], "connections": {}, "settings": {}},
            base_url=N8N_URL, api_key=N8N_KEY,
        )
        wf_id = wf["id"]

        try:
            detail = workflows.get_workflow(wf_id, base_url=N8N_URL, api_key=N8N_KEY)
            assert detail["name"] == "CLI-Anything Test WF"

            updated = workflows.update_workflow(
                wf_id,
                {"name": "CLI-Anything Test WF Updated", "nodes": [], "connections": {}, "settings": {}},
                base_url=N8N_URL, api_key=N8N_KEY,
            )
            assert updated["name"] == "CLI-Anything Test WF Updated"
        finally:
            workflows.delete_workflow(wf_id, base_url=N8N_URL, api_key=N8N_KEY)

        try:
            workflows.get_workflow(wf_id, base_url=N8N_URL, api_key=N8N_KEY)
            assert False, "Workflow should have been deleted"
        except req.exceptions.HTTPError as e:
            assert e.response.status_code == 404


class TestCredentialsE2E:
    def test_get_schema(self):
        _skip_if_no_n8n()
        result = credentials.get_credential_schema("httpBasicAuth", base_url=N8N_URL, api_key=N8N_KEY)
        assert isinstance(result, (dict, list))


class TestVariablesE2E:
    def test_list_variables(self):
        _skip_if_no_n8n()
        try:
            result = variables.list_variables(base_url=N8N_URL, api_key=N8N_KEY)
            assert isinstance(result, (list, dict))
        except req.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                pytest.skip("Variables API requires Enterprise license")
            raise


class TestTagsE2E:
    def test_list_tags(self):
        _skip_if_no_n8n()
        result = tags.list_tags(base_url=N8N_URL, api_key=N8N_KEY)
        assert isinstance(result, (list, dict))

    def test_tag_lifecycle(self):
        _skip_if_no_n8n()
        unique_name = f"CLITEST{uuid.uuid4().hex[:8].upper()}"

        tag = tags.create_tag(unique_name, base_url=N8N_URL, api_key=N8N_KEY)
        tag_id = tag["id"]

        try:
            all_tags = tags.list_tags(base_url=N8N_URL, api_key=N8N_KEY)
            data = all_tags.get("data", all_tags) if isinstance(all_tags, dict) else all_tags
            names = [t["name"] for t in data if isinstance(t, dict)]
            assert unique_name in names

            updated_name = f"{unique_name}UPD"
            updated = tags.update_tag(tag_id, updated_name, base_url=N8N_URL, api_key=N8N_KEY)
            assert updated["name"] == updated_name
        finally:
            tags.delete_tag(tag_id, base_url=N8N_URL, api_key=N8N_KEY)
