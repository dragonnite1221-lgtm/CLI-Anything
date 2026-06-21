# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestKdenliveGen5FormatMixin1:
    def test_guides_in_sequence_tractor(self):
        root = self._parse()
        seq = _find_sequence(root)
        guides_prop = seq.find("property[@name='kdenlive:sequenceproperties.guides']")
        assert guides_prop is not None
        data = json.loads(guides_prop.text)
        assert len(data) == 1
        assert data[0]["comment"] == "Marker"
    def test_empty_project_has_gen5_structure(self):
        proj = create_project()
        root = ET.fromstring(generate_kdenlive_xml(proj))
        assert root.get("producer") == "main_bin"
        assert root.find(".//playlist[@id='main_bin']") is not None
        assert root.find(".//tractor[@id='tractor_project']") is not None
        assert _find_sequence(root) is not None
    def test_no_kdenlivedoc_element(self):
        xml = generate_kdenlive_xml(self._make_simple_project())
        assert "<kdenlivedoc>" not in xml
    def test_project_tractor_is_last_element(self):
        root = self._parse()
        last = root[-1]
        assert last.get("id") == "tractor_project"
    def test_black_track_producer_exists(self):
        root = self._parse()
        black = root.find("producer[@id='producer0']")
        assert black is not None
        resource = black.find("property[@name='resource']")
        assert resource.text == "black"
    def test_bin_clip_chains_use_avformat(self):
        root = self._parse()
        # Bin chains are listed in main_bin entries with chainN ids
        main_bin = root.find(".//playlist[@id='main_bin']")
        bin_producers = [e.get("producer") for e in main_bin.findall("entry")
                         if e.get("producer", "").startswith("chain")]
        for prod_id in bin_producers:
            chain = root.find(f".//chain[@id='{prod_id}']")
            assert chain is not None
            svc = chain.find("property[@name='mlt_service']")
            assert svc is not None
            assert svc.text == "avformat-novalidate"
    def test_audio_track_tractor_has_internal_filters(self):
        root = self._parse()
        tractor1 = root.find(".//tractor[@id='tractor1']")
        filters = tractor1.findall("filter")
        services = [f.find("property[@name='mlt_service']") for f in filters]
        services = [s.text for s in services if s is not None]
        assert "volume" in services
        assert "panner" in services
        assert "audiolevel" in services
    def test_main_bin_has_xml_retain(self):
        root = self._parse()
        main_bin = root.find(".//playlist[@id='main_bin']")
        retain = main_bin.find("property[@name='xml_retain']")
        assert retain is not None
        assert retain.text == "1"
    def test_render_gen5_xml_through_melt(self):
        from cli_anything.kdenlive.utils.melt_backend import find_melt
        import subprocess

        melt = find_melt()

        with tempfile.TemporaryDirectory() as tmp_dir:
            mlt_path = os.path.join(tmp_dir, "gen5_test.kdenlive")
            output_path = os.path.join(tmp_dir, "rendered.mp4")

            proj = create_project(name="Gen5MeltTest", profile="hd1080p30")
            import_clip(proj, "color:red", name="Red", duration=2.0)
            add_track(proj, track_type="video")
            add_clip_to_track(proj, 0, "clip0", out_point=2.0)

            xml = generate_kdenlive_xml(proj)
            with open(mlt_path, 'w') as f:
                f.write(xml)

            ET.fromstring(xml)

            cmd = [melt, mlt_path, "-consumer", f"avformat:{output_path}",
                   "vcodec=libx264", "acodec=aac", "ar=48000", "channels=2"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            assert result.returncode == 0, f"melt failed: {result.stderr[-500:]}"
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
