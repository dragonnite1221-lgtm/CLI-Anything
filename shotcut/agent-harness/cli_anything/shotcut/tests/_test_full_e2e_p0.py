# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@pytest.fixture
def video():
    """Ensure the test video exists."""
    assert os.path.isfile(VIDEO), f"Test video not found: {VIDEO}"
    return VIDEO


@pytest.fixture
def session():
    s = Session()
    proj_mod.new_project(s, "hd1080p30")
    return s


@pytest.fixture
def session_with_tracks(session):
    tl_mod.add_track(session, "video", "V1")
    tl_mod.add_track(session, "video", "V2")
    tl_mod.add_track(session, "audio", "A1")
    return session


@pytest.fixture(scope="module")
def preview_video():
    """Create a colorful deterministic source video for preview verification."""
    tmpdir = tempfile.mkdtemp()
    video_path = os.path.join(tmpdir, "preview_source.mp4")
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "testsrc=duration=5:size=1280x720:rate=30",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:duration=5",
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                "-shortest",
                video_path,
            ],
            capture_output=True,
            check=True,
            timeout=60,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        pytest.skip("ffmpeg not available")

    yield video_path

    shutil.rmtree(tmpdir, ignore_errors=True)


def _artifact_path(manifest, artifact_id):
    for artifact in manifest["artifacts"]:
        if artifact["artifact_id"] == artifact_id:
            return os.path.join(manifest["_bundle_dir"], artifact["path"])
    raise KeyError(f"Artifact not found: {artifact_id}")


def _assert_png(path):
    assert os.path.isfile(path), f"Missing PNG artifact: {path}"
    with open(path, "rb") as fh:
        assert fh.read(8) == PNG_MAGIC, f"Invalid PNG header: {path}"
    assert os.path.getsize(path) > 0, f"Empty PNG artifact: {path}"


def _luma_yavg(path):
    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            path,
            "-vf",
            "signalstats,metadata=print:file=-",
            "-frames:v",
            "1",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    match = re.search(r"lavfi\.signalstats\.YAVG=([0-9.]+)", result.stdout + result.stderr)
    if not match:
        raise AssertionError(f"Could not determine YAVG for {path}")
    return float(match.group(1))


def _wait_for_live_bundle_count(session_path, expected_count, timeout_s=20.0):
    deadline = time.time() + timeout_s
    latest = None
    while time.time() < deadline:
        with open(session_path, "r", encoding="utf-8") as fh:
            latest = json.load(fh)
        if latest.get("bundle_count", 0) >= expected_count:
            return latest
        time.sleep(0.5)
    raise AssertionError(f"Timed out waiting for bundle_count >= {expected_count}: {latest}")
