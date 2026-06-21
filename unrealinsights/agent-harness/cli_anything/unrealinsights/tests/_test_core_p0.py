# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


@pytest.fixture(autouse=True)
def _session_state_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("CLI_ANYTHING_UNREALINSIGHTS_STATE_DIR", str(tmp_path / "state"))


class TestOutputUtils:
    def test_output_json(self):
        import io

        from cli_anything.unrealinsights.utils.output import output_json

        buf = io.StringIO()
        output_json({"ok": True, "value": 42}, file=buf)
        data = json.loads(buf.getvalue())
        assert data["ok"] is True
        assert data["value"] == 42

    def test_output_table_empty(self):
        import io

        from cli_anything.unrealinsights.utils.output import output_table

        buf = io.StringIO()
        output_table([], ["col"], file=buf)
        assert "(no data)" in buf.getvalue()

    def test_format_size(self):
        from cli_anything.unrealinsights.utils.output import format_size

        assert format_size(10) == "10 B"
        assert "KB" in format_size(4096)


class TestErrorUtils:
    def test_handle_error(self):
        from cli_anything.unrealinsights.utils.errors import handle_error

        result = handle_error(ValueError("bad"))
        assert result["error"] == "bad"
        assert result["type"] == "ValueError"


def _make_fake_binary(root: Path, binary_name: str) -> Path:
    target = root / "UE_5.5" / "Engine" / "Binaries" / "Win64" / binary_name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("fake-binary", encoding="utf-8")
    return target
