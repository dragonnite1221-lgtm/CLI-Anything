# ruff: noqa: F403, F405, E501
from ._test_mubu_probe_base import *  # noqa: F403


class DocumentMetadataOverlayTests(unittest.TestCase):
    def test_document_links_prefers_metadata_title_for_source_document(self):
        links = document_links(
            [
                {
                    "doc_id": "docA",
                    "title": "root node title",
                    "data": {
                        "nodes": [
                            {
                                "id": "n1",
                                "text": (
                                    '<a class="mention mm-iconfont" '
                                    'href="https://mubu.com/docdoc-target-1" '
                                    'data-token="doc-target-1">Target Doc</a>'
                                ),
                                "children": [],
                            }
                        ]
                    },
                }
            ],
            "docA",
            title_lookup={"docA": "26.03.18", "doc-target-1": "Target Doc"},
        )

        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["source_doc_title"], "26.03.18")

    def test_show_command_prefers_metadata_title_and_path_when_available(self):
        backups = [
            {
                "doc_id": "docA",
                "title": "root node title",
                "backup_file": "/tmp/docA.json",
                "modified_at": 123.0,
                "data": {
                    "viewType": "OUTLINE",
                    "nodes": [{"id": "n1", "text": "<span>today</span>", "children": []}],
                },
            }
        ]
        metas = [{"doc_id": "docA", "folder_id": "dailyA", "title": "26.03.18", "updated_at": 20}]
        folders = [
            {"folder_id": "rootA", "name": "Workspace", "parent_id": "0"},
            {"folder_id": "dailyA", "name": "Daily tasks", "parent_id": "rootA"},
        ]

        stdout = io.StringIO()
        with (
            mock.patch("mubu_probe.load_latest_backups", return_value=backups),
            mock.patch("mubu_probe.load_document_metas", return_value=metas),
            mock.patch("mubu_probe.load_folders", return_value=folders),
            contextlib.redirect_stdout(stdout),
        ):
            result = main(["show", "docA", "--json"])

        self.assertEqual(result, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["title"], "26.03.18")
        self.assertEqual(payload["folder_path"], "Workspace/Daily tasks")
        self.assertEqual(payload["doc_path"], "Workspace/Daily tasks/26.03.18")
