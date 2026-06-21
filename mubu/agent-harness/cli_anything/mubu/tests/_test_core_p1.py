# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class FolderIndexTests(unittest.TestCase):
    def test_build_folder_indexes_creates_by_id_and_folder_paths(self):
        folders = [
            {"folder_id": "root", "name": "Root", "parent_id": "0"},
            {"folder_id": "child", "name": "Child", "parent_id": "root"},
        ]
        by_id, folder_paths = build_folder_indexes(folders)
        self.assertIn("root", by_id)
        self.assertIn("child", by_id)
        self.assertEqual(folder_paths.get("root"), "Root")
        self.assertEqual(folder_paths.get("child"), "Root/Child")


class DailyTitleTests(unittest.TestCase):
    def test_date_range_titles(self):
        self.assertTrue(looks_like_daily_title("26.03.16"))
        self.assertTrue(looks_like_daily_title("26.3.8-3.9"))

    def test_rejects_non_date_titles(self):
        self.assertFalse(looks_like_daily_title("DDL表"))
        self.assertFalse(looks_like_daily_title("模板更新"))

    def test_rejects_template_suffix(self):
        self.assertFalse(looks_like_daily_title("26.2.22模板更新"))


class NormalizationHelperTests(unittest.TestCase):
    def test_parse_child_refs_handles_json_string(self):
        raw = '[{"id":"a","type":"doc"},{"id":"b","type":"folder"}]'
        refs = parse_child_refs(raw)
        self.assertEqual(len(refs), 2)
        self.assertEqual(refs[0]["id"], "a")

    def test_parse_child_refs_handles_list(self):
        refs = parse_child_refs([{"id": "x"}])
        self.assertEqual(refs[0]["id"], "x")

    def test_parse_child_refs_handles_empty(self):
        self.assertEqual(parse_child_refs(None), [])
        self.assertEqual(parse_child_refs(""), [])

    def test_normalized_lookup_key(self):
        self.assertEqual(normalized_lookup_key("Hello World"), "hello world")

    def test_numeric_values_extracts_ints(self):
        raw = {"|e": 100, "|z": "200", "|m": None, "other": "abc"}
        result = numeric_values(raw["|e"], raw["|z"], raw["|m"], raw["other"])
        self.assertEqual(result, [100])

    def test_parse_revision_generation(self):
        self.assertEqual(parse_revision_generation("2792-d896b5c6"), 2792)
        self.assertEqual(parse_revision_generation("invalid"), 0)
        self.assertEqual(parse_revision_generation(None), 0)


class TimestampConversionTests(unittest.TestCase):
    def test_timestamp_ms_to_iso(self):
        result = timestamp_ms_to_iso(1710000000000)
        self.assertIsInstance(result, str)
        # Timezone dependent; just check date is in March 2024
        self.assertIn("2024-03-", result)

    def test_parse_event_timestamp_ms(self):
        result = parse_event_timestamp_ms("2026-03-17T17:18:40.006")
        self.assertIsInstance(result, (int, float))
        self.assertGreater(result, 0)


class DefaultPathDiscoveryTests(unittest.TestCase):
    def test_candidate_appdata_roots_prefers_explicit_environment(self):
        env = {
            "APPDATA": "/tmp/appdata",
            "USERPROFILE": "/tmp/profile",
            "USER": "alice",
        }
        candidates = candidate_appdata_roots(env=env, home=Path("/home/alice"), mount_root=Path("/tmp/users"))
        self.assertEqual(candidates[0], Path("/tmp/appdata"))
        self.assertIn(Path("/tmp/profile/AppData/Roaming"), candidates)
        self.assertIn(Path("/tmp/users/alice/AppData/Roaming"), candidates)

    def test_default_mubu_data_root_uses_first_existing_candidate(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mount_root = Path(tmpdir) / "Users"
            roaming = mount_root / "alice" / "AppData" / "Roaming"
            roaming.mkdir(parents=True)
            root = default_mubu_data_root(env={}, home=Path("/home/alice"), mount_root=mount_root)
            self.assertEqual(root, roaming / "Mubu" / "mubu_app_data" / "mubu_data")


class DedupeLatestRecordsTests(unittest.TestCase):
    def test_keeps_highest_revision(self):
        records = [
            {"id": "a", "_rev": "1-abc"},
            {"id": "a", "_rev": "3-def"},
            {"id": "a", "_rev": "2-ghi"},
            {"id": "b", "_rev": "1-xyz"},
        ]
        result = dedupe_latest_records(records)
        by_id = {r["id"]: r for r in result}
        self.assertEqual(len(result), 2)
        self.assertEqual(by_id["a"]["_rev"], "3-def")


class AmbiguousErrorMessageTests(unittest.TestCase):
    def test_formats_readable_message(self):
        candidates = [
            {"path": "Workspace/Daily tasks"},
            {"path": "Archive/Daily tasks"},
        ]
        msg = ambiguous_error_message("folder", "Daily tasks", candidates, "path")
        self.assertIn("Daily tasks", msg)
        self.assertIn("Workspace", msg)
        self.assertIn("Archive", msg)


class EnrichDocumentMetaTests(unittest.TestCase):
    def test_adds_folder_path(self):
        meta = {"doc_id": "d1", "folder_id": "f1", "title": "Doc"}
        folders = [
            {"folder_id": "root", "name": "Root", "parent_id": "0"},
            {"folder_id": "f1", "name": "Sub", "parent_id": "root"},
        ]
        _, folder_paths = build_folder_indexes(folders)
        enriched = enrich_document_meta(meta, folder_paths)
        self.assertIn("Sub", enriched.get("folder_path", ""))
        self.assertIn("Doc", enriched.get("doc_path", ""))
