# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestPreview:
    def test_list_recipes(self):
        recipes = preview_mod.list_recipes()
        assert recipes
        assert recipes[0]["name"] == "quick"

    def test_capture_bundle(self, tmp_path, monkeypatch):
        session = Session("preview_test")
        session.new_project("/tmp/source.mp4")

        def fake_render(session_obj, output_path, on_progress=None):
            Path(output_path).write_bytes(b"\x00\x00\x00\x18ftypmp42")
            return {
                "output": output_path,
                "duration": 8.0,
                "width": 1920,
                "height": 1080,
                "segments_rendered": 3,
            }

        def fake_probe(path):
            return {"duration": 8.0, "width": 1920, "height": 1080}

        def fake_thumb(input_path, output_path, time_s=0.0):
            Path(output_path).write_bytes(b"\xff\xd8\xff\xe0preview")
            return {"output": output_path, "time_s": time_s}

        monkeypatch.setattr(export_mod, "render", fake_render)
        monkeypatch.setattr(media_mod, "probe", fake_probe)
        monkeypatch.setattr(media_mod, "extract_thumbnail", fake_thumb)

        manifest = preview_mod.capture(session, root_dir=str(tmp_path))
        assert manifest["software"] == "openscreen"
        assert manifest["recipe"] == "quick"
        assert manifest["status"] == "ok"
        assert manifest["cached"] is False
        assert any(item["role"] == "preview-clip" for item in manifest["artifacts"])
        assert any(item["role"] == "hero" for item in manifest["artifacts"])
        assert os.path.isfile(manifest["_manifest_path"])
        assert os.path.isfile(manifest["_trajectory_path"])
        trajectory = json.loads(
            Path(manifest["_trajectory_path"]).read_text(encoding="utf-8")
        )
        assert trajectory["step_count"] == 1
        assert trajectory["steps"][0]["bundle_id"] == manifest["bundle_id"]
        assert trajectory["steps"][0]["publish_reason"] == "capture"

    def test_latest_bundle(self, tmp_path, monkeypatch):
        session = Session("preview_test")
        session.new_project("/tmp/source.mp4")

        def fake_render(session_obj, output_path, on_progress=None):
            Path(output_path).write_bytes(b"\x00\x00\x00\x18ftypmp42")
            return {
                "output": output_path,
                "duration": 5.0,
                "width": 1280,
                "height": 720,
                "segments_rendered": 2,
            }

        def fake_probe(path):
            return {"duration": 5.0, "width": 1280, "height": 720}

        def fake_thumb(input_path, output_path, time_s=0.0):
            Path(output_path).write_bytes(b"\xff\xd8\xff\xe0preview")
            return {"output": output_path, "time_s": time_s}

        monkeypatch.setattr(export_mod, "render", fake_render)
        monkeypatch.setattr(media_mod, "probe", fake_probe)
        monkeypatch.setattr(media_mod, "extract_thumbnail", fake_thumb)

        created = preview_mod.capture(session, root_dir=str(tmp_path))
        latest = preview_mod.latest(root_dir=str(tmp_path))
        assert latest["bundle_id"] == created["bundle_id"]
        assert os.path.isfile(latest["_trajectory_path"])
