# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class WorkflowCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.env = create_sample_environment(Path(self.tmpdir.name))
        self.runtime = discovery.build_runtime_context(
            data_dir=str(self.env["data_dir"]),
            profile_dir=str(self.env["profile_dir"]),
            executable=str(self.env["executable"]),
        )

    def test_collection_find_and_item_find_sqlite_fallback(self):
        collections = catalog.find_collections(self.runtime, "sample", limit=10)
        self.assertEqual(collections[0]["key"], "COLLAAAA")

        with mock.patch.object(self.runtime, "local_api_available", False):
            items = catalog.find_items(self.runtime, "Sample", limit=10, session={})
        self.assertEqual(items[0]["key"], "REG12345")

        exact = catalog.find_items(self.runtime, "Sample Title", exact_title=True, limit=10, session={})
        self.assertEqual(exact[0]["itemID"], 1)

    def test_collection_scoped_item_find_prefers_local_api(self):
        with mock.patch.object(self.runtime, "local_api_available", True):
            with mock.patch("cli_anything.zotero.utils.zotero_http.local_api_get_json", return_value=[{"key": "REG12345"}]) as local_api:
                items = catalog.find_items(self.runtime, "Sample", collection_ref="COLLAAAA", limit=5, session={})
        local_api.assert_called_once()
        self.assertEqual(items[0]["key"], "REG12345")

    def test_group_library_local_api_scope_and_search_routes(self):
        self.assertEqual(catalog.local_api_scope(self.runtime, 1), "/api/users/0")
        self.assertEqual(catalog.local_api_scope(self.runtime, 2), "/api/groups/2")

        with mock.patch.object(self.runtime, "local_api_available", True):
            with mock.patch("cli_anything.zotero.utils.zotero_http.local_api_get_json", return_value=[{"key": "GROUPKEY"}]) as local_api:
                items = catalog.find_items(
                    self.runtime,
                    "Group",
                    collection_ref="GCOLLAAA",
                    limit=5,
                    session={"current_library": 2},
                )
        self.assertEqual(items[0]["libraryID"], 2)
        self.assertIn("/api/groups/2/collections/GCOLLAAA/items/top", local_api.call_args.args[1])

        with mock.patch.object(self.runtime, "local_api_available", True):
            with mock.patch("cli_anything.zotero.utils.zotero_http.local_api_get_json", return_value=[{"key": "GROUPKEY"}]) as local_api:
                payload = catalog.search_items(self.runtime, "GSEARCHKEY", session={"current_library": 2})
        self.assertEqual(payload[0]["key"], "GROUPKEY")
        self.assertIn("/api/groups/2/searches/GSEARCHKEY/items", local_api.call_args.args[1])

    def test_item_notes_and_note_get(self):
        item_notes = catalog.item_notes(self.runtime, "REG12345")
        self.assertEqual(len(item_notes), 1)
        self.assertEqual(item_notes[0]["notePreview"], "Example note")

        note = notes_mod.get_note(self.runtime, "NOTEKEY")
        self.assertEqual(note["noteText"], "Example note")

    def test_note_add_builds_child_note_payload(self):
        with mock.patch.object(self.runtime, "connector_available", True):
            with mock.patch("cli_anything.zotero.utils.zotero_http.get_selected_collection", return_value={"libraryID": 1}):
                with mock.patch("cli_anything.zotero.utils.zotero_http.connector_save_items") as save_items:
                    payload = notes_mod.add_note(
                        self.runtime,
                        "REG12345",
                        text="# Heading\n\nA **bold** note",
                        fmt="markdown",
                    )
        save_items.assert_called_once()
        submitted = save_items.call_args.args[1][0]
        self.assertEqual(submitted["itemType"], "note")
        self.assertEqual(submitted["parentItem"], "REG12345")
        self.assertIn("<h1>", submitted["note"])
        self.assertEqual(payload["parentItemKey"], "REG12345")

    def test_item_context_aggregates_exports_and_links(self):
        with mock.patch.object(self.runtime, "local_api_available", True):
            with mock.patch("cli_anything.zotero.core.rendering.export_item", side_effect=[{"content": "@article{sample}"}, {"content": '{"id":"sample"}'}]):
                payload = analysis.build_item_context(
                    self.runtime,
                    "REG12345",
                    include_notes=True,
                    include_bibtex=True,
                    include_csljson=True,
                    include_links=True,
                )
        self.assertEqual(payload["links"]["doi_url"], "https://doi.org/10.1000/sample")
        self.assertIn("bibtex", payload["exports"])
        self.assertIn("Notes:", payload["prompt_context"])

    def test_item_analyze_requires_api_key_and_uses_openai(self):
        with mock.patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            with self.assertRaises(RuntimeError):
                analysis.analyze_item(self.runtime, "REG12345", question="Summarize", model="gpt-test")

        with mock.patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}, clear=False):
            with mock.patch("cli_anything.zotero.core.analysis.build_item_context", return_value={"item": {"key": "REG12345"}, "prompt_context": "Title: Sample"}):
                with mock.patch("cli_anything.zotero.utils.openai_api.create_text_response", return_value={"response_id": "resp_123", "answer": "Analysis", "raw": {}}) as create_response:
                    payload = analysis.analyze_item(self.runtime, "REG12345", question="Summarize", model="gpt-test")
        create_response.assert_called_once()
        self.assertEqual(payload["answer"], "Analysis")

    def test_experimental_commands_require_closed_zotero_and_update_db_copy(self):
        with mock.patch.object(self.runtime, "connector_available", True):
            with self.assertRaises(RuntimeError):
                experimental.create_collection(self.runtime, "Blocked")

        with mock.patch.object(self.runtime, "connector_available", False):
            created = experimental.create_collection(self.runtime, "Created")
            self.assertEqual(created["action"], "collection_create")

            added = experimental.add_item_to_collection(self.runtime, "REG12345", "COLLBBBB")
            self.assertEqual(added["action"], "item_add_to_collection")

            moved = experimental.move_item_to_collection(
                self.runtime,
                "REG67890",
                "COLLAAAA",
                from_refs=["COLLBBBB"],
            )
        self.assertEqual(moved["action"], "item_move_to_collection")

    def test_rendering_uses_group_library_local_api_scope(self):
        with mock.patch.object(self.runtime, "local_api_available", True):
            with mock.patch("cli_anything.zotero.utils.zotero_http.local_api_get_text", return_value="TY  - JOUR\nER  - \n") as get_text:
                export_payload = rendering.export_item(self.runtime, "GROUPKEY", "ris", session={"current_library": 2})
        self.assertEqual(export_payload["libraryID"], 2)
        self.assertIn("/api/groups/2/items/GROUPKEY", get_text.call_args.args[1])
