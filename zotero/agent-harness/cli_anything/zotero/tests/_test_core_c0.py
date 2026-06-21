# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _ImportCoreTestsMixin0:
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.env = create_sample_environment(Path(self.tmpdir.name))
        self.runtime = discovery.build_runtime_context(
            data_dir=str(self.env["data_dir"]),
            profile_dir=str(self.env["profile_dir"]),
            executable=str(self.env["executable"]),
        )
    def test_enable_local_api_reports_idempotent_state(self):
        payload = imports_mod.enable_local_api(self.runtime)
        self.assertTrue(payload["enabled"])
        self.assertFalse(payload["already_enabled"])
        self.assertTrue(Path(payload["user_js_path"]).exists())

        refreshed = discovery.build_runtime_context(
            data_dir=str(self.env["data_dir"]),
            profile_dir=str(self.env["profile_dir"]),
            executable=str(self.env["executable"]),
        )
        second = imports_mod.enable_local_api(refreshed)
        self.assertTrue(second["already_enabled"])
    def test_import_json_uses_session_collection_and_tags(self):
        json_path = Path(self.tmpdir.name) / "items.json"
        json_path.write_text('[{"itemType": "journalArticle", "title": "Imported"}]', encoding="utf-8")

        with mock.patch.object(self.runtime, "connector_available", True):
            with mock.patch("cli_anything.zotero.utils.zotero_http.connector_save_items") as save_items:
                with mock.patch("cli_anything.zotero.utils.zotero_http.connector_update_session") as update_session:
                    payload = imports_mod.import_json(
                        self.runtime,
                        json_path,
                        tags=["alpha", "beta"],
                        session={"current_collection": "COLLAAAA"},
                    )

        save_items.assert_called_once()
        submitted_items = save_items.call_args.args[1]
        self.assertEqual(submitted_items[0]["title"], "Imported")
        self.assertTrue(submitted_items[0]["id"].startswith("cli-anything-zotero-"))
        update_session.assert_called_once()
        self.assertEqual(update_session.call_args.kwargs["target"], "C1")
        self.assertEqual(update_session.call_args.kwargs["tags"], ["alpha", "beta"])
        self.assertEqual(payload["submitted_count"], 1)
        self.assertEqual(payload["target"]["treeViewID"], "C1")
    def test_import_file_posts_raw_text_and_explicit_tree_view_target(self):
        ris_path = Path(self.tmpdir.name) / "sample.ris"
        ris_path.write_text("TY  - JOUR\nTI  - Imported Title\nER  - \n", encoding="utf-8")

        with mock.patch.object(self.runtime, "connector_available", True):
            with mock.patch("cli_anything.zotero.utils.zotero_http.connector_import_text", return_value=[{"title": "Imported Title"}]) as import_text:
                with mock.patch("cli_anything.zotero.utils.zotero_http.connector_update_session") as update_session:
                    payload = imports_mod.import_file(
                        self.runtime,
                        ris_path,
                        collection_ref="C99",
                        tags=["imported"],
                    )

        import_text.assert_called_once()
        self.assertIn("Imported Title", import_text.call_args.args[1])
        update_session.assert_called_once()
        self.assertEqual(update_session.call_args.kwargs["target"], "C99")
        self.assertEqual(payload["imported_count"], 1)
    def test_import_json_strips_inline_attachments_and_uploads_local_pdf(self):
        pdf_path = Path(self.tmpdir.name) / "inline.pdf"
        pdf_path.write_bytes(sample_pdf_bytes("inline"))
        json_path = Path(self.tmpdir.name) / "items.json"
        json_path.write_text(
            '[{"itemType": "journalArticle", "title": "Imported", "attachments": [{"path": "%s"}]}]' % str(pdf_path).replace("\\", "\\\\"),
            encoding="utf-8",
        )

        with mock.patch.object(self.runtime, "connector_available", True):
            with mock.patch("cli_anything.zotero.utils.zotero_http.connector_save_items") as save_items:
                with mock.patch("cli_anything.zotero.utils.zotero_http.connector_update_session"):
                    with mock.patch("cli_anything.zotero.utils.zotero_http.connector_save_attachment") as save_attachment:
                        payload = imports_mod.import_json(
                            self.runtime,
                            json_path,
                            attachment_timeout=91,
                        )

        submitted_items = save_items.call_args.args[1]
        self.assertNotIn("attachments", submitted_items[0])
        self.assertEqual(payload["attachment_summary"]["created_count"], 1)
        self.assertEqual(payload["status"], "success")
        save_attachment.assert_called_once()
        self.assertEqual(save_attachment.call_args.kwargs["parent_item_id"], submitted_items[0]["id"])
        self.assertEqual(save_attachment.call_args.kwargs["timeout"], 91)
        self.assertTrue(save_attachment.call_args.kwargs["url"].startswith("file:///"))
        self.assertTrue(save_attachment.call_args.kwargs["content"].startswith(b"%PDF-"))
