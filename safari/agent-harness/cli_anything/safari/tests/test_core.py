# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestPlatformCheck:
    def test_refuses_non_darwin(self):
        from cli_anything.safari.utils import safari_backend as backend

        with patch.object(platform, "system", return_value="Linux"):
            available, msg = backend.is_available()
            assert available is False
            assert "macOS" in msg

    def test_accepts_darwin_if_deps_present(self):
        from cli_anything.safari.utils import safari_backend as backend

        with (
            patch.object(platform, "system", return_value="Darwin"),
            patch.object(backend, "_check_npx", return_value=True),
            patch.object(
                backend, "_check_safari_mcp_package", return_value=(True, "2.7.8")
            ),
        ):
            available, msg = backend.is_available()
            assert available is True
            assert "2.7.8" in msg


class TestUnwrap:
    def test_unwrap_json_text(self):
        from cli_anything.safari.utils.safari_backend import _unwrap

        result = MagicMock()
        item = MagicMock()
        item.text = '{"ok": true, "url": "https://example.com"}'
        result.content = [item]

        parsed = _unwrap(result)
        assert parsed == {"ok": True, "url": "https://example.com"}

    def test_unwrap_plain_text(self):
        from cli_anything.safari.utils.safari_backend import _unwrap

        result = MagicMock()
        item = MagicMock()
        item.text = "not json, just a string"
        result.content = [item]

        assert _unwrap(result) == "not json, just a string"

    def test_unwrap_multiple_parts(self):
        from cli_anything.safari.utils.safari_backend import _unwrap

        result = MagicMock()
        a, b = MagicMock(), MagicMock()
        a.text = '{"a": 1}'
        b.text = '{"b": 2}'
        result.content = [a, b]

        parts = _unwrap(result)
        assert parts == [{"a": 1}, {"b": 2}]

    def test_unwrap_empty(self):
        from cli_anything.safari.utils.safari_backend import _unwrap

        result = MagicMock()
        result.content = []
        assert _unwrap(result) is None

    def test_unwrap_image_content(self):
        """ImageContent items must NOT be silently dropped.

        Regression test for the bug where _unwrap only checked for
        ``.text`` and returned None for screenshot tools, which
        return ``{type:'image', data:<base64>, mimeType:...}``.
        """
        from cli_anything.safari.utils.safari_backend import _unwrap

        result = MagicMock()
        item = MagicMock(spec=["data", "mimeType"])
        item.data = "base64encodedimagedata=="
        item.mimeType = "image/jpeg"
        result.content = [item]

        unwrapped = _unwrap(result)
        assert unwrapped is not None
        assert unwrapped["type"] == "image"
        assert unwrapped["data"] == "base64encodedimagedata=="
        assert unwrapped["mimeType"] == "image/jpeg"

    def test_unwrap_image_content_default_mimetype(self):
        from cli_anything.safari.utils.safari_backend import _unwrap

        result = MagicMock()
        item = MagicMock(spec=["data"])
        item.data = "abc"
        # No mimeType attribute
        result.content = [item]

        unwrapped = _unwrap(result)
        assert unwrapped is not None
        assert unwrapped["type"] == "image"
        assert unwrapped["data"] == "abc"
        assert unwrapped["mimeType"] == "application/octet-stream"
