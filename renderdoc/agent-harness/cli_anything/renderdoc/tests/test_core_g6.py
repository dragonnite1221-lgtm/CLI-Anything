# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestPreviewModule:
    def _make_handle(
        self, tmp_path: Path, name: str = "frame"
    ) -> tuple[MagicMock, Path]:
        capture_path = tmp_path / f"{name}.rdc"
        capture_path.write_bytes(b"RDC")
        handle = MagicMock()
        handle.controller = MagicMock()
        handle.metadata.return_value = {"api": "Vulkan", "replay_supported": True}

        def _thumb(output_path, max_dim=0):
            Path(output_path).write_bytes(b"\x89PNG\r\n\x1a\nthumb")
            return {"path": output_path, "format": "PNG"}

        handle.thumbnail.side_effect = _thumb
        return handle, capture_path

    def test_capture_bundle(self, tmp_path, monkeypatch):
        from cli_anything.renderdoc.core import preview as preview_mod
        from cli_anything.renderdoc.core import actions as actions_mod
        from cli_anything.renderdoc.core import textures as textures_mod
        from cli_anything.renderdoc.core import pipeline as pipeline_mod

        handle, capture_path = self._make_handle(tmp_path, "capture_a")

        monkeypatch.setattr(
            actions_mod, "get_drawcalls_only", lambda controller: [{"eventId": 42}]
        )
        monkeypatch.setattr(
            actions_mod, "action_summary", lambda controller: {"drawcalls": 5}
        )

        def fake_save_outputs(controller, event_id, output_dir, file_format="png"):
            os.makedirs(output_dir, exist_ok=True)
            output_path = Path(output_dir) / f"event{event_id}_rt0.png"
            output_path.write_bytes(b"\x89PNG\r\n\x1a\nout")
            return [{"path": str(output_path), "label": "RT0"}]

        monkeypatch.setattr(textures_mod, "save_action_outputs", fake_save_outputs)
        monkeypatch.setattr(
            pipeline_mod,
            "get_pipeline_state",
            lambda controller, event_id: {"eventId": event_id},
        )

        manifest = preview_mod.capture(
            handle, str(capture_path), root_dir=str(tmp_path)
        )
        assert manifest["software"] == "renderdoc"
        assert manifest["recipe"] == "quick"
        assert manifest["status"] == "ok"
        assert any(item["role"] == "hero" for item in manifest["artifacts"])
        assert any(
            item["artifact_id"] == "pipeline_state" for item in manifest["artifacts"]
        )
        assert os.path.isfile(manifest["_trajectory_path"])
        trajectory = json.loads(
            Path(manifest["_trajectory_path"]).read_text(encoding="utf-8")
        )
        assert trajectory["step_count"] == 1
        assert trajectory["steps"][0]["publish_reason"] == "capture"

    def test_diff_bundle(self, tmp_path, monkeypatch):
        from cli_anything.renderdoc.core import preview as preview_mod
        from cli_anything.renderdoc.core import textures as textures_mod
        from cli_anything.renderdoc.core import pipeline as pipeline_mod
        from cli_anything.renderdoc.core import diff as diff_mod

        handle_a, capture_a = self._make_handle(tmp_path, "capture_a")
        handle_b, capture_b = self._make_handle(tmp_path, "capture_b")

        def fake_save_outputs(controller, event_id, output_dir, file_format="png"):
            os.makedirs(output_dir, exist_ok=True)
            output_path = Path(output_dir) / f"event{event_id}_rt0.png"
            output_path.write_bytes(b"\x89PNG\r\n\x1a\nout")
            return [{"path": str(output_path), "label": "RT0"}]

        monkeypatch.setattr(textures_mod, "save_action_outputs", fake_save_outputs)
        monkeypatch.setattr(
            pipeline_mod,
            "get_pipeline_state",
            lambda controller, event_id: {"eventId": event_id},
        )
        monkeypatch.setattr(
            diff_mod,
            "diff_pipeline",
            lambda *args, **kwargs: {
                "identical": False,
                "blend": {"enabled": {"A": True, "B": False}},
            },
        )

        manifest = preview_mod.diff(
            handle_a,
            str(capture_a),
            100,
            handle_b,
            str(capture_b),
            200,
            root_dir=str(tmp_path),
        )
        assert manifest["software"] == "renderdoc"
        assert manifest["bundle_kind"] == "diff"
        assert any(
            item["artifact_id"] == "pipeline_diff" for item in manifest["artifacts"]
        )
        assert os.path.isfile(manifest["_trajectory_path"])
        trajectory = json.loads(
            Path(manifest["_trajectory_path"]).read_text(encoding="utf-8")
        )
        assert trajectory["step_count"] == 1
        assert trajectory["steps"][0]["publish_reason"] == "diff"

    def test_latest_bundle(self, tmp_path, monkeypatch):
        from cli_anything.renderdoc.core import preview as preview_mod
        from cli_anything.renderdoc.core import actions as actions_mod
        from cli_anything.renderdoc.core import textures as textures_mod
        from cli_anything.renderdoc.core import pipeline as pipeline_mod

        handle, capture_path = self._make_handle(tmp_path, "capture_latest")

        monkeypatch.setattr(
            actions_mod, "get_drawcalls_only", lambda controller: [{"eventId": 7}]
        )
        monkeypatch.setattr(
            actions_mod, "action_summary", lambda controller: {"drawcalls": 1}
        )

        def fake_save_outputs(controller, event_id, output_dir, file_format="png"):
            os.makedirs(output_dir, exist_ok=True)
            output_path = Path(output_dir) / f"event{event_id}_rt0.png"
            output_path.write_bytes(b"\x89PNG\r\n\x1a\nout")
            return [{"path": str(output_path), "label": "RT0"}]

        monkeypatch.setattr(textures_mod, "save_action_outputs", fake_save_outputs)
        monkeypatch.setattr(
            pipeline_mod,
            "get_pipeline_state",
            lambda controller, event_id: {"eventId": event_id},
        )

        created = preview_mod.capture(handle, str(capture_path), root_dir=str(tmp_path))
        latest = preview_mod.latest(root_dir=str(tmp_path))
        assert latest["bundle_id"] == created["bundle_id"]
        assert os.path.isfile(latest["_trajectory_path"])
