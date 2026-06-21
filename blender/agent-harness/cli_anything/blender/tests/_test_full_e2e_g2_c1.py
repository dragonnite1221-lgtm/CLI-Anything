# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLISubprocessMixin1:
    def test_cli_preview_live_manual_session(self, tmp_dir):
        proj_path = os.path.join(tmp_dir, "preview_live_manual.json")
        live_root = os.path.join(tmp_dir, "live-root")

        proj = create_scene(name="cli-live-manual", profile="preview")
        add_object(proj, mesh_type="plane", name="Ground", scale=[5, 5, 1])
        add_object(proj, mesh_type="torus", name="RingA", location=[0, 0, 1.3], rotation=[90, 0, 0])
        add_object(proj, mesh_type="sphere", name="Core", location=[0, 0, 1.3], scale=[0.55, 0.55, 0.55])
        create_material(proj, name="Brass", color=[0.83, 0.7, 0.28, 1.0], metallic=0.85, roughness=0.25)
        create_material(proj, name="CoreGlow", color=[0.2, 0.85, 1.0, 1.0], metallic=0.0, roughness=0.1)
        set_material_property(proj, 1, "emission_color", [0.2, 0.85, 1.0, 1.0])
        set_material_property(proj, 1, "emission_strength", 3.5)
        assign_material(proj, 0, 1)
        assign_material(proj, 1, 2)
        add_camera(proj, name="MainCam", location=[7, -7, 5], rotation=[63, 0, 46], set_active=True)
        add_light(proj, light_type="SUN", name="Sun", rotation=[-42, 0, 30], power=2.4)
        save_scene(proj, proj_path)

        started = self._run(
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
                "manual",
                "--root-dir",
                live_root,
            ],
            check=False,
            timeout=240,
        )
        assert started.returncode == 0, started.stderr
        started_payload = json.loads(started.stdout)
        assert started_payload["live_mode"] == "manual"
        assert started_payload["bundle_count"] == 1
        session_path = started_payload["_session_path"]
        assert os.path.isfile(session_path)

        status = self._run(
            [
                "--json",
                "--project",
                proj_path,
                "preview",
                "live",
                "status",
                "--recipe",
                "quick",
                "--root-dir",
                live_root,
            ],
            check=False,
            timeout=60,
        )
        assert status.returncode == 0, status.stderr
        status_payload = json.loads(status.stdout)
        assert status_payload["current_bundle_id"] == started_payload["current_bundle_id"]

        pushed = self._run(
            [
                "--json",
                "--project",
                proj_path,
                "preview",
                "live",
                "push",
                "--recipe",
                "quick",
                "--force",
                "--root-dir",
                live_root,
            ],
            check=False,
            timeout=240,
        )
        assert pushed.returncode == 0, pushed.stderr
        pushed_payload = json.loads(pushed.stdout)
        assert pushed_payload["bundle_count"] >= 2

        stopped = self._run(
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
        stopped_payload = json.loads(stopped.stdout)
        assert stopped_payload["status"] == "stopped"
