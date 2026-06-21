# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import session, video  # noqa: F401,E501


class TestChainLengthRegression:
    """Regression tests for the chain length bug that caused melt to hang.

    When add_clip creates a sub-clip (in > 0 or out < duration), the chain's
    ``length`` property must equal the source file duration, not the clip's
    out_point. Otherwise melt enters an infinite loop on playback.
    """

    def test_timeline_chain_length_equals_source_duration(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1,
                        in_point="00:00:01.000", out_point="00:00:03.000")

        with tempfile.NamedTemporaryFile(suffix=".mlt", delete=False) as f:
            path = f.name
        try:
            proj_mod.save_project(session, path)

            import xml.etree.ElementTree as ET
            tree = ET.parse(path)
            root = tree.getroot()

            bin_chain = None
            for chain in root.findall(".//chain"):
                res = get_property(chain, "resource") or ""
                if video in res and get_property(chain, "mlt_service") == "avformat-novalidate":
                    bin_chain = chain
                    break

            assert bin_chain is not None, "Bin chain not found"
            bin_out = bin_chain.get("out")

            for chain in root.findall(".//chain"):
                res = get_property(chain, "resource") or ""
                if video not in res:
                    continue
                if get_property(chain, "mlt_service") != "avformat-novalidate":
                    continue
                if chain.get("id") == bin_chain.get("id"):
                    continue

                chain_out = chain.get("out")
                assert chain_out == bin_out, \
                    f"Chain {chain.get('id')}: out={chain_out} != source out {bin_out}"

            # Verify playlist entry has the subclip range
            for pl in root.findall(".//playlist"):
                if pl.get("id") in ("main_bin", "background"):
                    continue
                for entry in pl.findall("entry"):
                    assert entry.get("in") == "00:00:01.000", \
                        f"Entry in should be subclip start, got {entry.get('in')}"
                    assert entry.get("out") == "00:00:03.000", \
                        f"Entry out should be subclip end, got {entry.get('out')}"
        finally:
            os.unlink(path)

    def test_melt_can_load_subclip_project(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1,
                        in_point="00:00:02.000", out_point="00:00:04.000")

        with tempfile.NamedTemporaryFile(suffix=".mlt", delete=False) as f:
            path = f.name
        try:
            proj_mod.save_project(session, path)

            try:
                from cli_anything.shotcut.utils.melt_backend import find_melt
                melt = find_melt()
            except (ImportError, FileNotFoundError):
                pytest.skip("melt not available")

            result = subprocess.run(
                [melt, path, "-consumer", "null", "-silent"],
                capture_output=True, text=True, timeout=10,
            )
            assert result.returncode == 0, \
                f"melt failed with exit code {result.returncode}: {result.stderr[-500:]}"
        finally:
            os.unlink(path)

    def test_melt_multiple_subclips_no_loop(self, session, video):
        """Regression: melt must not infinite-loop when a video is subclipped
        into many pieces across multiple tracks.

        The chain element's in/out must span the full source duration;
        only playlist entry in/out defines the subclip range.  If the chain
        out is set to the clip end instead, melt will loop.
        """
        tl_mod.add_track(session, "video")
        tl_mod.add_track(session, "audio")

        clip_id = media_mod.import_media(session, video)["clip_id"]
        # 10 subclips covering the first 8 seconds of the test video
        for i in range(10):
            start = i * 0.8
            end = start + 0.8
            in_tc = f"00:00:00.{int(start*1000):03d}"
            out_tc = f"00:00:00.{int(end*1000):03d}"
            tl_mod.add_clip(session, clip_id, 1, in_tc, out_tc)
            tl_mod.add_clip(session, clip_id, 2, in_tc, out_tc)

        with tempfile.NamedTemporaryFile(suffix=".mlt", delete=False) as f:
            path = f.name
        try:
            proj_mod.save_project(session, path)

            try:
                from cli_anything.shotcut.utils.melt_backend import find_melt
                melt = find_melt()
            except (ImportError, FileNotFoundError):
                pytest.skip("melt not available")

            # 15-second timeout: 8s of content + margin; infinite loop would timeout
            result = subprocess.run(
                [melt, path, "-consumer", "null", "-silent"],
                capture_output=True, text=True, timeout=15,
            )
            assert result.returncode == 0, \
                f"melt failed with exit code {result.returncode}: {result.stderr[-500:]}"
        finally:
            os.unlink(path)
