# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import _artifact_path, _assert_png, _luma_yavg, preview_video, session  # noqa: F401,E501


def _resolve_cli(name, force=False):
    import shutil
    path = shutil.which(name)
    if path:
        return [path]
    module = name.replace("cli-anything-", "cli_anything.") + "." + name.split("-")[-1] + "_cli"
    return [sys.executable, "-m", module]


class TestPreviewE2E:
    def test_capture_preview_bundle(self, session, preview_video):
        tl_mod.add_track(session, "video", "Preview")
        tl_mod.add_clip(
            session,
            preview_video,
            1,
            in_point="00:00:00.000",
            out_point="00:00:04.000",
            caption="Preview Clip",
        )
        filt_mod.add_filter(
            session,
            "brightness",
            track_index=1,
            clip_index=0,
            params={"level": "1.25"},
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = os.path.join(tmp_dir, "preview_capture.mlt")
            proj_mod.save_project(session, project_path)

            manifest = preview_mod.capture(session, root_dir=tmp_dir, force=True)
            assert manifest["software"] == "shotcut"
            assert manifest["bundle_kind"] == "capture"
            assert manifest["status"] in ("ok", "partial")

            clip_path = _artifact_path(manifest, "clip")
            hero_path = _artifact_path(manifest, "frame_03")
            probe = media_mod.probe_media(clip_path)
            video_stream = (probe.get("video_streams") or [{}])[0]

            assert os.path.isfile(clip_path)
            assert os.path.getsize(clip_path) > 0
            assert manifest["artifacts"][0]["render_method"] == "ffmpeg-filtergraph"
            assert int(video_stream.get("width") or 0) == 640
            assert int(video_stream.get("height") or 0) == 360
            _assert_png(hero_path)
            assert _luma_yavg(hero_path) > 10.0

            latest = preview_mod.latest(project_path=project_path, recipe="quick", root_dir=tmp_dir)
            assert latest["bundle_id"] == manifest["bundle_id"]

            print(f"\n  Shotcut preview bundle: {manifest['_bundle_dir']}")
            print(f"  Shotcut preview clip: {clip_path}")
            print(f"  Shotcut preview hero: {hero_path}")
