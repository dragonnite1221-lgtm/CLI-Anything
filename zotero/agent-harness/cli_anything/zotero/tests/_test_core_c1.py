# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _ImportCoreTestsMixin1:
    def test_import_json_url_attachment_uses_delay_and_default_timeout(self):
        json_path = Path(self.tmpdir.name) / "items.json"
        with fake_zotero_http_server() as server:
            json_path.write_text(
                json.dumps(
                    [
                        {
                            "itemType": "journalArticle",
                            "title": "Imported URL",
                            "attachments": [
                                {
                                    "url": f"http://127.0.0.1:{server['port']}/downloads/wrong-content-type.pdf",
                                    "delay_ms": 10,
                                }
                            ],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            with mock.patch.object(self.runtime, "connector_available", True):
                with mock.patch("cli_anything.zotero.utils.zotero_http.connector_save_items"):
                    with mock.patch("cli_anything.zotero.utils.zotero_http.connector_update_session"):
                        with mock.patch("cli_anything.zotero.utils.zotero_http.connector_save_attachment") as save_attachment:
                            with mock.patch("cli_anything.zotero.core.imports.time.sleep") as sleep:
                                payload = imports_mod.import_json(
                                    self.runtime,
                                    json_path,
                                    attachment_timeout=47,
                                )

        sleep.assert_called_once_with(0.01)
        save_attachment.assert_called_once()
        self.assertEqual(save_attachment.call_args.kwargs["timeout"], 47)
        self.assertEqual(payload["attachment_summary"]["created_count"], 1)
    def test_import_json_duplicate_inline_attachments_are_skipped(self):
        pdf_path = Path(self.tmpdir.name) / "duplicate.pdf"
        pdf_path.write_bytes(sample_pdf_bytes("duplicate"))
        json_path = Path(self.tmpdir.name) / "items.json"
        json_path.write_text(
            json.dumps(
                [
                    {
                        "itemType": "journalArticle",
                        "title": "Imported Duplicate",
                        "attachments": [
                            {"path": str(pdf_path)},
                            {"path": str(pdf_path)},
                        ],
                    }
                ]
            ),
            encoding="utf-8",
        )

        with mock.patch.object(self.runtime, "connector_available", True):
            with mock.patch("cli_anything.zotero.utils.zotero_http.connector_save_items"):
                with mock.patch("cli_anything.zotero.utils.zotero_http.connector_update_session"):
                    with mock.patch("cli_anything.zotero.utils.zotero_http.connector_save_attachment") as save_attachment:
                        payload = imports_mod.import_json(self.runtime, json_path)

        save_attachment.assert_called_once()
        self.assertEqual(payload["attachment_summary"]["created_count"], 1)
        self.assertEqual(payload["attachment_summary"]["skipped_count"], 1)
        self.assertEqual(payload["attachment_results"][1]["status"], "skipped_duplicate")
    def test_import_json_rejects_invalid_inline_attachment_schema(self):
        json_path = Path(self.tmpdir.name) / "invalid-attachments.json"
        json_path.write_text(
            json.dumps(
                [
                    {
                        "itemType": "journalArticle",
                        "title": "Broken",
                        "attachments": [{"path": "a.pdf", "url": "https://example.com/a.pdf"}],
                    }
                ]
            ),
            encoding="utf-8",
        )
        with mock.patch.object(self.runtime, "connector_available", True):
            with self.assertRaises(RuntimeError):
                imports_mod.import_json(self.runtime, json_path)
