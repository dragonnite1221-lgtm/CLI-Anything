# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestPreviewMixin0:
    @staticmethod
    def _fake_bundle(tmp_path, bundle_id):
        bundle_dir = tmp_path / bundle_id
        artifacts_dir = bundle_dir / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        for artifact_id in ("hero", "front", "top", "right"):
            (artifacts_dir / f"{artifact_id}.png").write_bytes(b"\x89PNG\r\n\x1a\npreview")
        summary_path = bundle_dir / "summary.json"
        summary_path.write_text(
            json.dumps(
                {
                    "headline": "FreeCAD quick preview",
                    "facts": {"views": 4, "units": "mm"},
                }
            )
        )
        manifest_path = bundle_dir / "manifest.json"
        manifest_path.write_text(json.dumps({"bundle_id": bundle_id, "status": "ok"}))
        return {
            "bundle_id": bundle_id,
            "status": "ok",
            "_bundle_dir": str(bundle_dir),
            "_manifest_path": str(manifest_path),
            "_summary_path": str(summary_path),
            "cached": False,
        }
    def test_list_recipes(self):
        recipes = preview_mod.list_recipes()
        assert recipes
        assert recipes[0]["name"] == "quick"
    def test_capture_bundle(self, tmp_path, monkeypatch):
        sess = Session()
        proj = create_document(name="PreviewDoc")
        add_part(proj, "box", name="HeroBox")
        sess.set_project(proj, str(tmp_path / "project.json"))

        def fake_capture(script_content, timeout=120, gui_required=False, env=None):
            marker = "artifacts/"
            for line in script_content.splitlines():
                if marker in line and ".png" in line:
                    path = line.split("'")[3]
                    Path(path).parent.mkdir(parents=True, exist_ok=True)
                    Path(path).write_bytes(b"\x89PNG\r\n\x1a\npreview")
            return {"returncode": 0, "stdout": "", "stderr": ""}

        monkeypatch.setattr(freecad_backend, "run_macro_content", fake_capture)

        manifest = preview_mod.capture(sess, root_dir=str(tmp_path))
        assert manifest["software"] == "freecad"
        assert manifest["recipe"] == "quick"
        assert any(item["role"] == "hero" for item in manifest["artifacts"])
        assert len(manifest["artifacts"]) >= 4
    def test_latest_bundle(self, tmp_path, monkeypatch):
        sess = Session()
        proj = create_document(name="PreviewDoc")
        add_part(proj, "box", name="HeroBox")
        sess.set_project(proj)

        def fake_capture(script_content, timeout=120, gui_required=False, env=None):
            for line in script_content.splitlines():
                if "artifacts/" in line and ".png" in line:
                    path = line.split("'")[3]
                    Path(path).parent.mkdir(parents=True, exist_ok=True)
                    Path(path).write_bytes(b"\x89PNG\r\n\x1a\npreview")
            return {"returncode": 0, "stdout": "", "stderr": ""}

        monkeypatch.setattr(freecad_backend, "run_macro_content", fake_capture)

        created = preview_mod.capture(sess, root_dir=str(tmp_path))
        latest = preview_mod.latest(root_dir=str(tmp_path))
        assert latest["bundle_id"] == created["bundle_id"]
    def test_live_start_publishes_session(self, tmp_path, monkeypatch):
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

        live = preview_mod.live_start(
            sess,
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
