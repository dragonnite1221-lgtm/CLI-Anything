# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import session, video  # noqa: F401,E501


class TestMeltRenderE2E:
    def test_render_color_bars_mp4(self):
        from cli_anything.shotcut.utils.melt_backend import render_color_bars

        with tempfile.TemporaryDirectory() as tmp_dir:
            output = os.path.join(tmp_dir, "test.mp4")
            result = render_color_bars(output, duration=2, width=320, height=240)

            assert os.path.exists(result["output"])
            assert result["file_size"] > 0
            assert result["method"] == "melt"

    def test_render_mlt_xml_file(self):
        from cli_anything.shotcut.utils.melt_backend import find_melt

        melt = find_melt()

        with tempfile.TemporaryDirectory() as tmp_dir:
            mlt_content = '''<?xml version="1.0" encoding="utf-8"?>
<mlt LC_NUMERIC="C" version="7.0.0" root="/tmp" profile="atsc_720p_25">
  <profile description="HD 720p 25fps" width="320" height="240" progressive="1"
           sample_aspect_num="1" sample_aspect_den="1"
           display_aspect_num="4" display_aspect_den="3"
           frame_rate_num="25" frame_rate_den="1" colorspace="709"/>
  <producer id="producer0" in="0" out="49">
    <property name="resource">color:blue</property>
    <property name="mlt_service">color</property>
  </producer>
  <producer id="producer1" in="0" out="49">
    <property name="resource">color:red</property>
    <property name="mlt_service">color</property>
  </producer>
  <playlist id="playlist0">
    <entry producer="producer0" in="0" out="49"/>
    <entry producer="producer1" in="0" out="49"/>
  </playlist>
  <tractor id="tractor0" in="0" out="99">
    <track producer="playlist0"/>
  </tractor>
</mlt>'''
            mlt_path = os.path.join(tmp_dir, "test.mlt")
            output_path = os.path.join(tmp_dir, "output.mp4")

            with open(mlt_path, 'w') as f:
                f.write(mlt_content)

            cmd = [
                melt, mlt_path,
                "-consumer", f"avformat:{output_path}",
                "vcodec=libx264", "acodec=aac",
                "ar=48000", "channels=2",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            assert result.returncode == 0, f"melt failed: {result.stderr[-500:]}"
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

    def test_render_imported_media_is_not_black(self, session, video):
        if shutil.which("ffmpeg") is None:
            pytest.skip("ffmpeg is required for frame extraction")

        tl_mod.add_track(session, "video", "V1")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:01.000")

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "render.mp4")
            frame_path = os.path.join(tmp_dir, "frame.png")

            result = export_mod.render(session, output_path, "default", overwrite=True)
            assert result["method"] == "melt"
            assert os.path.exists(output_path)

            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-ss",
                    "00:00:00.500",
                    "-i",
                    output_path,
                    "-frames:v",
                    "1",
                    frame_path,
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
            mean = ImageStat.Stat(Image.open(frame_path).convert("RGB")).mean
            assert max(mean) > 5, f"Rendered frame appears black: {mean}"
