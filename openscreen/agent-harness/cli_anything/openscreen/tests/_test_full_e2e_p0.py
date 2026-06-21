# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


def _resolve_cli(name: str):
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
        raise RuntimeError(
            f"{name} not found in PATH. Install with: pip install -e ."
        )
    module = "cli_anything.openscreen.openscreen_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


@pytest.fixture(scope="module")
def test_video():
    """Create a 5-second test video with ffmpeg."""
    tmpdir = tempfile.mkdtemp()
    video_path = os.path.join(tmpdir, "test_recording.mp4")

    try:
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i",
            "testsrc=duration=5:size=1920x1080:rate=30",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=5",
            "-c:v", "libx264", "-c:a", "aac", "-shortest",
            video_path,
        ], capture_output=True, check=True, timeout=30)
    except (FileNotFoundError, subprocess.CalledProcessError):
        pytest.skip("ffmpeg not available")

    yield video_path

    # Cleanup
    try:
        os.remove(video_path)
        os.rmdir(tmpdir)
    except OSError:
        pass


@pytest.fixture
def session(test_video):
    """Create a session with a project and test video attached."""
    s = Session()
    s.new_project(test_video)
    return s


def _artifact_path(manifest, artifact_id):
    for artifact in manifest["artifacts"]:
        if artifact["artifact_id"] == artifact_id:
            return os.path.join(manifest["_bundle_dir"], artifact["path"])
    raise KeyError(f"Artifact not found: {artifact_id}")


def _assert_jpeg(path):
    assert os.path.isfile(path), f"Missing JPEG artifact: {path}"
    with open(path, "rb") as fh:
        assert fh.read(3) == JPEG_MAGIC_PREFIX, f"Invalid JPEG header: {path}"
    assert os.path.getsize(path) > 0, f"Empty JPEG artifact: {path}"
