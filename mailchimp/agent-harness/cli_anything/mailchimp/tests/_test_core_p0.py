# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestServerPrefix(unittest.TestCase):
    def test_extracts_suffix(self):
        from cli_anything.mailchimp.core.client import _server_prefix

        assert _server_prefix("abc123-us8") == "us8"
        assert _server_prefix("xyz-eu2") == "eu2"

    def test_missing_suffix_raises(self):
        from cli_anything.mailchimp.core.client import _server_prefix

        with self.assertRaises(ValueError):
            _server_prefix("nodashinkey")


class TestSubscriberHash(unittest.TestCase):
    def test_md5_lowercased(self):
        from cli_anything.mailchimp.core.client import subscriber_hash

        # Known MD5 of "test@example.com"
        assert subscriber_hash("test@example.com") == "55502f40dc8b7c769880b10874abc9d0"
        # Should normalise to lowercase before hashing
        assert subscriber_hash("TEST@EXAMPLE.COM") == subscriber_hash("test@example.com")

    def test_strips_whitespace(self):
        from cli_anything.mailchimp.core.client import subscriber_hash

        assert subscriber_hash("  test@example.com  ") == subscriber_hash("test@example.com")
