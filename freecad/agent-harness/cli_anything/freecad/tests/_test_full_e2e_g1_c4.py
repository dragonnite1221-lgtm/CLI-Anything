# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLISubprocessMixin4:
    @pytest.mark.skipif(not (_has_freecad_preview() and _has_ffmpeg()), reason="GUI-capable FreeCAD and ffmpeg required")
    def test_motion_render_video_subprocess(self, tmp_path):
        proj_file = str(tmp_path / "motion_video.json")
        frames_dir = str(tmp_path / "motion-video-frames")
        video_path = str(tmp_path / "motion.mp4")

        proj = create_document(name="MotionVideo")
        add_part(proj, "box", name="Mover", params={"length": 20, "width": 12, "height": 8})
        save_document(proj, proj_file)

        assert self._run(
            "--json",
            "-p",
            proj_file,
            "motion",
            "new",
            "--name",
            "Drive",
            "--duration",
            "1.0",
            "--fps",
            "4",
            "--camera",
            "hero",
            "--width",
            "640",
            "--height",
            "480",
        ).returncode == 0

        assert self._run(
            "--json", "-p", proj_file, "motion", "keyframe", "0", "part", "0", "0.0"
        ).returncode == 0
        assert self._run(
            "--json",
            "-p",
            proj_file,
            "motion",
            "keyframe",
            "0",
            "part",
            "0",
            "1.0",
            "--position",
            "35,0,0",
            "--rotation",
            "0,0,90",
        ).returncode == 0

        rendered = self._run(
            "--json",
            "-p",
            proj_file,
            "motion",
            "render-video",
            "0",
            video_path,
            "--overwrite",
            "--frames-dir",
            frames_dir,
            timeout=300,
        )
        assert rendered.returncode == 0, rendered.stderr
        payload = json.loads(rendered.stdout)
        assert payload["format"] == "mp4"
        assert os.path.isfile(video_path)
        assert os.path.getsize(video_path) > 0
        assert payload["frame_count"] == 5
        assert payload["frames_dir"] == os.path.abspath(frames_dir)
        assert os.path.isfile(payload["sequence_path"])
