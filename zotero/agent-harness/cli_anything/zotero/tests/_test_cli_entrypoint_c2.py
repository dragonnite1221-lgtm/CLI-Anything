# ruff: noqa: F403, F405, E501
from ._test_cli_entrypoint_base import *  # noqa: F403


class _CliEntrypointTestsMixin2:
    def test_item_context_and_analyze(self):
        result = self.run_cli(["--json", "item", "context", "REG12345", "--include-notes", "--include-links"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"prompt_context"', result.stdout)
        self.assertIn('"doi_url"', result.stdout)

        with fake_zotero_http_server() as server:
            analyze_result = self.run_cli(
                ["--json", "item", "analyze", "REG12345", "--question", "Summarize", "--model", "gpt-test"],
                extra_env={
                    "OPENAI_API_KEY": "test-key",
                    "CLI_ANYTHING_ZOTERO_OPENAI_URL": f"http://127.0.0.1:{server['port']}/v1/responses",
                },
            )
        self.assertEqual(analyze_result.returncode, 0, msg=analyze_result.stderr)
        self.assertIn('"answer": "Analysis text"', analyze_result.stdout)
    def test_session_status_json(self):
        self.run_cli(["session", "use-item", "REG12345"])
        result = self.run_cli(["--json", "session", "status"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"current_item": "REG12345"', result.stdout)
    def test_session_use_library_normalizes_tree_view_library_ref(self):
        result = self.run_cli(["--json", "session", "use-library", "L2"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"current_library": 2', result.stdout)
    def test_group_library_routes_use_group_scope(self):
        with fake_zotero_http_server() as server:
            extra_env = {"ZOTERO_HTTP_PORT": str(server["port"])}
            use_library = self.run_cli(["--json", "session", "use-library", "L2"], extra_env=extra_env)
            self.assertEqual(use_library.returncode, 0, msg=use_library.stderr)

            find_result = self.run_cli(
                ["--json", "item", "find", "Group", "--collection", "GCOLLAAA"],
                extra_env=extra_env,
            )
            self.assertEqual(find_result.returncode, 0, msg=find_result.stderr)
            self.assertIn("GROUPKEY", find_result.stdout)

            export_result = self.run_cli(["--json", "item", "export", "GROUPKEY", "--format", "ris"], extra_env=extra_env)
            self.assertEqual(export_result.returncode, 0, msg=export_result.stderr)
            self.assertIn("GROUPKEY", export_result.stdout)

            citation_result = self.run_cli(
                ["--json", "item", "citation", "GROUPKEY", "--style", "apa", "--locale", "en-US"],
                extra_env=extra_env,
            )
            self.assertEqual(citation_result.returncode, 0, msg=citation_result.stderr)
            self.assertIn("citation", citation_result.stdout)

            bibliography_result = self.run_cli(
                ["--json", "item", "bibliography", "GROUPKEY", "--style", "apa", "--locale", "en-US"],
                extra_env=extra_env,
            )
            self.assertEqual(bibliography_result.returncode, 0, msg=bibliography_result.stderr)
            self.assertIn("bibliography", bibliography_result.stdout)

            search_result = self.run_cli(["--json", "search", "items", "GSEARCHKEY"], extra_env=extra_env)
            self.assertEqual(search_result.returncode, 0, msg=search_result.stderr)
            self.assertIn("GROUPKEY", search_result.stdout)

        get_paths = [entry["path"] for entry in server["calls"] if entry["method"] == "GET"]
        self.assertTrue(any("/api/groups/2/collections/GCOLLAAA/items/top" in path for path in get_paths))
        self.assertTrue(any("/api/groups/2/items/GROUPKEY?format=ris" in path for path in get_paths))
        self.assertTrue(any("/api/groups/2/items/GROUPKEY?format=json&include=citation" in path for path in get_paths))
        self.assertTrue(any("/api/groups/2/items/GROUPKEY?format=json&include=bib" in path for path in get_paths))
        self.assertTrue(any("/api/groups/2/searches/GSEARCHKEY/items?format=json" in path for path in get_paths))
    def test_import_file_subprocess(self):
        import_path = Path(self.tmpdir.name) / "sample.ris"
        import_path.write_text("TY  - JOUR\nTI  - Imported Sample\nER  - \n", encoding="utf-8")
        with fake_zotero_http_server() as server:
            result = self.run_cli(
                ["--json", "import", "file", str(import_path), "--collection", "COLLAAAA", "--tag", "alpha"],
                extra_env={"ZOTERO_HTTP_PORT": str(server["port"])},
            )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"action": "import_file"', result.stdout)
        self.assertIn('"treeViewID": "C1"', result.stdout)
    def test_import_json_subprocess(self):
        import_path = Path(self.tmpdir.name) / "items.json"
        import_path.write_text('[{"itemType": "journalArticle", "title": "Imported JSON"}]', encoding="utf-8")
        with fake_zotero_http_server() as server:
            result = self.run_cli(
                ["--json", "import", "json", str(import_path), "--collection", "COLLAAAA", "--tag", "beta"],
                extra_env={"ZOTERO_HTTP_PORT": str(server["port"])},
            )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"action": "import_json"', result.stdout)
        self.assertIn('"submitted_count": 1', result.stdout)
