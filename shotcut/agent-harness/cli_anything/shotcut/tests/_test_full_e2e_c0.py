# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import _artifact_path, _assert_png, _luma_yavg, preview_video, session, video  # noqa: F401,E501
from ._test_full_e2e_p7 import _resolve_cli  # noqa: F401,E501


class _TestCLISubprocessMixin0:
    CLI_BASE = _resolve_cli("cli-anything-shotcut")
    def _run(self, *args, json_mode=False, timeout=30):
        import subprocess
        cmd = list(self.CLI_BASE)
        if json_mode:
            cmd.append("--json")
        cmd.extend(args)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result
    def test_help(self):
        r = self._run("--help")
        assert r.returncode == 0
        assert "Shotcut" in r.stdout
    def test_project_new(self):
        with tempfile.NamedTemporaryFile(suffix=".mlt", delete=False) as f:
            path = f.name
        try:
            r = self._run("project", "new", "--profile", "hd1080p30", "-o", path)
            assert r.returncode == 0
            assert os.path.isfile(path)
        finally:
            os.unlink(path)
    def test_project_info_json(self):
        with tempfile.NamedTemporaryFile(suffix=".mlt", delete=False) as f:
            path = f.name
        try:
            self._run("project", "new", "--profile", "hd1080p30", "-o", path)
            r = self._run("--json", "--project", path, "project", "info")
            assert r.returncode == 0
            data = json.loads(r.stdout)
            assert data["profile"]["width"] == "1920"
        finally:
            os.unlink(path)
    def test_profiles_list(self):
        r = self._run("project", "profiles")
        assert r.returncode == 0
        assert "hd1080p30" in r.stdout
    def test_filter_list_available(self):
        r = self._run("filter", "list-available")
        assert r.returncode == 0
        assert "brightness" in r.stdout
    def test_media_probe(self, video):
        r = self._run("media", "probe", video)
        assert r.returncode == 0
        assert os.path.basename(video) in r.stdout
    def test_preview_capture_json(self, preview_video):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = os.path.join(tmp_dir, "preview_source.mlt")

            session = Session()
            proj_mod.new_project(session, "hd1080p30")
            tl_mod.add_track(session, "video", "Preview")
            tl_mod.add_clip(
                session,
                preview_video,
                1,
                in_point="00:00:00.000",
                out_point="00:00:03.000",
                caption="Preview Shot",
            )
            filt_mod.add_filter(
                session,
                "brightness",
                track_index=1,
                clip_index=0,
                params={"level": "1.15"},
            )
            proj_mod.save_project(session, project_path)

            result = self._run(
                "--project",
                project_path,
                "preview",
                "capture",
                "--root-dir",
                tmp_dir,
                json_mode=True,
                timeout=180,
            )
            assert result.returncode == 0, result.stderr

            manifest = json.loads(result.stdout)
            assert manifest["software"] == "shotcut"
            assert manifest["bundle_kind"] == "capture"
            assert manifest["status"] in ("ok", "partial")
            clip_path = _artifact_path(manifest, "clip")
            hero_path = _artifact_path(manifest, "frame_03")
            assert manifest["artifacts"][0]["render_method"] == "ffmpeg-filtergraph"
            assert os.path.isfile(clip_path)
            _assert_png(hero_path)
            assert _luma_yavg(hero_path) > 10.0

            latest = self._run(
                "preview",
                "latest",
                "--recipe",
                "quick",
                "--root-dir",
                tmp_dir,
                json_mode=True,
                timeout=60,
            )
            assert latest.returncode == 0, latest.stderr
            latest_manifest = json.loads(latest.stdout)
            assert latest_manifest["bundle_id"] == manifest["bundle_id"]

            print(f"\n  Shotcut preview bundle: {manifest['_bundle_dir']}")
            print(f"  Shotcut preview clip: {clip_path}")
            print(f"  Shotcut preview hero: {hero_path}")
