# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestPreviewMixin2:
    def test_project_fingerprint_is_stable_across_sessions_for_saved_project(self, tmp_path):
        project_path = tmp_path / "stable-project.json"
        proj = create_scene(name="StablePreviewScene")
        save_scene(proj, str(project_path))

        session_a = Session()
        session_a.set_project(proj, str(project_path))

        session_b = Session()
        session_b.set_project(open_scene(str(project_path)), str(project_path))

        assert preview_mod._project_fingerprint(session_a) == preview_mod._project_fingerprint(session_b)
    def test_poll_live_session_once_captures_after_source_change(self, tmp_path, monkeypatch):
        sess = Session()
        proj = create_scene(name="PollingPreviewScene")
        project_path = tmp_path / "polling-demo.json"
        save_scene(proj, str(project_path))
        sess.set_project(proj, str(project_path))
        bundle_a = self._fake_bundle(tmp_path / "bundles", "bundle-a")
        bundle_b = self._fake_bundle(tmp_path / "bundles", "bundle-b")
        manifests = [dict(bundle_a), dict(bundle_b)]

        def fake_capture(*args, **kwargs):
            return manifests.pop(0)

        monkeypatch.setattr(preview_mod, "capture", fake_capture)

        started = preview_mod.live_start(
            sess,
            root_dir=str(tmp_path),
            live_mode="poll",
            source_poll_ms=500,
        )
        started_session_dir = Path(started["_session_dir"])

        updated = open_scene(str(project_path))
        add_object(updated, mesh_type="cube", name="ChangedCube")
        save_scene(updated, str(project_path))

        result = preview_mod.poll_live_session_once(str(started_session_dir))
        payload = json.loads((started_session_dir / "session.json").read_text(encoding="utf-8"))
        trajectory = json.loads((started_session_dir / "trajectory.json").read_text(encoding="utf-8"))
        assert result["action"] == "captured"
        assert result["bundle_id"] == "bundle-b"
        assert payload["bundle_count"] >= 2
        assert payload["source_state"]["last_publish_reason"] == "auto-poll"
        assert trajectory["step_count"] == 2
        assert trajectory["steps"][-1]["publish_reason"] == "auto-poll"
    def test_poll_live_session_once_exits_for_manual_mode(self, tmp_path, monkeypatch):
        sess = Session()
        proj = create_scene(name="ManualPreviewScene")
        project_path = tmp_path / "manual-demo.json"
        save_scene(proj, str(project_path))
        sess.set_project(proj, str(project_path))
        bundle_manifest = self._fake_bundle(tmp_path / "bundles", "bundle-a")

        def fake_capture(*args, **kwargs):
            return dict(bundle_manifest)

        monkeypatch.setattr(preview_mod, "capture", fake_capture)

        started = preview_mod.live_start(sess, root_dir=str(tmp_path), live_mode="manual")
        result = preview_mod.poll_live_session_once(started["_session_dir"])
        assert result["action"] == "exit"
        assert result["reason"] == "mode:manual"
