# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class SQLiteInspectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.env = create_sample_environment(Path(self.tmpdir.name))

    def test_fetch_libraries(self):
        libraries = zotero_sqlite.fetch_libraries(self.env["sqlite_path"])
        self.assertEqual(len(libraries), 2)
        self.assertEqual([entry["type"] for entry in libraries], ["user", "group"])

    def test_fetch_collections_and_tree(self):
        collections = zotero_sqlite.fetch_collections(self.env["sqlite_path"], library_id=1)
        self.assertIn("Sample Collection", [entry["collectionName"] for entry in collections])
        tree = zotero_sqlite.build_collection_tree(collections)
        self.assertIn("Sample Collection", [entry["collectionName"] for entry in tree])

    def test_resolve_item_includes_fields_creators_tags(self):
        item = zotero_sqlite.resolve_item(self.env["sqlite_path"], "REG12345")
        self.assertEqual(item["title"], "Sample Title")
        self.assertEqual(item["fields"]["title"], "Sample Title")
        self.assertEqual(item["creators"][0]["lastName"], "Lovelace")
        self.assertEqual(item["tags"][0]["name"], "sample-tag")

    def test_fetch_item_children_and_attachments(self):
        children = zotero_sqlite.fetch_item_children(self.env["sqlite_path"], "REG12345")
        self.assertEqual(len(children), 2)
        attachments = zotero_sqlite.fetch_item_attachments(self.env["sqlite_path"], "REG12345")
        self.assertEqual(len(attachments), 1)
        resolved = zotero_sqlite.resolve_attachment_real_path(attachments[0], self.env["data_dir"])
        self.assertTrue(str(resolved).endswith("paper.pdf"))

        linked_attachments = zotero_sqlite.fetch_item_attachments(self.env["sqlite_path"], "REG67890")
        self.assertEqual(len(linked_attachments), 1)
        linked_resolved = zotero_sqlite.resolve_attachment_real_path(linked_attachments[0], self.env["data_dir"])
        self.assertEqual(linked_resolved, "C:\\Users\\Public\\linked.pdf")

    def test_duplicate_key_resolution_requires_library_context(self):
        with self.assertRaises(zotero_sqlite.AmbiguousReferenceError):
            zotero_sqlite.resolve_item(self.env["sqlite_path"], "DUPITEM1")
        with self.assertRaises(zotero_sqlite.AmbiguousReferenceError):
            zotero_sqlite.resolve_collection(self.env["sqlite_path"], "DUPCOLL1")
        with self.assertRaises(zotero_sqlite.AmbiguousReferenceError):
            zotero_sqlite.resolve_saved_search(self.env["sqlite_path"], "DUPSEARCH")

        user_item = zotero_sqlite.resolve_item(self.env["sqlite_path"], "DUPITEM1", library_id=1)
        group_item = zotero_sqlite.resolve_item(self.env["sqlite_path"], "DUPITEM1", library_id=2)
        self.assertEqual(user_item["title"], "User Duplicate Title")
        self.assertEqual(group_item["title"], "Group Duplicate Title")

        group_collection = zotero_sqlite.resolve_collection(self.env["sqlite_path"], "DUPCOLL1", library_id=2)
        self.assertEqual(group_collection["collectionName"], "Group Duplicate Collection")

        group_search = zotero_sqlite.resolve_saved_search(self.env["sqlite_path"], "DUPSEARCH", library_id=2)
        self.assertEqual(group_search["savedSearchName"], "Group Duplicate Search")

    def test_cross_library_unique_key_still_resolves_without_session_context(self):
        group_item = zotero_sqlite.resolve_item(self.env["sqlite_path"], "GROUPKEY")
        self.assertEqual(group_item["libraryID"], 2)
        group_collection = zotero_sqlite.resolve_collection(self.env["sqlite_path"], "GCOLLAAA")
        self.assertEqual(group_collection["libraryID"], 2)

    def test_fetch_saved_searches_and_tags(self):
        searches = zotero_sqlite.fetch_saved_searches(self.env["sqlite_path"], library_id=1)
        self.assertEqual(searches[0]["savedSearchName"], "Important")
        tags = zotero_sqlite.fetch_tags(self.env["sqlite_path"], library_id=1)
        self.assertEqual(tags[0]["name"], "sample-tag")
        items = zotero_sqlite.fetch_tag_items(self.env["sqlite_path"], "sample-tag", library_id=1)
        self.assertGreaterEqual(len(items), 1)

    def test_find_collections_and_items_and_notes(self):
        collections = zotero_sqlite.find_collections(self.env["sqlite_path"], "collection", library_id=1, limit=10)
        self.assertGreaterEqual(len(collections), 2)
        self.assertIn("Archive Collection", [entry["collectionName"] for entry in collections])

        fuzzy_items = zotero_sqlite.find_items_by_title(self.env["sqlite_path"], "Sample", library_id=1, limit=10)
        self.assertEqual(fuzzy_items[0]["key"], "REG12345")
        exact_items = zotero_sqlite.find_items_by_title(self.env["sqlite_path"], "Sample Title", library_id=1, exact_title=True, limit=10)
        self.assertEqual(exact_items[0]["itemID"], 1)

        notes = zotero_sqlite.fetch_item_notes(self.env["sqlite_path"], "REG12345")
        self.assertEqual(notes[0]["typeName"], "note")
        self.assertEqual(notes[0]["noteText"], "Example note")

    def test_experimental_sqlite_write_helpers(self):
        created = zotero_sqlite.create_collection_record(self.env["sqlite_path"], name="Created Here", library_id=1, parent_collection_id=1)
        self.assertEqual(created["collectionName"], "Created Here")
        self.assertTrue(Path(created["backupPath"]).exists())

        added = zotero_sqlite.add_item_to_collection_record(self.env["sqlite_path"], item_id=1, collection_id=2)
        self.assertTrue(Path(added["backupPath"]).exists())

        moved = zotero_sqlite.move_item_between_collections_record(
            self.env["sqlite_path"],
            item_id=4,
            target_collection_id=1,
            source_collection_ids=[2],
        )
        self.assertTrue(Path(moved["backupPath"]).exists())
        memberships = zotero_sqlite.fetch_item_collections(self.env["sqlite_path"], 4)
        self.assertEqual([membership["collectionID"] for membership in memberships], [1])
