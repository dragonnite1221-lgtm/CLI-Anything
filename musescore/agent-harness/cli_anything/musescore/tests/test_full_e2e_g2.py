# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestCLISubprocess:
    def test_help(self):
        """Test --help flag."""
        cmd = _resolve_cli("cli-anything-musescore") + ["--help"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0
        assert "MuseScore CLI" in result.stdout or "musescore" in result.stdout.lower()
        print(f"  --help: OK ({len(result.stdout)} chars)")

    @requires_mscore
    @requires_samples
    def test_json_project_info(self):
        """Test --json project info via subprocess."""
        cmd = _resolve_cli("cli-anything-musescore") + [
            "--json",
            "project",
            "info",
            "-i",
            str(_SAMPLE_MXL),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "metadata" in data or "path" in data
        print(f"  JSON project info: OK")

    @requires_mscore
    @requires_samples
    def test_json_export_pdf(self):
        """Test --json export pdf via subprocess."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            out = f.name
        try:
            cmd = _resolve_cli("cli-anything-musescore") + [
                "--json",
                "export",
                "pdf",
                "-i",
                str(_SAMPLE_MXL),
                "-o",
                out,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert data.get("format") == "pdf"
            # Verify the output file
            assert os.path.isfile(out)
            with open(out, "rb") as f:
                header = f.read(5)
            assert header == b"%PDF-"
            print(f"  JSON export pdf: OK")
        finally:
            if os.path.exists(out):
                os.unlink(out)

    @requires_mscore
    @requires_samples
    def test_json_transpose_by_key(self):
        """Test --json transpose by-key via subprocess."""
        with tempfile.NamedTemporaryFile(suffix=".mscz", delete=False) as f:
            out = f.name
        try:
            cmd = _resolve_cli("cli-anything-musescore") + [
                "--json",
                "transpose",
                "by-key",
                "-i",
                str(_SAMPLE_MXL),
                "-o",
                out,
                "--target-key",
                "C major",
                "--direction",
                "closest",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert data.get("target_key_int") == 0
            print(f"  JSON transpose by-key: OK")
        finally:
            if os.path.exists(out):
                os.unlink(out)

    @requires_mscore
    @requires_samples
    def test_full_workflow(self):
        """Test a full workflow: info → transpose → export PDF → verify."""
        with tempfile.TemporaryDirectory() as tmpdir:
            transposed = os.path.join(tmpdir, "transposed.mscz")
            pdf_out = os.path.join(tmpdir, "output.pdf")

            # 1. Transpose G → C
            cmd = _resolve_cli("cli-anything-musescore") + [
                "--json",
                "transpose",
                "by-key",
                "-i",
                str(_SAMPLE_MXL),
                "-o",
                transposed,
                "--target-key",
                "C major",
            ]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            assert r.returncode == 0, f"Transpose failed: {r.stderr}"

            # 2. Export to PDF
            cmd = _resolve_cli("cli-anything-musescore") + [
                "--json",
                "export",
                "pdf",
                "-i",
                transposed,
                "-o",
                pdf_out,
            ]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            assert r.returncode == 0, f"Export failed: {r.stderr}"

            # 3. Verify PDF
            with open(pdf_out, "rb") as f:
                assert f.read(5) == b"%PDF-"

            print(f"  Full workflow: transpose → export → verify: OK")
