# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import session  # noqa: F401,E501


class TestExportE2E:
    def test_basic_export(self, session):
        """Export with default settings (no regions)."""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            out_path = f.name
        try:
            result = export_mod.render(session, out_path)
            assert os.path.exists(out_path)
            assert result["file_size"] > 0
            assert result["width"] > 0
            assert result["codec"] == "h264"
            assert result["segments_rendered"] >= 1
        finally:
            os.unlink(out_path)

    def test_export_with_zoom(self, session):
        """Export with a zoom region."""
        tl_mod.add_zoom_region(session, 1000, 3000, depth=3, focus_x=0.7, focus_y=0.3)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            out_path = f.name
        try:
            result = export_mod.render(session, out_path)
            assert os.path.exists(out_path)
            assert result["file_size"] > 0
            assert result["segments_rendered"] >= 2  # before, during, after zoom
        finally:
            os.unlink(out_path)

    def test_export_with_speed(self, session):
        """Export with a speed region."""
        tl_mod.add_speed_region(session, 2000, 4000, speed=2.0)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            out_path = f.name
        try:
            result = export_mod.render(session, out_path)
            assert os.path.exists(out_path)
            assert result["file_size"] > 0
            # Output should be shorter than source due to 2x speed section
            assert result["duration"] < 5.0
        finally:
            os.unlink(out_path)

    def test_export_with_trim(self, session):
        """Export with a trim region."""
        tl_mod.add_trim_region(session, 0, 1000)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            out_path = f.name
        try:
            result = export_mod.render(session, out_path)
            assert os.path.exists(out_path)
            # Should be shorter due to trimmed 1 second
            assert result["duration"] < 5.0
        finally:
            os.unlink(out_path)

    def test_export_complex(self, session):
        """Export with multiple regions and settings."""
        proj_mod.set_setting(session, "padding", 40)
        proj_mod.set_setting(session, "wallpaper", "solid_dark")

        tl_mod.add_zoom_region(session, 500, 2000, depth=4, focus_x=0.5, focus_y=0.5)
        tl_mod.add_speed_region(session, 3000, 4500, speed=1.5)
        tl_mod.add_trim_region(session, 0, 200)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            out_path = f.name
        try:
            result = export_mod.render(session, out_path)
            assert os.path.exists(out_path)
            assert result["file_size"] > 0
            assert result["width"] == 1920
            assert result["height"] == 1080
        finally:
            os.unlink(out_path)

    def test_export_no_video_raises(self):
        """Export fails if no source video is set."""
        s = Session()
        s.new_project()
        with pytest.raises(Exception):
            export_mod.render(s, "/tmp/out.mp4")

    def test_export_missing_video_raises(self):
        """Export fails if source video file is missing."""
        import tempfile as _tempfile
        with _tempfile.TemporaryDirectory() as tmp_dir:
            s = Session()
            s.new_project(video_path="/tmp/nonexistent_12345.mp4")
            with pytest.raises(Exception):
                export_mod.render(s, os.path.join(tmp_dir, "out.mp4"))
