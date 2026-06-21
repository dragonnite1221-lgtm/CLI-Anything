# ruff: noqa: F403, F405, E501
from ._test_mubu_probe_base import *  # noqa: F403


class PathResolutionTests(unittest.TestCase):
    def setUp(self):
        self.folders = [
            {"folder_id": "rootA", "name": "Workspace", "parent_id": "0"},
            {"folder_id": "dailyA", "name": "Daily tasks", "parent_id": "rootA"},
            {"folder_id": "rootB", "name": "Archive", "parent_id": "0"},
            {"folder_id": "dailyB", "name": "Daily tasks", "parent_id": "rootB"},
        ]
        self.document_metas = [
            {"doc_id": "docA", "folder_id": "dailyA", "title": "26.03.16", "updated_at": 20},
            {"doc_id": "docA2", "folder_id": "dailyA", "title": "26.03.16", "updated_at": 25},
            {"doc_id": "docB", "folder_id": "dailyA", "title": "26.3.15", "updated_at": 10},
            {"doc_id": "docC", "folder_id": "dailyB", "title": "26.03.16", "updated_at": 30},
        ]
        self.backups = [
            {
                "doc_id": "docA2",
                "title": "today root",
                "backup_file": "/tmp/docA2.json",
                "modified_at": 123.0,
                "data": {"viewType": "OUTLINE", "nodes": [{"id": "n1", "text": "<span>today</span>", "children": []}]},
            }
        ]

    def test_folder_documents_supports_full_folder_path(self):
        docs, folder, ambiguous = folder_documents(self.document_metas, self.folders, "Workspace/Daily tasks")
        self.assertEqual(ambiguous, [])
        self.assertEqual(folder["folder_id"], "dailyA")
        self.assertEqual([doc["doc_id"] for doc in docs], ["docA2", "docB"])
        self.assertEqual(docs[0]["doc_path"], "Workspace/Daily tasks/26.03.16")

    def test_folder_documents_detects_ambiguous_folder_name(self):
        docs, folder, ambiguous = folder_documents(self.document_metas, self.folders, "Daily tasks")
        self.assertEqual(docs, [])
        self.assertIsNone(folder)
        self.assertEqual(len(ambiguous), 2)

    def test_resolve_document_reference_supports_full_doc_path(self):
        doc, ambiguous = resolve_document_reference(self.document_metas, self.folders, "Workspace/Daily tasks/26.03.16")
        self.assertEqual(ambiguous, [])
        self.assertEqual(doc["doc_id"], "docA2")
        self.assertEqual(doc["doc_path"], "Workspace/Daily tasks/26.03.16")

    def test_resolve_document_reference_detects_ambiguous_title(self):
        doc, ambiguous = resolve_document_reference(self.document_metas, self.folders, "26.03.16")
        self.assertIsNone(doc)
        self.assertEqual(len(ambiguous), 2)
        self.assertEqual({item["doc_id"] for item in ambiguous}, {"docA2", "docC"})

    def test_resolve_document_reference_collapses_same_path_duplicates_for_title(self):
        folders = [
            {"folder_id": "rootA", "name": "Workspace", "parent_id": "0"},
            {"folder_id": "dailyA", "name": "Daily tasks", "parent_id": "rootA"},
        ]
        metas = [
            {"doc_id": "old", "folder_id": "dailyA", "title": "26.03.18", "updated_at": 10},
            {"doc_id": "new", "folder_id": "dailyA", "title": "26.03.18", "updated_at": 20},
        ]

        doc, ambiguous = resolve_document_reference(metas, folders, "26.03.18")

        self.assertEqual(ambiguous, [])
        self.assertEqual(doc["doc_id"], "new")

    def test_resolve_document_reference_prefers_newer_timestamp_over_higher_revision_across_doc_ids(self):
        folders = [
            {"folder_id": "rootA", "name": "Workspace", "parent_id": "0"},
            {"folder_id": "dailyA", "name": "Daily tasks", "parent_id": "rootA"},
        ]
        metas = [
            {
                "doc_id": "old-high-rev",
                "folder_id": "dailyA",
                "title": "26.03.19",
                "updated_at": 10,
                "_rev": "999-older",
            },
            {
                "doc_id": "new-low-rev",
                "folder_id": "dailyA",
                "title": "26.03.19",
                "updated_at": 20,
                "_rev": "1-newer",
            },
        ]

        doc, ambiguous = resolve_document_reference(metas, folders, "Workspace/Daily tasks/26.03.19")

        self.assertEqual(ambiguous, [])
        self.assertEqual(doc["doc_id"], "new-low-rev")

    def test_show_document_by_reference_uses_resolved_path(self):
        payload, ambiguous = show_document_by_reference(
            self.backups,
            self.document_metas,
            self.folders,
            "Workspace/Daily tasks/26.03.16",
        )
        self.assertEqual(ambiguous, [])
        self.assertEqual(payload["doc_id"], "docA2")
        self.assertEqual(payload["title"], "26.03.16")
        self.assertEqual(payload["folder_path"], "Workspace/Daily tasks")
        self.assertEqual(payload["doc_path"], "Workspace/Daily tasks/26.03.16")
        self.assertEqual(payload["nodes"][0]["text"], "today")
