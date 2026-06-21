# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestOutputUtils:
    def test_output_json(self):
        from cli_anything.renderdoc.utils.output import output_json
        import io

        buf = io.StringIO()
        output_json({"key": "value", "num": 42}, file=buf)
        result = json.loads(buf.getvalue())
        assert result["key"] == "value"
        assert result["num"] == 42

    def test_output_table(self):
        from cli_anything.renderdoc.utils.output import output_table
        import io

        buf = io.StringIO()
        output_table(
            [["Alice", 30], ["Bob", 25]],
            ["Name", "Age"],
            file=buf,
        )
        text = buf.getvalue()
        assert "Alice" in text
        assert "Bob" in text
        assert "Name" in text

    def test_output_table_empty(self):
        from cli_anything.renderdoc.utils.output import output_table
        import io

        buf = io.StringIO()
        output_table([], ["Name"], file=buf)
        assert "(no data)" in buf.getvalue()

    def test_format_size(self):
        from cli_anything.renderdoc.utils.output import format_size

        assert format_size(512) == "512 B"
        assert "KB" in format_size(2048)
        assert "MB" in format_size(2 * 1024 * 1024)
        assert "GB" in format_size(3 * 1024 * 1024 * 1024)


class TestErrorUtils:
    def test_handle_error(self):
        from cli_anything.renderdoc.utils.errors import handle_error

        result = handle_error(ValueError("test error"))
        assert result["error"] == "test error"
        assert result["type"] == "ValueError"
        assert "traceback" not in result

    def test_handle_error_debug(self):
        from cli_anything.renderdoc.utils.errors import handle_error

        try:
            raise RuntimeError("boom")
        except RuntimeError as e:
            result = handle_error(e, debug=True)
        assert "traceback" in result
        assert "boom" in result["traceback"]
