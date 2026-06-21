# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestMailchimpClient(unittest.TestCase):
    def _make_client(self, key: str = "testkey-us1"):
        from cli_anything.mailchimp.core.client import MailchimpClient

        return MailchimpClient(api_key=key)

    def test_base_url(self):
        client = self._make_client("abc-us8")
        assert client._base == "https://us8.api.mailchimp.com/3.0"

    def test_auth_header(self):
        client = self._make_client("abc-us8")
        assert client._session.auth == ("anystring", "abc-us8")

    def test_missing_key_raises_auth_error(self):
        from cli_anything.mailchimp.core.client import MailchimpClient, MailchimpAuthError
        import os

        orig = os.environ.pop("MAILCHIMP_API_KEY", None)
        try:
            with self.assertRaises(MailchimpAuthError):
                MailchimpClient(api_key=None)
        finally:
            if orig:
                os.environ["MAILCHIMP_API_KEY"] = orig

    def test_get_client_exits_on_missing_key(self):
        from cli_anything.mailchimp.core.client import get_client
        import os

        orig = os.environ.pop("MAILCHIMP_API_KEY", None)
        try:
            with self.assertRaises(SystemExit):
                get_client()
        finally:
            if orig:
                os.environ["MAILCHIMP_API_KEY"] = orig

    def test_get_client_exits_cleanly_on_key_without_suffix(self):
        from cli_anything.mailchimp.core.client import get_client
        import os

        orig = os.environ.get("MAILCHIMP_API_KEY")
        os.environ["MAILCHIMP_API_KEY"] = "invalid"
        try:
            with self.assertRaises(SystemExit):
                get_client()
        finally:
            if orig is None:
                os.environ.pop("MAILCHIMP_API_KEY", None)
            else:
                os.environ["MAILCHIMP_API_KEY"] = orig

    @resp_lib.activate
    def test_get_success(self):
        from cli_anything.mailchimp.core.client import MailchimpClient

        client = MailchimpClient(api_key="key-us1")
        resp_lib.add(
            resp_lib.GET,
            "https://us1.api.mailchimp.com/3.0/ping",
            json={"health_status": "Everything's Chimpy!"},
            status=200,
        )
        result = client.get("/ping")
        assert result["health_status"] == "Everything's Chimpy!"

    @resp_lib.activate
    def test_get_error_raises(self):
        from cli_anything.mailchimp.core.client import MailchimpClient, MailchimpError

        client = MailchimpClient(api_key="key-us1")
        resp_lib.add(
            resp_lib.GET,
            "https://us1.api.mailchimp.com/3.0/lists/bad",
            json={"title": "Resource Not Found", "detail": "The requested resource could not be found.", "status": 404},
            status=404,
        )
        with self.assertRaises(MailchimpError) as ctx:
            client.get("/lists/bad")
        assert ctx.exception.status == 404
        assert "Resource Not Found" in ctx.exception.title

    @resp_lib.activate
    def test_post_success(self):
        from cli_anything.mailchimp.core.client import MailchimpClient

        client = MailchimpClient(api_key="key-us1")
        resp_lib.add(
            resp_lib.POST,
            "https://us1.api.mailchimp.com/3.0/lists",
            json={"id": "abc123", "name": "My List"},
            status=200,
        )
        result = client.post("/lists", json={"name": "My List"})
        assert result["id"] == "abc123"

    @resp_lib.activate
    def test_delete_returns_ok(self):
        from cli_anything.mailchimp.core.client import MailchimpClient

        client = MailchimpClient(api_key="key-us1")
        resp_lib.add(
            resp_lib.DELETE,
            "https://us1.api.mailchimp.com/3.0/lists/abc123",
            status=204,
        )
        result = client.delete("/lists/abc123")
        assert result == {"ok": True}

    def test_patch_forwards_query_params(self):
        from cli_anything.mailchimp.core.client import MailchimpClient

        client = MailchimpClient(api_key="key-us1")
        client._session.patch = MagicMock()
        client._session.patch.return_value.ok = True
        client._session.patch.return_value.json.return_value = {"id": "contact-1"}

        result = client.patch(
            "/audiences/audience-1/contacts/contact-1",
            json={"email_address": "user@example.com"},
            params={"data_mode": "sync"},
        )

        assert result == {"id": "contact-1"}
        client._session.patch.assert_called_once_with(
            "https://us1.api.mailchimp.com/3.0/audiences/audience-1/contacts/contact-1",
            json={"email_address": "user@example.com"},
            params={"data_mode": "sync"},
            timeout=30,
        )

    def test_put_forwards_query_params(self):
        from cli_anything.mailchimp.core.client import MailchimpClient

        client = MailchimpClient(api_key="key-us1")
        client._session.put = MagicMock()
        client._session.put.return_value.ok = True
        client._session.put.return_value.json.return_value = {"id": "member-1"}

        result = client.put(
            "/lists/list-1/members/hash-1",
            json={"email_address": "user@example.com"},
            params={"skip_merge_validation": True},
        )

        assert result == {"id": "member-1"}
        client._session.put.assert_called_once_with(
            "https://us1.api.mailchimp.com/3.0/lists/list-1/members/hash-1",
            json={"email_address": "user@example.com"},
            params={"skip_merge_validation": True},
            timeout=30,
        )

    def test_delete_forwards_query_params(self):
        from cli_anything.mailchimp.core.client import MailchimpClient

        client = MailchimpClient(api_key="key-us1")
        client._session.delete = MagicMock()
        client._session.delete.return_value.ok = True

        result = client.delete("/lists/list-1", params={"force": True})

        assert result == {"ok": True}
        client._session.delete.assert_called_once_with(
            "https://us1.api.mailchimp.com/3.0/lists/list-1",
            params={"force": True},
            timeout=30,
        )
