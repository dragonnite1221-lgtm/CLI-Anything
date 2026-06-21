# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import test_video  # noqa: F401,E501


class TestMediaE2E:
    def test_probe_real_video(self, test_video):
        result = media_mod.probe(test_video)
        assert result["width"] == 1920
        assert result["height"] == 1080
        assert result["duration"] > 4.0
        assert result["codec"] == "h264"
        assert result["has_audio"] is True

    def test_check_video(self, test_video):
        result = media_mod.check_video(test_video)
        assert result["valid"] is True
        assert result["width"] == 1920

    def test_check_invalid_video(self):
        result = media_mod.check_video("/nonexistent/file.mp4")
        assert result["valid"] is False

    def test_extract_thumbnail(self, test_video):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            thumb_path = f.name
        try:
            result = media_mod.extract_thumbnail(test_video, thumb_path, time_s=1.0)
            assert os.path.exists(thumb_path)
            assert result["file_size"] > 0
        finally:
            os.unlink(thumb_path)

    def test_extract_thumbnail_at_zero(self, test_video):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            thumb_path = f.name
        try:
            result = media_mod.extract_thumbnail(test_video, thumb_path, time_s=0.0)
            assert os.path.exists(thumb_path)
            assert result["file_size"] > 0
        finally:
            os.unlink(thumb_path)

    def test_extract_frames(self, test_video):
        tmpdir = tempfile.mkdtemp()
        try:
            frames = ffmpeg_backend.extract_frames(test_video, tmpdir, fps=2, max_frames=10)
            assert len(frames) > 0
            assert all(f.endswith(".jpg") for f in frames)
            assert all(os.path.getsize(f) > 0 for f in frames)
        finally:
            import shutil
            shutil.rmtree(tmpdir)

    def test_ffmpeg_and_ffprobe_found(self):
        ffmpeg = ffmpeg_backend.find_ffmpeg()
        ffprobe = ffmpeg_backend.find_ffprobe()
        assert os.path.exists(ffmpeg)
        assert os.path.exists(ffprobe)
        print(f"\n  ffmpeg: {ffmpeg}")
        print(f"  ffprobe: {ffprobe}")
