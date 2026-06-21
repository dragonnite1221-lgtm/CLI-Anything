# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLISubprocessMixin5:
    @pytest.mark.skipif(not _has_freecad_preview(), reason="GUI-capable FreeCAD not installed")
    def test_preview_live_poll_auto_refresh(self, tmp_path):
        proj_file = str(tmp_path / "preview_live_poll.json")
        live_root = str(tmp_path / "live-root")

        proj = create_document(name="PreviewLiveCLI")
        add_part(proj, "box", name="BaseBody", params={"length": 24, "width": 18, "height": 10})
        save_document(proj, proj_file)

        started = self._run(
            "--json",
            "-p",
            proj_file,
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
            timeout=240,
        )
        assert started.returncode == 0, started.stderr
        started_payload = json.loads(started.stdout)
        session_path = started_payload["_session_path"]
        assert started_payload["bundle_count"] == 1
        assert started_payload["live_mode"] == "poll"

        try:
            changed = self._run(
                "--json",
                "-p",
                proj_file,
                "part",
                "add",
                "cylinder",
                "--name",
                "SideBoss",
                "-P",
                "radius=4",
                "-P",
                "height=14",
                "-pos",
                "18,0,0",
                timeout=60,
            )
            assert changed.returncode == 0, changed.stderr

            session_payload = _wait_for_live_bundle_count(session_path, 2, timeout_s=30.0)
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

            print(f"\n  FreeCAD poll session: {os.path.dirname(session_path)}")
            print(f"  FreeCAD live hero: {hero_path}")
        finally:
            stopped = self._run(
                "--json",
                "-p",
                proj_file,
                "preview",
                "live",
                "stop",
                "--recipe",
                "quick",
                "--root-dir",
                live_root,
                timeout=60,
            )
            assert stopped.returncode == 0, stopped.stderr
