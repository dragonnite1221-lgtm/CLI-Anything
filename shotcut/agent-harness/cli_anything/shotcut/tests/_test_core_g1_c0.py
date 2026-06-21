# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestPreviewMixin0:
    @staticmethod
    def _fake_bundle(tmp_path, bundle_id):
        bundle_dir = tmp_path / bundle_id
        artifacts_dir = bundle_dir / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        hero_path = artifacts_dir / "hero.png"
        clip_path = artifacts_dir / "preview.mp4"
        hero_path.write_bytes(b"\x89PNG\r\n\x1a\npreview")
        clip_path.write_bytes(b"\x00\x00\x00\x18ftypmp42")
        summary_path = bundle_dir / "summary.json"
        summary_path.write_text(json.dumps({"headline": "Shotcut quick preview", "facts": {"duration_s": 5.0}}))
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
        session = Session("preview_test")
        session.new_project()

        def fake_render(session_obj, output_path, preset, width, height, overwrite, prefer_ffmpeg=False):
            Path(output_path).write_bytes(b"\x00\x00\x00\x18ftypmp42")
            return {
                "output": output_path,
                "method": "ffmpeg-filtergraph" if prefer_ffmpeg else "melt",
                "size_bytes": 12,
            }

        def fake_probe(path):
            return {
                "duration_seconds": 6.0,
                "video_streams": [{"width": 640, "height": 360}],
            }

        def fake_thumb(filepath, output_path, timecode, width, height):
            Path(output_path).write_bytes(b"\x89PNG\r\n\x1a\npreview")
            return {"output": output_path, "time": timecode}

        monkeypatch.setattr(export_mod, "render", fake_render)
        monkeypatch.setattr(media_mod, "probe_media", fake_probe)
        monkeypatch.setattr(media_mod, "generate_thumbnail", fake_thumb)

        manifest = preview_mod.capture(session, root_dir=str(tmp_path))
        assert manifest["software"] == "shotcut"
        assert manifest["recipe"] == "quick"
        assert manifest["status"] == "ok"
        assert manifest["cached"] is False
        assert any(item["role"] == "preview-clip" for item in manifest["artifacts"])
        assert any(item["role"] == "hero" for item in manifest["artifacts"])
        assert os.path.isfile(manifest["_manifest_path"])
    def test_latest_bundle(self, tmp_path, monkeypatch):
        session = Session("preview_test")
        session.new_project()

        def fake_render(session_obj, output_path, preset, width, height, overwrite, prefer_ffmpeg=False):
            Path(output_path).write_bytes(b"\x00\x00\x00\x18ftypmp42")
            return {"output": output_path, "method": "ffmpeg-filtergraph" if prefer_ffmpeg else "melt"}

        def fake_probe(path):
            return {
                "duration_seconds": 3.0,
                "video_streams": [{"width": 640, "height": 360}],
            }

        def fake_thumb(filepath, output_path, timecode, width, height):
            Path(output_path).write_bytes(b"\x89PNG\r\n\x1a\nthumb")
            return {"output": output_path, "time": timecode}

        monkeypatch.setattr(export_mod, "render", fake_render)
        monkeypatch.setattr(media_mod, "probe_media", fake_probe)
        monkeypatch.setattr(media_mod, "generate_thumbnail", fake_thumb)

        created = preview_mod.capture(session, root_dir=str(tmp_path))
        latest = preview_mod.latest(root_dir=str(tmp_path))
        assert latest["bundle_id"] == created["bundle_id"]
