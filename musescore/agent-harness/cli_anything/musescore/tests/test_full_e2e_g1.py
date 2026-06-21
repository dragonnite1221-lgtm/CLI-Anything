# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


@requires_mscore
@requires_samples
class TestPartsE2E:
    def test_list_parts(self):
        """List parts in the sample score."""
        from cli_anything.musescore.core.parts import list_parts

        parts = list_parts(str(_SAMPLE_MXL))
        assert len(parts) >= 1
        print(f"  Parts: {[p['name'] for p in parts]}")

    def test_extract_part(self):
        """Extract the first part."""
        from cli_anything.musescore.core.parts import list_parts, extract_part

        parts = list_parts(str(_SAMPLE_MXL))
        if not parts:
            pytest.skip("No parts found")

        first_part = parts[0]["name"]
        with tempfile.NamedTemporaryFile(suffix=".mscz", delete=False) as f:
            out = f.name
        try:
            result = extract_part(str(_SAMPLE_MXL), first_part, out)
            assert os.path.isfile(out)
            assert result["size_bytes"] > 0
            print(f"  Extracted '{first_part}': {result['size_bytes']} bytes")
        finally:
            if os.path.exists(out):
                os.unlink(out)


@requires_mscore
@requires_samples
class TestMediaE2E:
    def test_probe_mxl(self):
        """Probe sample MXL file."""
        from cli_anything.musescore.core.media import probe_score

        result = probe_score(str(_SAMPLE_MXL))
        assert result["format"] == "mxl"
        assert "metadata" in result
        print(
            f"  Probe: {json.dumps(result.get('metadata', {}), indent=2, default=str)[:200]}"
        )

    def test_probe_mscz(self):
        """Probe sample MSCZ file."""
        from cli_anything.musescore.core.media import probe_score

        result = probe_score(str(_SAMPLE_MSCZ))
        assert result["format"] == "mscz"
        assert "metadata" in result

    def test_stats_mxl(self):
        """Get stats for sample MXL file."""
        from cli_anything.musescore.core.media import score_stats

        result = score_stats(str(_SAMPLE_MXL))
        assert "stats" in result
        assert result["stats"]["measures"] > 0
        assert result["stats"]["notes"] > 0
        print(f"  Stats: {result['stats']}")
