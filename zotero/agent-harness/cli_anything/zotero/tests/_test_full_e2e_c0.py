# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import resolve_cli, uses_module_fallback  # noqa: F401,E501


class _ZoteroFullE2EMixin0:
    CLI_BASE = resolve_cli()
    @classmethod
    def setUpClass(cls) -> None:
        discovery.ensure_live_api_enabled()
        runtime = discovery.build_runtime_context()
        if not runtime.connector_available:
            discovery.launch_zotero(runtime, wait_timeout=45)
        cls.runtime = discovery.build_runtime_context()
    def run_cli(self, args):
        env = os.environ.copy()
        if uses_module_fallback(self.CLI_BASE):
            env["PYTHONPATH"] = str(REPO_ROOT / "zotero" / "agent-harness") + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.run(self.CLI_BASE + args, capture_output=True, text=True, env=env, timeout=60)
    def run_cli_with_retry(self, args, retries: int = 2):
        last = None
        for _ in range(retries):
            last = self.run_cli(args)
            if last.returncode == 0:
                return last
        return last
    def test_sqlite_inventory_commands(self):
        result = self.run_cli(["--json", "collection", "list"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("collectionName", result.stdout)

        result = self.run_cli(["--json", "item", "list"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("itemID", result.stdout)

        result = self.run_cli(["--json", "style", "list"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("title", result.stdout)

        result = self.run_cli(["--json", "search", "list"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
    @unittest.skipUnless(SAMPLE_ITEM is not None, "No regular Zotero item found")
    def test_item_find_and_context_commands(self):
        assert SAMPLE_ITEM is not None
        title = zotero_sqlite.resolve_item(ENVIRONMENT.sqlite_path, SAMPLE_ITEM["itemID"])["title"]
        query = title.split()[0]

        item_find = self.run_cli(["--json", "item", "find", query, "--limit", "5"])
        self.assertEqual(item_find.returncode, 0, msg=item_find.stderr)
        self.assertIn(SAMPLE_ITEM["key"], item_find.stdout)

        exact_find = self.run_cli(["--json", "item", "find", title, "--exact-title"])
        self.assertEqual(exact_find.returncode, 0, msg=exact_find.stderr)
        self.assertIn(SAMPLE_ITEM["key"], exact_find.stdout)

        context_result = self.run_cli(["--json", "item", "context", str(SAMPLE_ITEM["itemID"]), "--include-links"])
        self.assertEqual(context_result.returncode, 0, msg=context_result.stderr)
        self.assertIn('"prompt_context"', context_result.stdout)
    @unittest.skipUnless(ATTACHMENT_SAMPLE_ITEM is not None, "No Zotero item with attachments found")
    def test_attachment_inventory_commands(self):
        assert ATTACHMENT_SAMPLE_ITEM is not None
        attachments = self.run_cli(["--json", "item", "attachments", str(ATTACHMENT_SAMPLE_ITEM["itemID"])])
        self.assertEqual(attachments.returncode, 0, msg=attachments.stderr)
        attachment_data = json.loads(attachments.stdout)
        self.assertTrue(attachment_data)
        self.assertTrue(attachment_data[0].get("resolvedPath"))

        item_file = self.run_cli(["--json", "item", "file", str(ATTACHMENT_SAMPLE_ITEM["itemID"])])
        self.assertEqual(item_file.returncode, 0, msg=item_file.stderr)
        item_file_data = json.loads(item_file.stdout)
        self.assertTrue(item_file_data.get("exists"))
        self.assertTrue(item_file_data.get("resolvedPath"))
    @unittest.skipUnless(NOTE_SAMPLE_ITEM is not None, "No Zotero item with notes found")
    def test_note_inventory_commands(self):
        assert NOTE_SAMPLE_ITEM is not None
        item_notes = self.run_cli(["--json", "item", "notes", str(NOTE_SAMPLE_ITEM["itemID"])])
        self.assertEqual(item_notes.returncode, 0, msg=item_notes.stderr)
        item_notes_data = json.loads(item_notes.stdout)
        self.assertTrue(item_notes_data)
        note_key = item_notes_data[0]["key"]

        note_get = self.run_cli(["--json", "note", "get", note_key])
        self.assertEqual(note_get.returncode, 0, msg=note_get.stderr)
        self.assertIn(note_key, note_get.stdout)
    def test_connector_ping(self):
        result = self.run_cli(["--json", "app", "ping"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"connector_available": true', result.stdout)
    def test_collection_use_selected(self):
        result = self.run_cli(["--json", "collection", "use-selected"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("libraryID", result.stdout)
    @unittest.skipUnless(SAMPLE_COLLECTION is not None, "No Zotero collection found")
    def test_collection_detail_commands(self):
        collection_key = SAMPLE_COLLECTION["key"]

        tree = self.run_cli(["--json", "collection", "tree"])
        self.assertEqual(tree.returncode, 0, msg=tree.stderr)
        self.assertIn("children", tree.stdout)

        collection_get = self.run_cli(["--json", "collection", "get", collection_key])
        self.assertEqual(collection_get.returncode, 0, msg=collection_get.stderr)
        self.assertIn(collection_key, collection_get.stdout)

        collection_items = self.run_cli(["--json", "collection", "items", collection_key])
        self.assertEqual(collection_items.returncode, 0, msg=collection_items.stderr)
    @unittest.skipUnless(SAMPLE_TAG is not None, "No Zotero tag found")
    def test_tag_and_session_commands(self):
        tag_items = self.run_cli(["--json", "tag", "items", SAMPLE_TAG])
        self.assertEqual(tag_items.returncode, 0, msg=tag_items.stderr)
        self.assertIn("itemID", tag_items.stdout)

        if SAMPLE_COLLECTION is not None:
            session_collection = self.run_cli(["--json", "session", "use-collection", SAMPLE_COLLECTION["key"]])
            self.assertEqual(session_collection.returncode, 0, msg=session_collection.stderr)
            self.assertIn('"current_collection"', session_collection.stdout)

        if SAMPLE_ITEM is not None:
            session_item = self.run_cli(["--json", "session", "use-item", str(SAMPLE_ITEM["itemID"])])
            self.assertEqual(session_item.returncode, 0, msg=session_item.stderr)
            self.assertIn(f'"current_item": "{SAMPLE_ITEM["itemID"]}"', session_item.stdout)
