# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _ImportCoreTestsMixin2:
    def test_import_file_manifest_partial_success_records_attachment_failures(self):
        ris_path = Path(self.tmpdir.name) / "sample.ris"
        ris_path.write_text("TY  - JOUR\nTI  - Imported Title\nER  - \n", encoding="utf-8")
        pdf_path = Path(self.tmpdir.name) / "manifest.pdf"
        pdf_path.write_bytes(sample_pdf_bytes("manifest"))
        manifest_path = Path(self.tmpdir.name) / "attachments.json"
        manifest_path.write_text(
            json.dumps(
                [
                    {
                        "index": 0,
                        "attachments": [
                            {"path": str(pdf_path)},
                            {"path": str(Path(self.tmpdir.name) / "missing.pdf")},
                        ],
                    }
                ]
            ),
            encoding="utf-8",
        )

        with mock.patch.object(self.runtime, "connector_available", True):
            with mock.patch(
                "cli_anything.zotero.utils.zotero_http.connector_import_text",
                return_value=[{"id": "imported-1", "title": "Imported Title"}],
            ):
                with mock.patch("cli_anything.zotero.utils.zotero_http.connector_update_session"):
                    with mock.patch("cli_anything.zotero.utils.zotero_http.connector_save_attachment") as save_attachment:
                        payload = imports_mod.import_file(
                            self.runtime,
                            ris_path,
                            attachments_manifest=manifest_path,
                        )

        save_attachment.assert_called_once()
        self.assertEqual(payload["status"], "partial_success")
        self.assertEqual(payload["attachment_summary"]["created_count"], 1)
        self.assertEqual(payload["attachment_summary"]["failed_count"], 1)
        self.assertIn("Attachment file not found", payload["attachment_results"][1]["error"])
    def test_import_file_manifest_title_mismatch_marks_attachment_failure(self):
        ris_path = Path(self.tmpdir.name) / "sample.ris"
        ris_path.write_text("TY  - JOUR\nTI  - Imported Title\nER  - \n", encoding="utf-8")
        pdf_path = Path(self.tmpdir.name) / "manifest.pdf"
        pdf_path.write_bytes(sample_pdf_bytes("manifest"))
        manifest_path = Path(self.tmpdir.name) / "attachments.json"
        manifest_path.write_text(
            json.dumps(
                [
                    {
                        "index": 0,
                        "expected_title": "Different Title",
                        "attachments": [{"path": str(pdf_path)}],
                    }
                ]
            ),
            encoding="utf-8",
        )

        with mock.patch.object(self.runtime, "connector_available", True):
            with mock.patch(
                "cli_anything.zotero.utils.zotero_http.connector_import_text",
                return_value=[{"id": "imported-1", "title": "Imported Title"}],
            ):
                with mock.patch("cli_anything.zotero.utils.zotero_http.connector_update_session"):
                    with mock.patch("cli_anything.zotero.utils.zotero_http.connector_save_attachment") as save_attachment:
                        payload = imports_mod.import_file(
                            self.runtime,
                            ris_path,
                            attachments_manifest=manifest_path,
                        )

        save_attachment.assert_not_called()
        self.assertEqual(payload["status"], "partial_success")
        self.assertIn("title mismatch", payload["attachment_results"][0]["error"])
    def test_import_file_manifest_index_out_of_range_and_missing_connector_id_fail_cleanly(self):
        ris_path = Path(self.tmpdir.name) / "sample.ris"
        ris_path.write_text("TY  - JOUR\nTI  - Imported Title\nER  - \n", encoding="utf-8")
        pdf_path = Path(self.tmpdir.name) / "manifest.pdf"
        pdf_path.write_bytes(sample_pdf_bytes("manifest"))
        manifest_path = Path(self.tmpdir.name) / "attachments.json"
        manifest_path.write_text(
            json.dumps(
                [
                    {"index": 1, "attachments": [{"path": str(pdf_path)}]},
                    {"index": 0, "attachments": [{"path": str(pdf_path)}]},
                ]
            ),
            encoding="utf-8",
        )

        with mock.patch.object(self.runtime, "connector_available", True):
            with mock.patch(
                "cli_anything.zotero.utils.zotero_http.connector_import_text",
                return_value=[{"title": "Imported Title"}],
            ):
                with mock.patch("cli_anything.zotero.utils.zotero_http.connector_update_session"):
                    with mock.patch("cli_anything.zotero.utils.zotero_http.connector_save_attachment") as save_attachment:
                        payload = imports_mod.import_file(
                            self.runtime,
                            ris_path,
                            attachments_manifest=manifest_path,
                        )

        save_attachment.assert_not_called()
        self.assertEqual(payload["attachment_summary"]["failed_count"], 2)
        self.assertIn("index 1", payload["attachment_results"][0]["error"])
        self.assertIn("did not include a connector id", payload["attachment_results"][1]["error"])
