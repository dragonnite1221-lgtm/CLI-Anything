# ruff: noqa: F403, F405, E501
from ._test_mubu_probe_base import *  # noqa: F403


class DocumentMetaNormalizationTests(unittest.TestCase):
    def test_normalize_document_meta_record_extracts_folder_title_and_times(self):
        raw = {
            "id": "1kapleatfQ0",
            "|h": "folder-daily-01",
            "|n": "11.24",
            "|e": 1763865805160,
            "|z": 1764003928841,
            "|B": 1764003934105,
            "|m": 1764003934105,
            "|j": 48,
            "|d": "NewSyncApp",
            "_rev": "915-ca5340b309a22ea63f8990f806765fbc",
        }

        normalized = normalize_document_meta_record(raw)
        self.assertEqual(normalized["doc_id"], "1kapleatfQ0")
        self.assertEqual(normalized["folder_id"], "folder-daily-01")
        self.assertEqual(normalized["title"], "11.24")
        self.assertEqual(normalized["created_at"], 1763865805160)
        self.assertEqual(normalized["updated_at"], 1764003934105)
        self.assertEqual(normalized["word_count"], 48)
        self.assertEqual(normalized["source"], "NewSyncApp")


class LinkExtractionTests(unittest.TestCase):
    def test_extract_doc_links_finds_mubu_doc_mentions(self):
        markup = (
            '<span>参考</span>'
            '<a class="mention mm-iconfont" href="https://mubu.com/docdoc-link-001" '
            'data-token="doc-link-001">DDL表(To Do List)</a>'
        )

        links = extract_doc_links(markup)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["target_doc_id"], "doc-link-001")
        self.assertEqual(links[0]["label"], "DDL表(To Do List)")
