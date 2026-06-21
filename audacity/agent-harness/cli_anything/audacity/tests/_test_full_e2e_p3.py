# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import sine_wav, stereo_wav  # noqa: F401,E501


class TestSessionE2E:
    def test_undo_track_addition(self, sine_wav):
        sess = Session()
        proj = create_project()
        sess.set_project(proj)

        sess.snapshot("Add track")
        add_track(proj, name="New Track")
        assert len(proj["tracks"]) == 1

        sess.undo()
        proj = sess.get_project()
        assert len(proj["tracks"]) == 0

    def test_undo_effect_addition(self, sine_wav):
        sess = Session()
        proj = create_project()
        add_track(proj, name="T1")
        sess.set_project(proj)

        sess.snapshot("Add effect")
        add_effect(proj, "amplify", 0, {"gain_db": 6.0})
        assert len(proj["tracks"][0]["effects"]) == 1

        sess.undo()
        proj = sess.get_project()
        assert len(proj["tracks"][0]["effects"]) == 0

    def test_heavy_undo_redo_stress(self):
        sess = Session()
        proj = create_project()
        sess.set_project(proj)

        # 30 operations
        for i in range(30):
            sess.snapshot(f"Add track {i}")
            add_track(proj, name=f"Track {i}")

        assert len(sess.get_project()["tracks"]) == 30

        # Undo all
        for i in range(30):
            sess.undo()
        assert len(sess.get_project()["tracks"]) == 0

        # Redo all
        for i in range(30):
            sess.redo()
        assert len(sess.get_project()["tracks"]) == 30


class TestMediaProbeE2E:
    def test_probe_real_wav(self, sine_wav):
        info = probe_audio(sine_wav)
        assert info["format"] == "WAV"
        assert info["sample_rate"] == 44100
        assert info["channels"] == 1
        assert info["bit_depth"] == 16
        assert abs(info["duration"] - 1.0) < 0.01

    def test_probe_stereo_wav(self, stereo_wav):
        info = probe_audio(stereo_wav)
        assert info["channels"] == 2
        assert abs(info["duration"] - 2.0) < 0.01

    def test_get_duration_real_file(self, sine_wav):
        dur = get_duration(sine_wav)
        assert abs(dur - 1.0) < 0.01

    def test_check_media_with_real_files(self, sine_wav):
        proj = create_project()
        add_track(proj, name="T1")
        add_clip(proj, 0, sine_wav, start_time=0.0)
        result = check_media(proj)
        assert result["status"] == "ok"
        assert result["found"] == 1


def _resolve_cli(name):
    """Resolve installed CLI command; falls back to python -m for dev.

    Set env CLI_ANYTHING_FORCE_INSTALLED=1 to require the installed command.
    """
    import shutil
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    module = name.replace("cli-anything-", "cli_anything.") + "." + name.split("-")[-1] + "_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]
