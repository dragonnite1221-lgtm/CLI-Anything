# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestBackendURLConstruction:
    """Verify SeaClipBackend builds correct URLs."""

    def test_default_base_url(self):
        b = SeaClipBackend()
        assert b.base_url == "http://127.0.0.1:5200"

    def test_custom_base_url(self):
        b = SeaClipBackend(base_url="http://myhost:9000/")
        assert b.base_url == "http://myhost:9000"  # trailing slash stripped

    def test_url_helper(self):
        b = SeaClipBackend(base_url="http://localhost:5200")
        assert b._url("/health") == "http://localhost:5200/health"

    def test_env_var_url(self, monkeypatch):
        monkeypatch.setenv("SEACLIP_URL", "http://envhost:1234")
        b = SeaClipBackend()
        assert b.base_url == "http://envhost:1234"


class TestJSONOutput:
    """Verify --json flag produces valid JSON for every command group."""

    @patch.object(
        SeaClipBackend, "health", return_value={"status": "ok", "version": "1.0"}
    )
    def test_server_health_json(self, mock_health):
        result, data = invoke_json("server", "health")
        assert result.exit_code == 0
        assert data["status"] == "ok"

    @patch.object(
        SeaClipBackend,
        "list_issues",
        return_value=[
            {"id": "abc-123", "title": "Bug", "status": "backlog", "priority": "high"}
        ],
    )
    def test_issue_list_json(self, mock_list):
        result, data = invoke_json("issue", "list")
        assert result.exit_code == 0
        assert isinstance(data, list)
        assert data[0]["title"] == "Bug"

    @patch.object(
        SeaClipBackend, "create_issue", return_value={"id": "new-uuid", "title": "Task"}
    )
    def test_issue_create_json(self, mock_create):
        result, data = invoke_json("issue", "create", "--title", "Task")
        assert result.exit_code == 0
        assert data["id"] == "new-uuid"

    @patch.object(
        SeaClipBackend,
        "list_agents",
        return_value=[{"name": "triage", "role": "triage", "status": "idle"}],
    )
    def test_agent_list_json(self, mock_agents):
        result, data = invoke_json("agent", "list")
        assert result.exit_code == 0
        assert isinstance(data, list)
        assert data[0]["name"] == "triage"

    @patch.object(
        SeaClipBackend,
        "list_schedules",
        return_value=[{"id": 1, "repo": "org/repo", "enabled": True}],
    )
    def test_scheduler_list_json(self, mock_sched):
        result, data = invoke_json("scheduler", "list")
        assert result.exit_code == 0
        assert isinstance(data, list)

    @patch.object(
        SeaClipBackend,
        "list_activity",
        return_value=[
            {
                "event_type": "issue_created",
                "summary": "New issue",
                "created_at": "2026-03-23T10:00:00",
            }
        ],
    )
    def test_activity_list_json(self, mock_act):
        result, data = invoke_json("activity", "list", "--limit", "5")
        assert result.exit_code == 0
        assert isinstance(data, list)


class TestHumanOutput:
    """Verify non-JSON output works without crashing."""

    @patch.object(
        SeaClipBackend,
        "list_issues",
        return_value=[
            {"id": "abc", "title": "Bug", "status": "backlog", "priority": "high"}
        ],
    )
    def test_issue_list_human(self, mock_list):
        result = invoke("issue", "list")
        assert result.exit_code == 0

    @patch.object(SeaClipBackend, "list_issues", return_value=[])
    def test_issue_list_empty_human(self, mock_list):
        result = invoke("issue", "list")
        assert result.exit_code == 0
