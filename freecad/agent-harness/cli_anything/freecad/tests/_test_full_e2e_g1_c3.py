# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLISubprocessMixin3:
    @pytest.mark.skipif(not _has_freecad_preview(), reason="GUI-capable FreeCAD not installed")
    def test_motion_render_frames_subprocess(self, tmp_path):
        proj_file = str(tmp_path / "motion_frames.json")
        frames_dir = str(tmp_path / "motion-frames")

        created = self._run(
            "--json",
            "document",
            "new",
            "--name",
            "MotionFrames",
            "-o",
            proj_file,
        )
        assert created.returncode == 0, created.stderr

        added = self._run(
            "--json",
            "-p",
            proj_file,
            "part",
            "add",
            "box",
            "--name",
            "Mover",
            "-P",
            "length=20",
            "-P",
            "width=12",
            "-P",
            "height=8",
        )
        assert added.returncode == 0, added.stderr

        motion_new = self._run(
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
        )
        assert motion_new.returncode == 0, motion_new.stderr

        k0 = self._run("--json", "-p", proj_file, "motion", "keyframe", "0", "part", "0", "0.0")
        assert k0.returncode == 0, k0.stderr

        k1 = self._run(
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
            "0,0,45",
        )
        assert k1.returncode == 0, k1.stderr

        rendered = self._run(
            "--json",
            "-p",
            proj_file,
            "motion",
            "render-frames",
            "0",
            frames_dir,
            "--overwrite",
            timeout=240,
        )
        assert rendered.returncode == 0, rendered.stderr
        payload = json.loads(rendered.stdout)
        assert payload["frame_count"] == 5
        assert payload["method"] == "freecad-gui-sequence"

        sequence_path = payload["sequence_path"]
        assert os.path.isfile(sequence_path)
        with open(sequence_path, "r", encoding="utf-8") as fh:
            sequence = json.load(fh)
        assert sequence["frame_count"] == 5

        first_frame = os.path.join(payload["output_dir"], sequence["frames"][0]["path"])
        last_frame = os.path.join(payload["output_dir"], sequence["frames"][-1]["path"])
        _assert_png_not_blank(first_frame)
        _assert_png_not_blank(last_frame)
        _assert_images_differ(first_frame, last_frame)
