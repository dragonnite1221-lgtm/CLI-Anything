# ruff: noqa: F403, F405, E501
from ._test_cli_entrypoint_base import *  # noqa: F403


class _CliEntrypointTestsMixin4:
    def test_import_json_subprocess_partial_success_returns_nonzero(self):
        pdf_path = Path(self.tmpdir.name) / "partial.pdf"
        pdf_path.write_bytes(sample_pdf_bytes("partial"))
        missing_path = Path(self.tmpdir.name) / "missing.pdf"
        import_path = Path(self.tmpdir.name) / "partial-items.json"
        import_path.write_text(
            json.dumps(
                [
                    {
                        "itemType": "journalArticle",
                        "title": "Imported Partial",
                        "attachments": [
                            {"path": str(pdf_path)},
                            {"path": str(missing_path)},
                        ],
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
        self.assertEqual(result.returncode, 1, msg=result.stderr)
        self.assertIn('"status": "partial_success"', result.stdout)
        self.assertIn('"failed_count": 1', result.stdout)
    def test_import_json_subprocess_duplicate_attachment_is_idempotent(self):
        pdf_path = Path(self.tmpdir.name) / "duplicate.pdf"
        pdf_path.write_bytes(sample_pdf_bytes("duplicate"))
        import_path = Path(self.tmpdir.name) / "duplicate-items.json"
        import_path.write_text(
            json.dumps(
                [
                    {
                        "itemType": "journalArticle",
                        "title": "Imported Duplicate Attachment",
                        "attachments": [{"path": str(pdf_path)}, {"path": str(pdf_path)}],
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
            attachment_calls = [entry for entry in server["calls"] if entry["path"].startswith("/connector/saveAttachment")]
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"skipped_count": 1', result.stdout)
        self.assertEqual(len(attachment_calls), 1)
    def test_experimental_collection_write_commands(self):
        create = self.run_cli(["--json", "collection", "create", "Created By CLI", "--experimental"])
        self.assertEqual(create.returncode, 0, msg=create.stderr)
        self.assertIn('"action": "collection_create"', create.stdout)

        add = self.run_cli(["--json", "item", "add-to-collection", "REG12345", "COLLBBBB", "--experimental"])
        self.assertEqual(add.returncode, 0, msg=add.stderr)
        self.assertIn('"action": "item_add_to_collection"', add.stdout)

        move = self.run_cli(
            [
                "--json",
                "item",
                "move-to-collection",
                "REG67890",
                "COLLAAAA",
                "--from",
                "COLLBBBB",
                "--experimental",
            ]
        )
        self.assertEqual(move.returncode, 0, msg=move.stderr)
        self.assertIn('"action": "item_move_to_collection"', move.stdout)
