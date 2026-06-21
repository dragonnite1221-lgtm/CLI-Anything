# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestStoreCore:
    def test_list_trace_files_includes_ucache_and_live_flag(self, tmp_path):
        from cli_anything.unrealinsights.core.store import list_trace_files

        trace_dir = tmp_path / "Store" / "001"
        trace_dir.mkdir(parents=True)
        trace = trace_dir / "session.ucache"
        trace.write_text("trace", encoding="utf-8")

        result = list_trace_files(str(tmp_path / "Store"), live_window_seconds=3600)
        assert result["trace_count"] == 1
        assert result["traces"][0]["extension"] == ".ucache"
        assert result["traces"][0]["is_live_candidate"] is True

    def test_latest_trace_file(self, tmp_path):
        from cli_anything.unrealinsights.core.store import latest_trace_file

        store = tmp_path / "Store"
        store.mkdir()
        old_trace = store / "old.utrace"
        new_trace = store / "new.utrace"
        old_trace.write_text("old", encoding="utf-8")
        new_trace.write_text("new", encoding="utf-8")
        os.utime(old_trace, (1, 1))

        result = latest_trace_file(str(store))
        assert result["latest"]["path"] == str(new_trace.resolve())

    @patch("cli_anything.unrealinsights.core.store.backend.resolve_trace_server_exe")
    def test_trace_store_info(self, mock_resolve, tmp_path, monkeypatch):
        from cli_anything.unrealinsights.core.store import trace_store_info

        trace_root = tmp_path / "Trace"
        store = trace_root / "Store"
        store.mkdir(parents=True)
        monkeypatch.setenv("UNREAL_TRACE_ROOT", str(trace_root))
        mock_resolve.return_value = {"available": False, "path": None, "error": "missing"}

        result = trace_store_info()
        assert result["store_dir"] == str(store)
        assert result["store_exists"] is True
