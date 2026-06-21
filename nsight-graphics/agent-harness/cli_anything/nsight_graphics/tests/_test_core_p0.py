# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestOutputAndErrors:
    def test_output_json(self):
        buffer = io.StringIO()
        output_json({"key": "value", "num": 42}, file=buffer)
        payload = json.loads(buffer.getvalue())
        assert payload["key"] == "value"
        assert payload["num"] == 42

    def test_handle_error_debug(self):
        try:
            raise RuntimeError("boom")
        except RuntimeError as exc:
            payload = handle_error(exc, debug=True)
        assert payload["type"] == "RuntimeError"
        assert "traceback" in payload
