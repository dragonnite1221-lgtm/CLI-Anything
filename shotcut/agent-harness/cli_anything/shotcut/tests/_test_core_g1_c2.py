# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestPreviewMixin2:
    def test_live_stop_marks_session_stopped(self, tmp_path, monkeypatch):
        session = Session("preview_live")
        session.new_project()
        project_path = tmp_path / "live-demo.mlt"
        session.save_project(str(project_path))
        bundle_manifest = self._fake_bundle(tmp_path / "bundles", "bundle-a")

        def fake_capture(*args, **kwargs):
            return dict(bundle_manifest)

        monkeypatch.setattr(preview_mod, "capture", fake_capture)

        preview_mod.live_start(session, root_dir=str(tmp_path))
        stopped = preview_mod.live_stop(session, root_dir=str(tmp_path))
        assert stopped["status"] == "stopped"
        assert "stopped_at" in stopped
    def test_live_session_name_is_stable_for_same_project_path(self, tmp_path):
        project_path = tmp_path / "stable-demo.mlt"

        session_a = Session("session-a")
        session_a.new_project()
        session_a.save_project(str(project_path))

        session_b = Session("session-b")
        session_b.open_project(str(project_path))

        name_a = preview_mod._live_session_name(session_a, "quick")
        name_b = preview_mod._live_session_name(session_b, "quick")
        assert name_a == name_b
    def test_project_fingerprint_is_stable_across_sessions_for_saved_project(self, tmp_path):
        project_path = tmp_path / "stable-project.mlt"

        session_a = Session("session-a")
        session_a.new_project()
        session_a.save_project(str(project_path))

        session_b = Session("session-b")
        session_b.open_project(str(project_path))

        assert preview_mod._project_fingerprint(session_a) == preview_mod._project_fingerprint(session_b)
    def test_poll_live_session_once_captures_after_source_change(self, tmp_path, monkeypatch):
        session = Session("preview_live")
        session.new_project()
        project_path = tmp_path / "poll-demo.mlt"
        session.save_project(str(project_path))
        bundle_a = self._fake_bundle(tmp_path / "bundles", "bundle-a")
        bundle_b = self._fake_bundle(tmp_path / "bundles", "bundle-b")
        manifests = [dict(bundle_a), dict(bundle_b)]
        calls = []

        def fake_capture(*args, **kwargs):
            calls.append(kwargs.get("command"))
            return manifests.pop(0)

        monkeypatch.setattr(preview_mod, "capture", fake_capture)

        started = preview_mod.live_start(
            session,
            root_dir=str(tmp_path),
            live_mode="poll",
            source_poll_ms=preview_mod.MIN_SOURCE_POLL_MS,
        )
        started_session_dir = Path(started["_session_dir"])
        session_payload = json.loads(Path(started["_session_path"]).read_text())
        session_payload["source_state"]["last_rendered_fingerprint"] = "sha256:stale"
        Path(started["_session_path"]).write_text(json.dumps(session_payload, indent=2))

        result = preview_mod.poll_live_session_once(str(started_session_dir))
        refreshed = json.loads(Path(started["_session_path"]).read_text())
        trajectory = json.loads(Path(started["_session_dir"]).joinpath("trajectory.json").read_text())
        assert result["action"] == "captured"
        assert refreshed["current_bundle_id"] == "bundle-b"
        assert refreshed["source_state"]["last_rendered_fingerprint"].startswith("sha256:")
        assert refreshed["poller"]["last_capture_status"] == "ok"
        assert calls
        assert trajectory["step_count"] == 2
        assert trajectory["steps"][-1]["publish_reason"] == "auto-poll"
    def test_poll_live_session_once_exits_for_manual_mode(self, tmp_path, monkeypatch):
        session = Session("preview_live")
        session.new_project()
        project_path = tmp_path / "manual-demo.mlt"
        session.save_project(str(project_path))
        bundle_manifest = self._fake_bundle(tmp_path / "bundles", "bundle-a")

        def fake_capture(*args, **kwargs):
            return dict(bundle_manifest)

        monkeypatch.setattr(preview_mod, "capture", fake_capture)

        started = preview_mod.live_start(session, root_dir=str(tmp_path), live_mode="manual")
        result = preview_mod.poll_live_session_once(started["_session_dir"])
        refreshed = json.loads(Path(started["_session_path"]).read_text())
        assert result["action"] == "exit"
        assert refreshed["poller"]["running"] is False
        assert refreshed["poller"]["last_exit_reason"] == "live-mode:manual"
