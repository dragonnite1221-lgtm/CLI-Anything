# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestPreviewMixin1:
    def test_live_start_publishes_session(self, tmp_path, monkeypatch):
        session = Session("preview_live")
        session.new_project()
        project_path = tmp_path / "live-demo.mlt"
        session.save_project(str(project_path))
        bundle_manifest = self._fake_bundle(tmp_path / "bundles", "bundle-a")

        def fake_capture(*args, **kwargs):
            return dict(bundle_manifest)

        monkeypatch.setattr(preview_mod, "capture", fake_capture)

        live = preview_mod.live_start(
            session,
            root_dir=str(tmp_path),
            refresh_hint_ms=900,
            live_mode="poll",
            source_poll_ms=420,
        )
        assert live["protocol_version"] == preview_mod.LIVE_PROTOCOL_VERSION
        assert live["current_bundle_id"] == "bundle-a"
        assert live["refresh_hint_ms"] == 900
        assert live["live_mode"] == "poll"
        assert live["source_poll_ms"] == 420
        assert live["source_state"]["project_path"] == str(project_path)
        assert live["source_state"]["last_rendered_fingerprint"].startswith("sha256:")
        assert Path(live["_session_path"]).is_file()
        assert Path(live["_trajectory_path"]).is_file()
        assert (Path(live["_session_dir"]) / "current" / "manifest.json").is_file()
        trajectory = json.loads(Path(live["_trajectory_path"]).read_text(encoding="utf-8"))
        assert trajectory["step_count"] == 1
        assert trajectory["steps"][0]["bundle_id"] == "bundle-a"
        assert live["trajectory_step_count"] == 1
    def test_live_push_updates_history(self, tmp_path, monkeypatch):
        session = Session("preview_live")
        session.new_project()
        project_path = tmp_path / "live-demo.mlt"
        session.save_project(str(project_path))
        bundle_a = self._fake_bundle(tmp_path / "bundles", "bundle-a")
        bundle_b = self._fake_bundle(tmp_path / "bundles", "bundle-b")
        manifests = [dict(bundle_a), dict(bundle_b)]

        def fake_capture(*args, **kwargs):
            return manifests.pop(0)

        monkeypatch.setattr(preview_mod, "capture", fake_capture)

        started = preview_mod.live_start(session, root_dir=str(tmp_path))
        pushed = preview_mod.live_push(session, root_dir=str(tmp_path))
        assert started["current_bundle_id"] == "bundle-a"
        assert pushed["current_bundle_id"] == "bundle-b"
        assert pushed["history"][0]["bundle_id"] == "bundle-b"
        assert pushed["history"][1]["bundle_id"] == "bundle-a"
        trajectory = json.loads(Path(pushed["_trajectory_path"]).read_text(encoding="utf-8"))
        assert trajectory["step_count"] == 2
        assert [step["bundle_id"] for step in trajectory["steps"]] == ["bundle-a", "bundle-b"]
        assert pushed["current_step_id"] == "step-0002"
    def test_live_status_includes_trajectory_summary(self, tmp_path, monkeypatch):
        session = Session("preview_live")
        session.new_project()
        project_path = tmp_path / "live-demo.mlt"
        session.save_project(str(project_path))
        bundle_manifest = self._fake_bundle(tmp_path / "bundles", "bundle-a")

        monkeypatch.setattr(preview_mod, "capture", lambda *args, **kwargs: dict(bundle_manifest))

        preview_mod.live_start(session, root_dir=str(tmp_path), live_mode="manual")
        status = preview_mod.live_status(session, root_dir=str(tmp_path))
        summary = status["trajectory_summary"]
        assert summary["step_count"] == 1
        assert summary["latest_bundle_id"] == "bundle-a"
        assert summary["latest_publish_reason"] == "live-start"
        assert summary["recent_steps"][0]["step_id"] == "step-0001"
    def test_live_push_records_publish_time_when_bundle_is_reused(self, tmp_path, monkeypatch):
        session = Session("preview_live")
        session.new_project()
        project_path = tmp_path / "live-demo.mlt"
        session.save_project(str(project_path))
        bundle_manifest = self._fake_bundle(tmp_path / "bundles", "bundle-a")
        bundle_manifest["created_at"] = "2025-01-01T00:00:00Z"
        publish_times = [
            "2026-04-23T10:00:00Z",
            "2026-04-23T10:05:00Z",
        ]

        monkeypatch.setattr(preview_mod, "capture", lambda *args, **kwargs: dict(bundle_manifest))
        monkeypatch.setattr(preview_mod, "_now_iso", lambda: publish_times.pop(0))

        preview_mod.live_start(session, root_dir=str(tmp_path), live_mode="manual")
        pushed = preview_mod.live_push(session, root_dir=str(tmp_path))
        trajectory = json.loads(Path(pushed["_trajectory_path"]).read_text(encoding="utf-8"))

        assert len(pushed["history"]) == 1
        assert [step["bundle_id"] for step in trajectory["steps"]] == ["bundle-a", "bundle-a"]
        assert [step["command_finished_at"] for step in trajectory["steps"]] == [
            "2026-04-23T10:00:00Z",
            "2026-04-23T10:05:00Z",
        ]
        assert all(step["created_at"] == "2025-01-01T00:00:00Z" for step in trajectory["steps"])
