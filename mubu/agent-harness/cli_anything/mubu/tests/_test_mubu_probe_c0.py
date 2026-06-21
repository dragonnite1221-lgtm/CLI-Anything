# ruff: noqa: F403, F405, E501
from ._test_mubu_probe_base import *  # noqa: F403


class _WritePathTestsMixin0:
    def test_node_path_to_api_path_expands_child_hops(self):
        self.assertEqual(node_path_to_api_path(("nodes", 3)), ["nodes", 3])
        self.assertEqual(
            node_path_to_api_path(("nodes", 3, 0, 2)),
            ["nodes", 3, "children", 0, "children", 2],
        )
    def test_normalize_user_record_extracts_auth_and_profile_fields(self):
        raw = {
            "id": 16166162,
            "|u": "jwt-token-value",
            "|i": "Example User",
            "|n": "15500000000",
            "|o": "https://document-image.mubu.com/photo/example.jpg",
            "|w": "20270221",
            "|h": 1773649029957,
            "_rev": "1-abc",
        }

        normalized = normalize_user_record(raw)
        self.assertEqual(normalized["user_id"], "16166162")
        self.assertEqual(normalized["token"], "jwt-token-value")
        self.assertEqual(normalized["display_name"], "Example User")
        self.assertEqual(normalized["phone"], "15500000000")
        self.assertEqual(normalized["updated_at"], 1773649029957)
    def test_latest_doc_member_context_picks_most_recent_member_id(self):
        events = [
            {"timestamp": "2026-03-17T17:18:40.006", "document_id": "doc-demo-01", "member_id": "old-member"},
            {"timestamp": "2026-03-17T18:32:48.609", "document_id": "other-doc", "member_id": "ignore-me"},
            {"timestamp": "2026-03-17T18:40:01.000", "document_id": "doc-demo-01", "member_id": "new-member"},
        ]

        context = latest_doc_member_context(events, "doc-demo-01")
        self.assertEqual(context["member_id"], "new-member")
        self.assertEqual(context["last_seen_at"], "2026-03-17T18:40:01.000")
    def test_build_api_headers_matches_desktop_shape(self):
        user = {"user_id": "16166162", "token": "jwt-token-value"}

        headers = build_api_headers(user, platform_version="10.0.26100")
        self.assertEqual(headers["mubu-desktop"], "true")
        self.assertEqual(headers["platform"], "windows")
        self.assertEqual(headers["platform-version"], "10.0.26100")
        self.assertEqual(headers["User-Agent"], "windows Mubu Electron")
        self.assertEqual(headers["userId"], "16166162")
        self.assertEqual(headers["token"], "jwt-token-value")
        self.assertEqual(headers["Content-Type"], "application/json;")
    def test_build_text_update_request_builds_server_side_change_payload(self):
        node = {
            "id": "node-1",
            "text": [{"type": 1, "text": "简历做一下"}],
            "modified": 1773739119771,
        }

        request = build_text_update_request(
            doc_id="doc-demo-01",
            member_id="7992964417993318",
            version=256,
            node=node,
            path=("nodes", 3, "children", 0),
            new_text="简历做一下更新",
            modified_ms=1773744000000,
        )

        self.assertEqual(request["pathname"], "/v3/api/colla/events")
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["data"]["documentId"], "doc-demo-01")
        self.assertEqual(request["data"]["memberId"], "7992964417993318")
        self.assertEqual(request["data"]["version"], 256)
        event = request["data"]["events"][0]
        self.assertEqual(event["name"], "update")
        updated = event["updated"][0]
        self.assertEqual(updated["updated"]["id"], "node-1")
        self.assertEqual(updated["updated"]["text"], "<span>简历做一下更新</span>")
        self.assertEqual(updated["updated"]["modified"], 1773744000000)
        self.assertEqual(updated["original"]["text"], "<span>简历做一下</span>")
        self.assertEqual(updated["path"], ["nodes", 3, "children", 0])
