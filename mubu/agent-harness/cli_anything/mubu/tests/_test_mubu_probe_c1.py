# ruff: noqa: F403, F405, E501
from ._test_mubu_probe_base import *  # noqa: F403


class _WritePathTestsMixin1:
    def test_build_create_child_request_builds_create_payload(self):
        parent_node = {
            "id": "node-demo1",
            "children": [
                {"id": "child-0"},
                {"id": "child-1"},
            ],
        }

        request = build_create_child_request(
            doc_id="doc-demo-01",
            member_id="7992964417993318",
            version=257,
            parent_node=parent_node,
            parent_path=("nodes", 3, 0),
            text="继续推进 create-child",
            note="先 dry-run",
            child_id="new-child-1",
            modified_ms=1773748000000,
        )

        self.assertEqual(request["pathname"], "/v3/api/colla/events")
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["data"]["documentId"], "doc-demo-01")
        self.assertEqual(request["data"]["memberId"], "7992964417993318")
        self.assertEqual(request["data"]["version"], 257)
        event = request["data"]["events"][0]
        self.assertEqual(event["name"], "create")
        created = event["created"][0]
        self.assertEqual(created["index"], 2)
        self.assertEqual(created["parentId"], "node-demo1")
        self.assertEqual(
            created["path"],
            ["nodes", 3, "children", 0, "children", 2],
        )
        self.assertEqual(created["node"]["id"], "new-child-1")
        self.assertEqual(created["node"]["taskStatus"], 0)
        self.assertEqual(created["node"]["text"], "<span>继续推进 create-child</span>")
        self.assertEqual(created["node"]["note"], "<span>先 dry-run</span>")
        self.assertEqual(created["node"]["modified"], 1773748000000)
        self.assertEqual(created["node"]["children"], [])
        self.assertTrue(created["node"]["forceUpdate"])
    def test_parent_context_for_nested_node_path_returns_parent_and_index(self):
        data = {
            "nodes": [
                {
                    "id": "root-1",
                    "children": [
                        {
                            "id": "child-1",
                            "children": [
                                {
                                    "id": "leaf-1",
                                    "children": [],
                                }
                            ],
                        }
                    ],
                }
            ]
        }

        parent_node, parent_path, index = parent_context_for_path(data, ("nodes", 0, 0, 0))
        self.assertEqual(parent_node["id"], "child-1")
        self.assertEqual(parent_path, ("nodes", 0, 0))
        self.assertEqual(index, 0)
    def test_parent_context_for_root_node_path_returns_none_parent(self):
        data = {
            "nodes": [
                {
                    "id": "root-1",
                    "children": [],
                }
            ]
        }

        parent_node, parent_path, index = parent_context_for_path(data, ("nodes", 0))
        self.assertIsNone(parent_node)
        self.assertIsNone(parent_path)
        self.assertEqual(index, 0)
