# ruff: noqa: F403, F405, E501
from ._test_mubu_probe_base import *  # noqa: F403


class _WritePathTestsMixin2:
    def test_build_delete_node_request_builds_delete_payload(self):
        node = {
            "id": "child-2",
            "modified": 1773757000000,
            "text": "<span>临时删除节点</span>",
            "note": "<span>delete dry-run</span>",
            "children": [],
        }
        parent_node = {
            "id": "node-demo1",
        }

        request = build_delete_node_request(
            doc_id="doc-demo-01",
            member_id="7992964417993318",
            version=258,
            node=node,
            path=("nodes", 3, 0, 2),
            parent_node=parent_node,
        )

        self.assertEqual(request["pathname"], "/v3/api/colla/events")
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["data"]["documentId"], "doc-demo-01")
        self.assertEqual(request["data"]["memberId"], "7992964417993318")
        self.assertEqual(request["data"]["version"], 258)
        event = request["data"]["events"][0]
        self.assertEqual(event["name"], "delete")
        deleted = event["deleted"][0]
        self.assertEqual(deleted["parentId"], "node-demo1")
        self.assertEqual(deleted["index"], 2)
        self.assertEqual(
            deleted["path"],
            ["nodes", 3, "children", 0, "children", 2],
        )
        self.assertEqual(deleted["node"]["id"], "child-2")
        self.assertEqual(deleted["node"]["text"], "<span>临时删除节点</span>")
        self.assertEqual(deleted["node"]["note"], "<span>delete dry-run</span>")
