# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class TestPreviewE2E:
    @staticmethod
    def _run_cli(args, check=False, timeout=240):
        return subprocess.run(
            TestCLISubprocess.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout,
        )

    def test_capture_preview_bundle(self, tmp_dir):
        proj = create_scene(name="preview-test", profile="preview")
        add_object(proj, mesh_type="plane", name="Ground", scale=[5, 5, 1])
        add_object(proj, mesh_type="cube", name="Body", location=[0, 0, 1], scale=[1.2, 1.2, 1.2])
        add_object(proj, mesh_type="sphere", name="Accent", location=[2.2, 0.3, 1.0], scale=[0.7, 0.7, 0.7])
        create_material(proj, name="OrangeClay", color=[0.84, 0.45, 0.19, 1.0], roughness=0.32)
        create_material(proj, name="BlueAccent", color=[0.18, 0.42, 0.82, 1.0], metallic=0.1, roughness=0.25)
        assign_material(proj, 0, 1)
        assign_material(proj, 1, 2)
        add_camera(
            proj,
            name="MainCam",
            location=[7, -6, 5],
            rotation=[63, 0, 46],
            focal_length=50,
            set_active=True,
        )
        add_light(proj, light_type="SUN", name="KeySun", rotation=[-45, 0, 30], power=2.3)

        proj_path = os.path.join(tmp_dir, "preview_scene.json")
        save_scene(proj, proj_path)

        sess = Session()
        sess.set_project(proj, path=proj_path)

        manifest = preview_mod.capture(sess, root_dir=tmp_dir, force=True)
        assert manifest["software"] == "blender"
        assert manifest["bundle_kind"] == "capture"
        assert manifest["status"] in ("ok", "partial")

        hero_path = _artifact_path(manifest, "hero")
        workbench_path = _artifact_path(manifest, "workbench")
        _assert_png(hero_path)
        _assert_png(workbench_path)

        latest = preview_mod.latest(project_path=proj_path, recipe="quick", root_dir=tmp_dir)
        assert latest["bundle_id"] == manifest["bundle_id"]

        print(f"\n  Blender preview bundle: {manifest['_bundle_dir']}")
        print(f"  Blender preview hero: {hero_path}")
        print(f"  Blender preview workbench: {workbench_path}")

    def test_preview_live_poll_auto_refresh(self, tmp_dir):
        proj_path = os.path.join(tmp_dir, "preview_live_poll.json")
        live_root = os.path.join(tmp_dir, "live-root")

        proj = create_scene(name="poll-live", profile="preview")
        add_object(proj, mesh_type="plane", name="Ground", scale=[6, 6, 1])
        add_object(proj, mesh_type="torus", name="RingA", location=[0, 0, 1.35], rotation=[90, 0, 0])
        add_object(proj, mesh_type="sphere", name="Core", location=[0, 0, 1.35], scale=[0.45, 0.45, 0.45])
        create_material(proj, name="Bronze", color=[0.79, 0.58, 0.24, 1.0], metallic=0.9, roughness=0.22)
        create_material(proj, name="AzureCore", color=[0.22, 0.7, 0.95, 1.0], metallic=0.0, roughness=0.12)
        set_material_property(proj, 1, "emission_color", [0.22, 0.7, 0.95, 1.0])
        set_material_property(proj, 1, "emission_strength", 4.2)
        assign_material(proj, 0, 1)
        assign_material(proj, 1, 2)
        add_camera(proj, name="MainCam", location=[7.5, -7.0, 5.5], rotation=[63, 0, 46], set_active=True)
        add_light(proj, light_type="SUN", name="Sun", rotation=[-42, 0, 30], power=2.5)
        save_scene(proj, proj_path)

        started = self._run_cli(
            [
                "--json",
                "--project",
                proj_path,
                "preview",
                "live",
                "start",
                "--recipe",
                "quick",
                "--mode",
                "poll",
                "--source-poll-ms",
                "500",
                "--poll-ms",
                "700",
                "--root-dir",
                live_root,
            ],
            check=False,
            timeout=240,
        )
        assert started.returncode == 0, started.stderr
        started_payload = json.loads(started.stdout)
        assert started_payload["bundle_count"] == 1
        assert started_payload["live_mode"] == "poll"
        session_path = started_payload["_session_path"]

        try:
            changed = self._run_cli(
                [
                    "--json",
                    "--project",
                    proj_path,
                    "object",
                    "add",
                    "torus",
                    "--name",
                    "RingB",
                    "--location",
                    "0,0,1.35",
                    "--rotation",
                    "0,90,0",
                    "--scale",
                    "0.7,0.7,0.7",
                ],
                check=False,
                timeout=90,
            )
            assert changed.returncode == 0, changed.stderr

            session_payload = _wait_for_live_bundle_count(session_path, 2, timeout_s=45.0)
            assert session_payload["bundle_count"] >= 2
            assert session_payload["source_state"]["last_publish_reason"] == "auto-poll"
            assert session_payload["poller"]["running"] is True

            current_manifest_path = session_payload["current_manifest_path"]
            assert os.path.isfile(current_manifest_path)
            with open(current_manifest_path, "r", encoding="utf-8") as fh:
                current_manifest = json.load(fh)
            current_manifest["_bundle_dir"] = os.path.dirname(current_manifest_path)
            hero_path = _artifact_path(current_manifest, "hero")
            _assert_png(hero_path)

            print(f"\n  Blender poll session: {os.path.dirname(session_path)}")
            print(f"  Blender live hero: {hero_path}")
        finally:
            stopped = self._run_cli(
                [
                    "--json",
                    "--project",
                    proj_path,
                    "preview",
                    "live",
                    "stop",
                    "--recipe",
                    "quick",
                    "--root-dir",
                    live_root,
                ],
                check=False,
                timeout=60,
            )
            assert stopped.returncode == 0, stopped.stderr
