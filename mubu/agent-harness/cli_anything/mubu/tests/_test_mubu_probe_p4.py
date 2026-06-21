# ruff: noqa: F403, F405, E501
from ._test_mubu_probe_base import *  # noqa: F403


class DocumentNodeListingTests(unittest.TestCase):
    def test_list_document_nodes_flattens_tree_for_agent_targeting(self):
        data = {
            "nodes": [
                {
                    "id": "root-1",
                    "text": "<span>日志流</span>",
                    "note": "<span>顶层</span>",
                    "modified": 10,
                    "children": [
                        {
                            "id": "child-1",
                            "text": "<span>简历做一下</span>",
                            "note": "",
                            "modified": 20,
                            "children": [],
                        }
                    ],
                }
            ]
        }

        nodes = list_document_nodes(data)
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0]["node_id"], "root-1")
        self.assertEqual(nodes[0]["path"], ["nodes", 0])
        self.assertEqual(nodes[0]["depth"], 0)
        self.assertEqual(nodes[0]["text"], "日志流")
        self.assertEqual(nodes[1]["node_id"], "child-1")
        self.assertEqual(nodes[1]["path"], ["nodes", 0, 0])
        self.assertEqual(nodes[1]["depth"], 1)
        self.assertEqual(nodes[1]["text"], "简历做一下")

    def test_list_document_nodes_supports_query_and_max_depth(self):
        data = {
            "nodes": [
                {
                    "id": "root-1",
                    "text": "<span>日志流</span>",
                    "note": "",
                    "modified": 10,
                    "children": [
                        {
                            "id": "child-1",
                            "text": "<span>简历做一下</span>",
                            "note": "",
                            "modified": 20,
                            "children": [],
                        }
                    ],
                }
            ]
        }

        only_root = list_document_nodes(data, max_depth=0)
        self.assertEqual([item["node_id"] for item in only_root], ["root-1"])

        queried = list_document_nodes(data, query="简历")
        self.assertEqual([item["node_id"] for item in queried], ["child-1"])


class DailySelectionTests(unittest.TestCase):
    def test_looks_like_daily_title_accepts_date_titles_and_rejects_templates(self):
        self.assertTrue(looks_like_daily_title("26.03.16"))
        self.assertTrue(looks_like_daily_title("26.3.8-3.9"))
        self.assertTrue(looks_like_daily_title("2026-03-18"))
        self.assertTrue(looks_like_daily_title("2026年3月18日"))
        self.assertFalse(looks_like_daily_title("DDL表"))
        self.assertFalse(looks_like_daily_title("26.2.22模板更新"))

    def test_choose_current_daily_document_prefers_latest_date_titled_doc(self):
        docs = [
            {"doc_id": "template", "title": "26.2.22模板更新", "updated_at": 90},
            {"doc_id": "ddl", "title": "DDL表", "updated_at": 100},
            {"doc_id": "today", "title": "26.03.16", "updated_at": 120},
            {"doc_id": "yesterday", "title": "26.3.15", "updated_at": 110},
        ]

        selected, candidates = choose_current_daily_document(docs)
        self.assertEqual(selected["doc_id"], "today")
        self.assertEqual([item["doc_id"] for item in candidates], ["today", "yesterday"])

    def test_choose_current_daily_document_accepts_full_year_and_cn_date_titles(self):
        docs = [
            {"doc_id": "older", "title": "2026年3月17日", "updated_at": 90},
            {"doc_id": "latest", "title": "2026-03-18", "updated_at": 120},
            {"doc_id": "other", "title": "项目看板", "updated_at": 130},
        ]

        selected, candidates = choose_current_daily_document(docs)
        self.assertEqual(selected["doc_id"], "latest")
        self.assertEqual([item["doc_id"] for item in candidates], ["latest", "older"])

    def test_choose_current_daily_document_can_fallback_to_any_title(self):
        docs = [
            {"doc_id": "ddl", "title": "DDL表", "updated_at": 100},
            {"doc_id": "template", "title": "模板更新", "updated_at": 90},
        ]

        selected, candidates = choose_current_daily_document(docs, allow_non_daily_titles=True)
        self.assertEqual(selected["doc_id"], "ddl")
        self.assertEqual([item["doc_id"] for item in candidates], ["ddl", "template"])
