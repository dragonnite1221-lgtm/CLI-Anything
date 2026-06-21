# ruff: noqa: F403, F405, E501
from ._test_cli_hub_base import *  # noqa: F403


def _make_preview_bundle(tmp_path: Path, *, with_trajectory: bool = False) -> Path:
    bundle_dir = tmp_path / "preview-bundle"
    artifacts_dir = bundle_dir / "artifacts"
    artifacts_dir.mkdir(parents=True)
    (artifacts_dir / "hero.png").write_bytes(b"\x89PNG\r\n\x1a\npreview")
    (artifacts_dir / "preview.mp4").write_bytes(b"\x00\x00\x00\x18ftypmp42")
    summary = {
        "headline": "Quick preview rendered",
        "facts": {
            "duration_s": 6.0,
            "resolution": "640x360",
        },
        "warnings": [],
    }
    manifest = {
        "protocol_version": "preview-bundle/v1",
        "bundle_id": "20260419T104530Z_deadbeef_quick",
        "bundle_kind": "capture",
        "software": "shotcut",
        "recipe": "quick",
        "status": "ok",
        "created_at": "2026-04-19T10:45:30Z",
        "generator": {"entry_point": "cli-anything-shotcut", "command": "cli-anything-shotcut preview capture --recipe quick"},
        "source": {"project_path": "/tmp/demo.mlt", "project_fingerprint": "sha256:test"},
        "summary_path": "summary.json",
        "artifacts": [
            {
                "artifact_id": "hero",
                "role": "hero",
                "kind": "image",
                "label": "Midpoint frame",
                "media_type": "image/png",
                "path": "artifacts/hero.png",
                "width": 960,
                "height": 540,
                "bytes": (artifacts_dir / "hero.png").stat().st_size,
            },
            {
                "artifact_id": "clip",
                "role": "preview-clip",
                "kind": "clip",
                "label": "Preview clip",
                "media_type": "video/mp4",
                "path": "artifacts/preview.mp4",
                "width": 640,
                "height": 360,
                "duration_s": 6.0,
                "bytes": (artifacts_dir / "preview.mp4").stat().st_size,
            },
        ],
    }
    if with_trajectory:
        trajectory = {
            "protocol_version": "preview-trajectory/v1",
            "step_count": 1,
            "current_step_id": "step-001",
            "steps": [
                {
                    "step_id": "step-001",
                    "step_index": 1,
                    "bundle_id": "20260419T104530Z_deadbeef_quick",
                    "bundle_dir": str(bundle_dir),
                    "manifest_path": str(bundle_dir / "manifest.json"),
                    "summary_path": str(bundle_dir / "summary.json"),
                    "created_at": "2026-04-19T10:45:30Z",
                    "status": "ok",
                    "cached": False,
                    "publish_reason": "capture",
                    "command": "cli-anything-shotcut preview capture --recipe quick",
                }
            ],
        }
        (tmp_path / "trajectory.json").write_text(json.dumps(trajectory, indent=2))
        manifest["context"] = {"trajectory_path": "../trajectory.json"}
    (bundle_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return bundle_dir
