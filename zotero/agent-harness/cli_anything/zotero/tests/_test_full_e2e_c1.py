# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _ZoteroFullE2EMixin1:
    @unittest.skipUnless(SAMPLE_SEARCH is not None, "No Zotero saved search found")
    def test_search_detail_commands(self):
        assert SAMPLE_SEARCH is not None
        search_get = self.run_cli(["--json", "search", "get", str(SAMPLE_SEARCH["savedSearchID"])])
        self.assertEqual(search_get.returncode, 0, msg=search_get.stderr)
        self.assertIn(SAMPLE_SEARCH["key"], search_get.stdout)

        search_items = self.run_cli(["--json", "search", "items", str(SAMPLE_SEARCH["savedSearchID"])])
        self.assertEqual(search_items.returncode, 0, msg=search_items.stderr)
    @unittest.skipUnless(os.environ.get("CLI_ANYTHING_ZOTERO_ENABLE_WRITE_E2E") == "1", "Write E2E disabled")
    def test_opt_in_write_import_commands(self):
        target = os.environ.get("CLI_ANYTHING_ZOTERO_IMPORT_TARGET", "").strip()
        self.assertTrue(target, "CLI_ANYTHING_ZOTERO_IMPORT_TARGET must be set when write E2E is enabled")

        with tempfile.TemporaryDirectory() as tmpdir:
            ris_path = Path(tmpdir) / "import.ris"
            ris_path.write_text("TY  - JOUR\nTI  - CLI Anything Write E2E RIS\nER  - \n", encoding="utf-8")
            ris_result = self.run_cli(["--json", "import", "file", str(ris_path), "--collection", target, "--tag", "cli-anything-e2e"])
            self.assertEqual(ris_result.returncode, 0, msg=ris_result.stderr)
            self.assertIn('"action": "import_file"', ris_result.stdout)

            json_path = Path(tmpdir) / "import.json"
            json_path.write_text(
                json.dumps([{"itemType": "journalArticle", "title": "CLI Anything Write E2E JSON"}], ensure_ascii=False),
                encoding="utf-8",
            )
            json_result = self.run_cli(["--json", "import", "json", str(json_path), "--collection", target, "--tag", "cli-anything-e2e"])
            self.assertEqual(json_result.returncode, 0, msg=json_result.stderr)
            self.assertIn('"action": "import_json"', json_result.stdout)
    @unittest.skipUnless(os.environ.get("CLI_ANYTHING_ZOTERO_ENABLE_WRITE_E2E") == "1", "Write E2E disabled")
    def test_opt_in_import_json_with_inline_attachment(self):
        target = os.environ.get("CLI_ANYTHING_ZOTERO_IMPORT_TARGET", "").strip()
        self.assertTrue(target, "CLI_ANYTHING_ZOTERO_IMPORT_TARGET must be set when write E2E is enabled")

        with tempfile.TemporaryDirectory() as tmpdir:
            title = f"CLI Anything Attachment E2E {uuid.uuid4().hex[:8]}"
            pdf_path = Path(tmpdir) / "inline-e2e.pdf"
            pdf_path.write_bytes(sample_pdf_bytes("live-e2e"))
            json_path = Path(tmpdir) / "import-attachment.json"
            json_path.write_text(
                json.dumps(
                    [
                        {
                            "itemType": "journalArticle",
                            "title": title,
                            "attachments": [{"path": str(pdf_path)}],
                        }
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            import_result = self.run_cli(
                ["--json", "import", "json", str(json_path), "--collection", target, "--tag", "cli-anything-e2e"]
            )
            self.assertEqual(import_result.returncode, 0, msg=import_result.stderr)
            self.assertIn('"created_count": 1', import_result.stdout)

            find_result = self.run_cli_with_retry(["--json", "item", "find", title, "--exact-title"], retries=4)
            self.assertEqual(find_result.returncode, 0, msg=find_result.stderr)
            imported_items = json.loads(find_result.stdout)
            self.assertTrue(imported_items)
            imported_item_id = str(imported_items[0]["itemID"])

            attachments_result = self.run_cli_with_retry(["--json", "item", "attachments", imported_item_id], retries=4)
            self.assertEqual(attachments_result.returncode, 0, msg=attachments_result.stderr)
            attachments = json.loads(attachments_result.stdout)
            self.assertTrue(attachments)
            self.assertTrue(any((attachment.get("resolvedPath") or "").lower().endswith(".pdf") for attachment in attachments))

            item_file_result = self.run_cli_with_retry(["--json", "item", "file", imported_item_id], retries=4)
            self.assertEqual(item_file_result.returncode, 0, msg=item_file_result.stderr)
            item_file = json.loads(item_file_result.stdout)
            self.assertTrue(item_file.get("exists"))
            self.assertTrue((item_file.get("resolvedPath") or "").lower().endswith(".pdf"))
    @unittest.skipUnless(os.environ.get("CLI_ANYTHING_ZOTERO_ENABLE_WRITE_E2E") == "1", "Write E2E disabled")
    @unittest.skipUnless(SAMPLE_ITEM is not None, "No regular Zotero item found")
    def test_opt_in_note_add_command(self):
        assert SAMPLE_ITEM is not None
        result = self.run_cli(["--json", "note", "add", str(SAMPLE_ITEM["itemID"]), "--text", "CLI Anything write note"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"action": "note_add"', result.stdout)
    @unittest.skipUnless(SAMPLE_ITEM is not None, "No regular Zotero item found for export/citation tests")
    def test_item_citation_bibliography_and_exports(self):
        assert SAMPLE_ITEM is not None
        item_ref = str(SAMPLE_ITEM["itemID"])
        citation = self.run_cli_with_retry(["--json", "item", "citation", item_ref, "--style", "apa", "--locale", "en-US"])
        self.assertEqual(citation.returncode, 0, msg=citation.stderr)
        citation_data = json.loads(citation.stdout)
        self.assertTrue(citation_data.get("citation"))

        bibliography = self.run_cli_with_retry(["--json", "item", "bibliography", item_ref, "--style", "apa", "--locale", "en-US"])
        self.assertEqual(bibliography.returncode, 0, msg=bibliography.stderr)
        bibliography_data = json.loads(bibliography.stdout)
        self.assertTrue(bibliography_data.get("bibliography"))

        ris = self.run_cli_with_retry(["--json", "item", "export", item_ref, "--format", "ris"])
        self.assertEqual(ris.returncode, 0, msg=ris.stderr)
        ris_data = json.loads(ris.stdout)
        self.assertIn("TY  -", ris_data["content"])

        bibtex = self.run_cli_with_retry(["--json", "item", "export", item_ref, "--format", "bibtex"])
        self.assertEqual(bibtex.returncode, 0, msg=bibtex.stderr)
        bibtex_data = json.loads(bibtex.stdout)
        self.assertIn("@", bibtex_data["content"])

        csljson = self.run_cli_with_retry(["--json", "item", "export", item_ref, "--format", "csljson"])
        self.assertEqual(csljson.returncode, 0, msg=csljson.stderr)
        csljson_data = json.loads(csljson.stdout)
        parsed = json.loads(csljson_data["content"])
        self.assertTrue(parsed)
