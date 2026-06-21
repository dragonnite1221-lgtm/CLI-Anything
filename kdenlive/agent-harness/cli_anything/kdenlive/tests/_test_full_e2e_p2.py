# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class TestMeltRenderE2E:
    """True E2E tests: render videos using melt."""

    def test_render_color_bars_mp4(self):
        """Render a color bars test video."""
        from cli_anything.kdenlive.utils.melt_backend import render_color_bars

        with tempfile.TemporaryDirectory() as tmp_dir:
            output = os.path.join(tmp_dir, "test.mp4")
            result = render_color_bars(output, duration=2, width=320, height=240)

            assert os.path.exists(result["output"])
            assert result["file_size"] > 0
            print(f"\n  Color bars MP4: {result['output']} ({result['file_size']:,} bytes)")

    def test_render_generated_mlt_xml(self):
        """Generate Kdenlive MLT XML from project and render it."""
        from cli_anything.kdenlive.utils.melt_backend import find_melt

        melt = find_melt()

        with tempfile.TemporaryDirectory() as tmp_dir:
            mlt_content = '''<?xml version="1.0" encoding="utf-8"?>
<mlt LC_NUMERIC="C" version="7.0.0" profile="atsc_720p_25">
  <profile description="HD 720p 25fps" width="320" height="240" progressive="1"
           sample_aspect_num="1" sample_aspect_den="1"
           display_aspect_num="4" display_aspect_den="3"
           frame_rate_num="25" frame_rate_den="1" colorspace="709"/>
  <producer id="color0" in="0" out="49">
    <property name="resource">color:green</property>
    <property name="mlt_service">color</property>
  </producer>
  <playlist id="playlist0">
    <entry producer="color0" in="0" out="49"/>
  </playlist>
  <tractor id="tractor0">
    <track producer="playlist0"/>
  </tractor>
</mlt>'''
            mlt_path = os.path.join(tmp_dir, "kdenlive_test.mlt")
            output_path = os.path.join(tmp_dir, "rendered.mp4")

            with open(mlt_path, 'w') as f:
                f.write(mlt_content)

            import subprocess
            cmd = [melt, mlt_path, "-consumer", f"avformat:{output_path}",
                   "vcodec=libx264", "acodec=aac", "ar=48000", "channels=2"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            assert result.returncode == 0, f"melt failed: {result.stderr[-500:]}"
            assert os.path.exists(output_path)
            size = os.path.getsize(output_path)
            assert size > 0
            print(f"\n  Kdenlive MLT render: {output_path} ({size:,} bytes)")
