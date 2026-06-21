# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import _make_project, _make_wrapper_script  # noqa: F401,E501


class TestMotion:
    """Tests for motion sequencing and interpolation."""

    def test_create_motion_defaults(self):
        proj = _make_project()
        motion = motion_mod.create_motion(proj, name="Drive")
        assert motion["name"] == "Drive"
        assert motion["duration"] == 2.0
        assert motion["fps"] == 24
        assert motion["camera"] == "hero"
        assert motion["fit_mode"] == "initial"
        assert motion["tracks"] == []
        assert len(proj["motions"]) == 1

    def test_add_keyframes_and_sample_interpolates(self):
        proj = _make_project()
        add_part(proj, "box", name="RoverBody", position=[0.0, 0.0, 0.0])
        motion_mod.create_motion(proj, name="Drive", duration=2.0, fps=10)
        motion_mod.add_keyframe(
            proj,
            0,
            target_kind="part",
            target_index=0,
            time_value=0.0,
            position=[0.0, 0.0, 0.0],
            rotation=[0.0, 0.0, 0.0],
        )
        motion_mod.add_keyframe(
            proj,
            0,
            target_kind="part",
            target_index=0,
            time_value=2.0,
            position=[20.0, 10.0, 0.0],
            rotation=[0.0, 0.0, 90.0],
        )

        sample = motion_mod.sample_motion(proj, 0, 1.0)
        assert sample["time"] == 1.0
        assert len(sample["placements"]) == 1
        placement = sample["placements"][0]
        assert placement["position"] == [10.0, 5.0, 0.0]
        assert placement["rotation"] == [0.0, 0.0, 45.0]

    def test_apply_motion_returns_project_copy(self):
        proj = _make_project()
        add_part(proj, "box", name="Wheel", position=[1.0, 2.0, 3.0], rotation=[0.0, 0.0, 0.0])
        motion_mod.create_motion(proj, duration=1.0, fps=5)
        motion_mod.add_keyframe(proj, 0, target_kind="part", target_index=0, time_value=0.0)
        motion_mod.add_keyframe(
            proj,
            0,
            target_kind="part",
            target_index=0,
            time_value=1.0,
            position=[11.0, 2.0, 3.0],
            rotation=[0.0, 30.0, 0.0],
        )

        animated = motion_mod.apply_motion(proj, 0, 0.5)
        assert animated is not proj
        assert animated["parts"][0]["placement"]["position"] == [6.0, 2.0, 3.0]
        assert animated["parts"][0]["placement"]["rotation"] == [0.0, 15.0, 0.0]
        assert proj["parts"][0]["placement"]["position"] == [1.0, 2.0, 3.0]

    def test_render_video_requires_supported_extension(self, tmp_path):
        proj = _make_project()
        add_part(proj, "box", name="Box")
        motion_mod.create_motion(proj, duration=1.0, fps=5)
        motion_mod.add_keyframe(proj, 0, target_kind="part", target_index=0, time_value=0.0)
        with pytest.raises(ValueError, match="supports .mp4, .webm, and .gif"):
            motion_mod.render_video(proj, 0, str(tmp_path / "bad.avi"))


class TestFreeCADBackend:
    """Tests for backend command selection and wrapper handling."""

    def test_detects_gui_wrapper_script(self, tmp_path):
        wrapper = _make_wrapper_script(tmp_path / "freecad-wrapper")
        assert freecad_backend._is_gui_wrapper_script(str(wrapper)) is True

    def test_macro_command_forces_gui_branch_for_wrapper(self, tmp_path):
        wrapper = _make_wrapper_script(tmp_path / "freecad-wrapper")
        script_path = tmp_path / "macro.py"
        script_path.write_text("print('ok')\n", encoding="utf-8")

        argv = freecad_backend._macro_command(str(wrapper), str(script_path), gui_required=True)
        assert argv == [str(wrapper), "freecad", str(script_path)]

    def test_run_macro_uses_wrapper_gui_override(self, tmp_path, monkeypatch):
        wrapper = _make_wrapper_script(tmp_path / "freecad-wrapper")
        script_path = tmp_path / "macro.py"
        script_path.write_text("print('ok')\n", encoding="utf-8")
        captured = {}

        monkeypatch.setattr(freecad_backend, "find_freecad", lambda gui_required=False: str(wrapper))

        def fake_run(args, *, timeout=120, check=False, env=None):
            captured["args"] = args
            captured["timeout"] = timeout
            captured["env"] = env
            return {"command": " ".join(args), "returncode": 0, "stdout": "", "stderr": "", "ok": True}

        monkeypatch.setattr(freecad_backend, "_run", fake_run)

        result = freecad_backend.run_macro(str(script_path), timeout=55, gui_required=True, env={"QT_QPA_PLATFORM": "offscreen"})

        assert result["returncode"] == 0
        assert captured["args"] == [str(wrapper), "freecad", str(script_path.resolve())]
        assert captured["timeout"] == 55
        assert captured["env"] == {"QT_QPA_PLATFORM": "offscreen"}
