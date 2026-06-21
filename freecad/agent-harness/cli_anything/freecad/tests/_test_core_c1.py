# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestPreviewMixin1:
    def test_live_push_updates_history(self, tmp_path, monkeypatch):
        sess = Session()
        proj = create_document(name="LivePreviewDoc")
        add_part(proj, "box", name="HeroBox")
        project_path = tmp_path / "live-demo.json"
        save_document(proj, str(project_path))
        sess.set_project(proj, str(project_path))
        bundle_a = self._fake_bundle(tmp_path / "bundles", "bundle-a")
        bundle_b = self._fake_bundle(tmp_path / "bundles", "bundle-b")
        manifests = [dict(bundle_a), dict(bundle_b)]

        def fake_capture(*args, **kwargs):
            return manifests.pop(0)

        monkeypatch.setattr(preview_mod, "capture", fake_capture)

        started = preview_mod.live_start(sess, root_dir=str(tmp_path))
        pushed = preview_mod.live_push(sess, root_dir=str(tmp_path))
        assert started["current_bundle_id"] == "bundle-a"
        assert pushed["current_bundle_id"] == "bundle-b"
        assert pushed["history"][0]["bundle_id"] == "bundle-b"
        assert pushed["history"][1]["bundle_id"] == "bundle-a"
        trajectory = json.loads(Path(pushed["_trajectory_path"]).read_text(encoding="utf-8"))
        assert trajectory["step_count"] == 2
        assert [step["bundle_id"] for step in trajectory["steps"]] == ["bundle-a", "bundle-b"]
        assert pushed["current_step_id"] == "step-0002"
    def test_live_status_includes_trajectory_summary(self, tmp_path, monkeypatch):
        sess = Session()
        proj = create_document(name="LivePreviewDoc")
        add_part(proj, "box", name="HeroBox")
        project_path = tmp_path / "live-demo.json"
        save_document(proj, str(project_path))
        sess.set_project(proj, str(project_path))
        bundle_manifest = self._fake_bundle(tmp_path / "bundles", "bundle-a")

        monkeypatch.setattr(preview_mod, "capture", lambda *args, **kwargs: dict(bundle_manifest))

        preview_mod.live_start(sess, root_dir=str(tmp_path), live_mode="manual")
        status = preview_mod.live_status(sess, root_dir=str(tmp_path))
        summary = status["trajectory_summary"]
        assert summary["step_count"] == 1
        assert summary["latest_bundle_id"] == "bundle-a"
        assert summary["latest_publish_reason"] == "live-start"
        assert summary["recent_steps"][0]["step_id"] == "step-0001"
    def test_live_push_records_publish_time_when_bundle_is_reused(self, tmp_path, monkeypatch):
        sess = Session()
        proj = create_document(name="LivePreviewDoc")
        add_part(proj, "box", name="HeroBox")
        project_path = tmp_path / "live-demo.json"
        save_document(proj, str(project_path))
        sess.set_project(proj, str(project_path))
        bundle_manifest = self._fake_bundle(tmp_path / "bundles", "bundle-a")
        bundle_manifest["created_at"] = "2025-01-01T00:00:00Z"
        publish_times = [
            "2026-04-23T10:00:00Z",
            "2026-04-23T10:05:00Z",
        ]

        monkeypatch.setattr(preview_mod, "capture", lambda *args, **kwargs: dict(bundle_manifest))
        monkeypatch.setattr(preview_mod, "_now_iso", lambda: publish_times.pop(0))

        preview_mod.live_start(sess, root_dir=str(tmp_path), live_mode="manual")
        pushed = preview_mod.live_push(sess, root_dir=str(tmp_path))
        trajectory = json.loads(Path(pushed["_trajectory_path"]).read_text(encoding="utf-8"))

        assert len(pushed["history"]) == 1
        assert [step["bundle_id"] for step in trajectory["steps"]] == ["bundle-a", "bundle-a"]
        assert [step["command_finished_at"] for step in trajectory["steps"]] == [
            "2026-04-23T10:00:00Z",
            "2026-04-23T10:05:00Z",
        ]
        assert all(step["created_at"] == "2025-01-01T00:00:00Z" for step in trajectory["steps"])
    def test_live_stop_marks_session_stopped(self, tmp_path, monkeypatch):
        sess = Session()
        proj = create_document(name="LivePreviewDoc")
        add_part(proj, "box", name="HeroBox")
        project_path = tmp_path / "live-demo.json"
        save_document(proj, str(project_path))
        sess.set_project(proj, str(project_path))
        bundle_manifest = self._fake_bundle(tmp_path / "bundles", "bundle-a")

        def fake_capture(*args, **kwargs):
            return dict(bundle_manifest)

        monkeypatch.setattr(preview_mod, "capture", fake_capture)

        preview_mod.live_start(sess, root_dir=str(tmp_path))
        stopped = preview_mod.live_stop(sess, root_dir=str(tmp_path))
        assert stopped["status"] == "stopped"
        assert "stopped_at" in stopped
    def test_live_session_name_is_stable_for_same_project_path(self, tmp_path):
        project_path = tmp_path / "stable-demo.json"
        proj = create_document(name="StablePreviewDoc")
        save_document(proj, str(project_path))

        session_a = Session()
        session_a.set_project(proj, str(project_path))

        session_b = Session()
        session_b.set_project(open_document(str(project_path)), str(project_path))

        name_a = preview_mod._live_session_name(session_a, "quick")
        name_b = preview_mod._live_session_name(session_b, "quick")
        assert name_a == name_b
