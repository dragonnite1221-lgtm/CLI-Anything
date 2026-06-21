# ruff: noqa: F403, F405, E501
from ._test_mubu_probe_base import *  # noqa: F403


class ExtractPlainTextTests(unittest.TestCase):
    def test_extract_plain_text_handles_html_and_segment_lists(self):
        self.assertEqual(extract_plain_text("<span>简历做一下</span>"), "简历做一下")
        self.assertEqual(
            extract_plain_text(
                [
                    {"type": 1, "text": "简历"},
                    {"type": 1, "text": "更新"},
                ]
            ),
            "简历更新",
        )


class BackupLoadingTests(unittest.TestCase):
    def test_load_latest_backups_picks_newest_file_per_document(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc_dir = root / "docA"
            doc_dir.mkdir()

            older = doc_dir / "2026-03-01 10'00.json"
            newer = doc_dir / "2026-03-01 11'00.json"
            older.write_text(json.dumps({"nodes": [{"text": "<span>旧</span>", "children": []}]}))
            newer.write_text(json.dumps({"nodes": [{"text": "<span>新</span>", "children": []}]}))

            older.touch()
            newer.touch()

            docs = load_latest_backups(root)
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0]["doc_id"], "docA")
            self.assertTrue(docs[0]["backup_file"].endswith("11'00.json"))
            self.assertEqual(docs[0]["title"], "新")


class SearchTests(unittest.TestCase):
    def test_search_documents_finds_text_and_note(self):
        docs = [
            {
                "doc_id": "docA",
                "backup_file": "/tmp/docA.json",
                "title": "项目计划",
                "data": {
                    "nodes": [
                        {
                            "id": "n1",
                            "text": "<span>简历做一下更新</span>",
                            "note": "<span>今天处理</span>",
                            "children": [],
                        }
                    ]
                },
            }
        ]

        hits = search_documents(docs, "简历")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["doc_id"], "docA")
        self.assertEqual(hits[0]["node_id"], "n1")
        self.assertEqual(hits[0]["text"], "简历做一下更新")


class ClientSyncParsingTests(unittest.TestCase):
    def test_parse_client_sync_line_extracts_change_request(self):
        line = (
            '[2026-03-17T17:18:40.006] [INFO] clientSync - Info:  Net request 45715 '
            '{"pathname":"/v3/api/colla/events","data":{"memberId":"7992964417993318",'
            '"type":"CHANGE","version":209,"documentId":"doc-demo-01","events":[{"name":"create"}]},'
            '"method":"POST"}'
        )

        parsed = parse_client_sync_line(line)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["timestamp"], "2026-03-17T17:18:40.006")
        self.assertEqual(parsed["kind"], "change_request")
        self.assertEqual(parsed["document_id"], "doc-demo-01")
        self.assertEqual(parsed["event_type"], "CHANGE")
        self.assertEqual(parsed["version"], 209)


class FolderNormalizationTests(unittest.TestCase):
    def test_normalize_folder_record_extracts_parent_children_and_timestamps(self):
        raw = {
            "id": "folder-root-01",
            "|o": "Workspace",
            "|h": "0",
            "|p": '[{"id":"doc-link-001","type":"doc"},{"id":"folder-daily-01","type":"folder"}]',
            "|d": 1753841934779,
            "|n": 1773313495971,
            "|t": 1773313495971,
            "|v": 1773313495971,
            "_rev": "2792-d896b5c6a897c7c7b5e61487029f29ad",
        }

        normalized = normalize_folder_record(raw)
        self.assertEqual(normalized["folder_id"], "folder-root-01")
        self.assertEqual(normalized["name"], "Workspace")
        self.assertEqual(normalized["parent_id"], "0")
        self.assertEqual(normalized["created_at"], 1753841934779)
        self.assertEqual(normalized["updated_at"], 1773313495971)
        self.assertEqual(normalized["children"][0]["id"], "doc-link-001")
        self.assertEqual(normalized["children"][1]["type"], "folder")
