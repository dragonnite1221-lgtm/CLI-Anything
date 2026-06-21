# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestVersions:
    def test_save_and_list(self, tmp_path, monkeypatch):
        from cli_anything.n8n.core import versions as ver

        monkeypatch.setattr(ver, "DB_DIR", tmp_path)
        monkeypatch.setattr(ver, "DB_PATH", tmp_path / "versions.db")

        wf = {"name": "Test WF", "nodes": [], "connections": {}}
        v1 = ver.save_snapshot("wf1", wf, "update")
        assert v1 == 1
        v2 = ver.save_snapshot("wf1", {**wf, "name": "Updated"}, "patch")
        assert v2 == 2

        vers = ver.list_versions("wf1")
        assert len(vers) == 2
        assert vers[0]["version_number"] == 2

    def test_get_snapshot(self, tmp_path, monkeypatch):
        from cli_anything.n8n.core import versions as ver

        monkeypatch.setattr(ver, "DB_DIR", tmp_path)
        monkeypatch.setattr(ver, "DB_PATH", tmp_path / "versions.db")

        wf = {"name": "Original", "nodes": [{"name": "A"}]}
        ver.save_snapshot("wf1", wf, "update")
        snapshot = ver.get_snapshot("wf1", 1)
        assert snapshot["name"] == "Original"
        assert snapshot["nodes"][0]["name"] == "A"

    def test_prune(self, tmp_path, monkeypatch):
        from cli_anything.n8n.core import versions as ver

        monkeypatch.setattr(ver, "DB_DIR", tmp_path)
        monkeypatch.setattr(ver, "DB_PATH", tmp_path / "versions.db")

        for i in range(5):
            ver.save_snapshot("wf1", {"name": f"v{i}"}, "test")
        deleted = ver.prune_versions("wf1", keep=2)
        assert deleted == 3
        remaining = ver.list_versions("wf1")
        assert len(remaining) == 2

    def test_stats(self, tmp_path, monkeypatch):
        from cli_anything.n8n.core import versions as ver

        monkeypatch.setattr(ver, "DB_DIR", tmp_path)
        monkeypatch.setattr(ver, "DB_PATH", tmp_path / "versions.db")

        ver.save_snapshot("wf1", {"name": "A"}, "test")
        ver.save_snapshot("wf2", {"name": "B"}, "test")
        st = ver.stats()
        assert st["total_versions"] == 2
        assert st["workflows_tracked"] == 2


class TestFixers:
    def test_expression_format(self):
        from cli_anything.n8n.core.fixers import autofix

        wf = {
            "name": "Test",
            "nodes": [
                {
                    "name": "Node1",
                    "type": "n8n-nodes-base.set",
                    "parameters": {"value": "{{$json.name}}"},
                }
            ],
            "connections": {},
        }
        _, fixes = autofix(wf, apply=False)
        assert any(f.fix_type == "expression-format" for f in fixes)

    def test_expression_format_apply(self):
        from cli_anything.n8n.core.fixers import autofix

        wf = {
            "name": "Test",
            "nodes": [
                {
                    "name": "Node1",
                    "type": "n8n-nodes-base.set",
                    "parameters": {"value": "{{$json.name}}"},
                }
            ],
            "connections": {},
        }
        fixed, fixes = autofix(wf, apply=True)
        assert fixed["nodes"][0]["parameters"]["value"] == "={{$json.name}}"

    def test_webhook_missing_path(self):
        from cli_anything.n8n.core.fixers import autofix

        wf = {
            "name": "Test",
            "nodes": [
                {"name": "Webhook", "type": "n8n-nodes-base.webhook", "parameters": {}}
            ],
            "connections": {},
        }
        _, fixes = autofix(wf, apply=False)
        assert any(f.fix_type == "webhook-missing-path" for f in fixes)

    def test_orphan_connection(self):
        from cli_anything.n8n.core.fixers import autofix

        wf = {
            "name": "Test",
            "nodes": [{"name": "A", "type": "test"}],
            "connections": {
                "NonExistent": {"main": [[{"node": "A", "type": "main", "index": 0}]]}
            },
        }
        fixed, fixes = autofix(wf, apply=True)
        assert "NonExistent" not in fixed["connections"]

    def test_no_issues(self):
        from cli_anything.n8n.core.fixers import autofix

        wf = {
            "name": "Test",
            "nodes": [
                {"name": "A", "type": "n8n-nodes-base.manualTrigger", "parameters": {}}
            ],
            "connections": {},
        }
        _, fixes = autofix(wf, apply=False)
        assert len(fixes) == 0

    def test_null_nodes_no_crash(self):
        """Bug fix: autofix must not crash when nodes or connections are None."""
        from cli_anything.n8n.core.fixers import autofix

        wf = {"name": "Test", "nodes": None, "connections": None}
        _, fixes = autofix(wf, apply=False)
        assert isinstance(fixes, list)

    def test_expression_in_list_apply(self):
        """Bug fix: _set_nested must handle bracket notation for list items."""
        from cli_anything.n8n.core.fixers import autofix

        wf = {
            "name": "Test",
            "nodes": [
                {
                    "name": "Set",
                    "type": "n8n-nodes-base.set",
                    "parameters": {
                        "assignments": [{"name": "x", "value": "{{$json.y}}"}]
                    },
                }
            ],
            "connections": {},
        }
        fixed, fixes = autofix(wf, apply=True)
        # The fix should update the value inside the list, not create a corrupted key
        assert "assignments[0]" not in fixed["nodes"][0]["parameters"]
        assert (
            fixed["nodes"][0]["parameters"]["assignments"][0]["value"] == "={{$json.y}}"
        )
