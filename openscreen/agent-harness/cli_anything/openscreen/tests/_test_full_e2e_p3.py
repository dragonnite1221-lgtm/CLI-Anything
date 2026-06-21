# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import _artifact_path, _assert_jpeg, session  # noqa: F401,E501


class TestPreviewE2E:
    def test_capture_preview_bundle(self, session):
        tl_mod.add_zoom_region(session, 800, 2400, depth=2, focus_x=0.65, focus_y=0.35)
        tl_mod.add_speed_region(session, 2500, 3800, speed=1.5)

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = os.path.join(tmp_dir, "preview.openscreen")
            proj_mod.save_project(session, project_path)

            manifest = preview_mod.capture(session, root_dir=tmp_dir, force=True)
            assert manifest["software"] == "openscreen"
            assert manifest["bundle_kind"] == "capture"
            assert manifest["status"] in ("ok", "partial")

            clip_path = _artifact_path(manifest, "clip")
            hero_path = _artifact_path(manifest, "frame_03")
            probe = media_mod.probe(clip_path)

            assert os.path.isfile(clip_path)
            assert os.path.getsize(clip_path) > 0
            assert probe["width"] > 0
            assert probe["height"] > 0
            assert probe["duration"] > 0
            _assert_jpeg(hero_path)

            latest = preview_mod.latest(project_path=project_path, recipe="quick", root_dir=tmp_dir)
            assert latest["bundle_id"] == manifest["bundle_id"]

            print(f"\n  Openscreen preview bundle: {manifest['_bundle_dir']}")
            print(f"  Openscreen preview clip: {clip_path}")
            print(f"  Openscreen preview hero: {hero_path}")
