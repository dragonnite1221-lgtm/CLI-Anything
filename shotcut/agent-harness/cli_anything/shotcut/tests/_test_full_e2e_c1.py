# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import _wait_for_live_bundle_count, preview_video  # noqa: F401,E501


class _TestCLISubprocessMixin1:
    def test_preview_live_poll_auto_refresh(self, preview_video):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = os.path.join(tmp_dir, "preview_live_poll.mlt")
            live_root = os.path.join(tmp_dir, "live-root")

            r = self._run("project", "new", "--profile", "hd1080p30", "-o", project_path, timeout=60)
            assert r.returncode == 0, r.stderr

            r = self._run("-s", "--project", project_path, "timeline", "add-track", "--type", "video", "--name", "Preview", timeout=60)
            assert r.returncode == 0, r.stderr

            r = self._run(
                "-s",
                "--project",
                project_path,
                "timeline",
                "add-clip",
                preview_video,
                "--track",
                "1",
                "--in",
                "00:00:00.000",
                "--out",
                "00:00:04.000",
                "--caption",
                "Preview Clip",
                timeout=60,
            )
            assert r.returncode == 0, r.stderr

            started = self._run(
                "--json",
                "--project",
                project_path,
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
                timeout=180,
            )
            assert started.returncode == 0, started.stderr
            started_payload = json.loads(started.stdout)
            session_path = started_payload["_session_path"]
            assert started_payload["bundle_count"] == 1
            assert started_payload["live_mode"] == "poll"

            try:
                changed = self._run(
                    "-s",
                    "--project",
                    project_path,
                    "filter",
                    "add",
                    "brightness",
                    "--track",
                    "1",
                    "--clip",
                    "0",
                    "--param",
                    "level=1.35",
                    timeout=60,
                )
                assert changed.returncode == 0, changed.stderr

                session_payload = _wait_for_live_bundle_count(session_path, 2, timeout_s=20.0)
                assert session_payload["bundle_count"] >= 2
                assert session_payload["source_state"]["last_publish_reason"] == "auto-poll"
                assert session_payload["poller"]["running"] is True

                print(f"\n  Shotcut poll session: {session_payload['_session_dir'] if '_session_dir' in session_payload else os.path.dirname(session_path)}")
                print(f"  Shotcut poll bundle count: {session_payload['bundle_count']}")
                print(f"  Shotcut poll current bundle: {session_payload['current_bundle_id']}")
            finally:
                stopped = self._run(
                    "--project",
                    project_path,
                    "preview",
                    "live",
                    "stop",
                    "--root-dir",
                    live_root,
                    timeout=60,
                )
                assert stopped.returncode == 0, stopped.stderr
