# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLISubprocessMixin1:
    def test_part_align_and_bounds_json(self, tmp_path):
        """Create parts, align one to another, and verify bbox output."""
        proj_file = str(tmp_path / "part_align.json")

        self._run("--json", "document", "new", "--name", "AlignTest", "-o", proj_file)
        self._run(
            "--json",
            "-p",
            proj_file,
            "part",
            "add",
            "box",
            "--name",
            "Base",
            "-P",
            "length=20",
            "-P",
            "width=10",
            "-P",
            "height=6",
        )
        self._run(
            "--json",
            "-p",
            proj_file,
            "part",
            "add",
            "box",
            "--name",
            "Cap",
            "-P",
            "length=8",
            "-P",
            "width=6",
            "-P",
            "height=4",
            "-pos",
            "100,50,20",
        )

        aligned = self._run(
            "--json",
            "-p",
            proj_file,
            "part",
            "align",
            "1",
            "0",
            "--x",
            "min",
            "--to-x",
            "max",
            "--y",
            "center",
            "--to-y",
            "center",
            "--z",
            "min",
            "--to-z",
            "max",
        )
        assert aligned.returncode == 0, aligned.stderr
        align_payload = json.loads(aligned.stdout)
        assert align_payload["placement"]["position"] == [20.0, 2.0, 6.0]

        bounds = self._run("--json", "-p", proj_file, "part", "bounds", "1")
        assert bounds.returncode == 0, bounds.stderr
        bounds_payload = json.loads(bounds.stdout)
        world = bounds_payload["world_bounding_box"]
        assert world["min"]["x"] == pytest.approx(20.0)
        assert world["center"]["y"] == pytest.approx(5.0)
        assert world["min"]["z"] == pytest.approx(6.0)
