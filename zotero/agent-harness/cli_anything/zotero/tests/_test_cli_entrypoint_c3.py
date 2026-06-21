# ruff: noqa: F403, F405, E501
from ._test_cli_entrypoint_base import *  # noqa: F403


class _CliEntrypointTestsMixin3:
    def test_import_json_subprocess_with_inline_file_attachment(self):
        pdf_path = Path(self.tmpdir.name) / "inline.pdf"
        pdf_path.write_bytes(sample_pdf_bytes("subprocess-inline"))
        import_path = Path(self.tmpdir.name) / "items-with-attachment.json"
        title = "Imported JSON Attachment"
        import_path.write_text(
            json.dumps(
                [
                    {
                        "itemType": "journalArticle",
                        "title": title,
                        "attachments": [{"path": str(pdf_path)}],
                    }
                ]
            ),
            encoding="utf-8",
        )
        with fake_zotero_http_server(sqlite_path=self.env_paths["sqlite_path"], data_dir=self.env_paths["data_dir"]) as server:
            result = self.run_cli(
                ["--json", "import", "json", str(import_path), "--collection", "COLLAAAA"],
                extra_env={"ZOTERO_HTTP_PORT": str(server["port"])},
            )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"created_count": 1', result.stdout)

        find_result = self.run_cli(["--json", "item", "find", title, "--exact-title"])
        self.assertEqual(find_result.returncode, 0, msg=find_result.stderr)
        imported_items = json.loads(find_result.stdout)
        self.assertTrue(imported_items)
        imported_item_id = str(imported_items[0]["itemID"])

        attachments_result = self.run_cli(["--json", "item", "attachments", imported_item_id])
        self.assertEqual(attachments_result.returncode, 0, msg=attachments_result.stderr)
        attachments = json.loads(attachments_result.stdout)
        self.assertTrue(attachments)
        self.assertTrue(attachments[0].get("resolvedPath", "").endswith(".pdf"))

        file_result = self.run_cli(["--json", "item", "file", imported_item_id])
        self.assertEqual(file_result.returncode, 0, msg=file_result.stderr)
        item_file = json.loads(file_result.stdout)
        self.assertTrue(item_file.get("exists"))
        self.assertTrue(item_file.get("resolvedPath", "").endswith(".pdf"))
    def test_import_json_subprocess_with_url_attachment(self):
        title = "Imported URL Attachment"
        import_path = Path(self.tmpdir.name) / "items-with-url.json"
        with fake_zotero_http_server(sqlite_path=self.env_paths["sqlite_path"], data_dir=self.env_paths["data_dir"]) as server:
            import_path.write_text(
                json.dumps(
                    [
                        {
                            "itemType": "journalArticle",
                            "title": title,
                            "attachments": [{"url": f"http://127.0.0.1:{server['port']}/downloads/sample.pdf"}],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            result = self.run_cli(
                ["--json", "import", "json", str(import_path), "--collection", "COLLAAAA"],
                extra_env={"ZOTERO_HTTP_PORT": str(server["port"])},
            )
            attachment_calls = [entry for entry in server["calls"] if entry["path"].startswith("/connector/saveAttachment")]

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"created_count": 1', result.stdout)
        self.assertEqual(len(attachment_calls), 1)
        self.assertEqual(attachment_calls[0]["metadata"]["url"], f"http://127.0.0.1:{server['port']}/downloads/sample.pdf")
    def test_import_file_subprocess_with_attachment_manifest(self):
        ris_path = Path(self.tmpdir.name) / "manifest-import.ris"
        ris_path.write_text("TY  - JOUR\nTI  - Imported Manifest Attachment\nER  - \n", encoding="utf-8")
        pdf_path = Path(self.tmpdir.name) / "manifest.pdf"
        pdf_path.write_bytes(sample_pdf_bytes("manifest"))
        manifest_path = Path(self.tmpdir.name) / "attachments-manifest.json"
        manifest_path.write_text(
            json.dumps([{"index": 0, "attachments": [{"path": str(pdf_path)}]}]),
            encoding="utf-8",
        )
        with fake_zotero_http_server(sqlite_path=self.env_paths["sqlite_path"], data_dir=self.env_paths["data_dir"]) as server:
            result = self.run_cli(
                [
                    "--json",
                    "import",
                    "file",
                    str(ris_path),
                    "--collection",
                    "COLLAAAA",
                    "--attachments-manifest",
                    str(manifest_path),
                ],
                extra_env={"ZOTERO_HTTP_PORT": str(server["port"])},
            )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"created_count": 1', result.stdout)
