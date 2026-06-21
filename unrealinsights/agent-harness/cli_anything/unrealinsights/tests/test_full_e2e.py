# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestCLISmoke:
    CLI_BASE = _resolve_cli("cli-anything-unrealinsights")

    def _run(self, args, check=True, timeout=180):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout,
            env=_cli_env(),
        )

    @skip_no_local_ue
    def test_backend_info(self):
        result = self._run(["--json", "backend", "info"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["insights"]["available"] is True
        assert data["insights"]["path"].lower().endswith("unrealinsights.exe")

    def test_store_list_latest_smoke(self, tmp_path, monkeypatch):
        store = tmp_path / "Store" / "001"
        store.mkdir(parents=True)
        trace = store / "session.utrace"
        trace.write_text("trace", encoding="utf-8")
        monkeypatch.setenv("UNREAL_TRACE_STORE_DIR", str(tmp_path / "Store"))

        result = self._run(["--json", "store", "list"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["trace_count"] == 1

        latest = self._run(["--json", "store", "latest", "--set-current"])
        latest_data = json.loads(latest.stdout)
        assert latest_data["latest"]["path"] == str(trace.resolve())

    def test_gui_status_smoke(self):
        result = self._run(["--json", "gui", "status"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "running" in data
        assert "processes" in data

    def test_live_backend_unavailable_smoke(self, monkeypatch):
        monkeypatch.delenv("UNREALINSIGHTS_LIVE_EXEC", raising=False)
        result = self._run(
            ["--json", "live", "exec", "--pid", "1234", "Trace.Status"], check=False
        )
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "Live control backend unavailable" in data["error"]

    def test_analyze_summary_skip_export_smoke(self, tmp_path):
        (tmp_path / "timer_stats.csv").write_text(
            "Timer Name,Thread,Total Time\nTick,GameThread,1.0\n",
            encoding="utf-8",
        )
        result = self._run(
            ["--json", "analyze", "summary", "--skip-export", "--out", str(tmp_path)]
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["summary"]["top_timers"][0]["name"] == "Tick"
