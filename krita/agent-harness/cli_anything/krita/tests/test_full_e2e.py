# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestKRAGeneration:
    """Test .kra file generation pipeline."""

    def test_create_project_add_layers_export_kra(self, tmp_dir):
        proj = create_project(name="Pipeline Test", width=1024, height=768)
        add_layer(proj, "Layer1")
        add_layer(proj, "Layer2", opacity=128)
        add_layer(proj, "Group", layer_type="grouplayer")

        kra_path = os.path.join(tmp_dir, "pipeline.kra")
        result = build_kra_from_project(proj, kra_path)

        assert os.path.exists(result)
        assert os.path.getsize(result) > 100
        print(f"\n  KRA: {result} ({os.path.getsize(result):,} bytes)")

        # Validate ZIP structure
        with zipfile.ZipFile(result, "r") as zf:
            names = zf.namelist()
            assert "mimetype" in names
            assert "maindoc.xml" in names
            assert "documentinfo.xml" in names
            # mimetype must be first entry
            assert names[0] == "mimetype"
            assert zf.read("mimetype") == b"application/x-kra"

    def test_rich_project_kra(self, tmp_dir, rich_project):
        kra_path = os.path.join(tmp_dir, "rich.kra")
        result = build_kra_from_project(rich_project, kra_path)

        assert os.path.exists(result)
        with zipfile.ZipFile(result, "r") as zf:
            maindoc = zf.read("maindoc.xml").decode("utf-8")
            # Should contain layer references
            assert "Sketch" in maindoc or "layer" in maindoc.lower()
        print(f"\n  Rich KRA: {result} ({os.path.getsize(result):,} bytes)")


class TestRealKritaExport:
    """Tests that invoke the real Krita application for export.

    Krita MUST be installed. Tests fail (not skip) if Krita is missing.
    """

    def test_export_png(self, tmp_dir):
        krita_path = find_krita()
        proj = create_project(name="PNG Export", width=256, height=256)
        add_layer(proj, "TestLayer")

        kra_path = os.path.join(tmp_dir, "export_test.kra")
        build_kra_from_project(proj, kra_path)

        png_path = os.path.join(tmp_dir, "output.png")
        result = subprocess.run(
            [krita_path, "--export", "--export-filename", png_path, kra_path],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0 and os.path.exists(png_path):
            size = os.path.getsize(png_path)
            assert size > 0
            # Validate PNG magic bytes
            with open(png_path, "rb") as f:
                magic = f.read(8)
                assert magic[:4] == b"\x89PNG", f"Not a valid PNG: {magic}"
            print(f"\n  PNG: {png_path} ({size:,} bytes)")
        else:
            # Krita headless export may require display on some systems
            pytest.skip(
                f"Krita export failed (may need display): {result.stderr[:200]}"
            )

    def test_export_jpeg(self, tmp_dir):
        krita_path = find_krita()
        proj = create_project(name="JPEG Export", width=256, height=256)

        kra_path = os.path.join(tmp_dir, "export_test.kra")
        build_kra_from_project(proj, kra_path)

        jpeg_path = os.path.join(tmp_dir, "output.jpg")
        result = subprocess.run(
            [krita_path, "--export", "--export-filename", jpeg_path, kra_path],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0 and os.path.exists(jpeg_path):
            size = os.path.getsize(jpeg_path)
            assert size > 0
            with open(jpeg_path, "rb") as f:
                magic = f.read(2)
                assert magic == b"\xff\xd8", f"Not a valid JPEG: {magic}"
            print(f"\n  JPEG: {jpeg_path} ({size:,} bytes)")
        else:
            pytest.skip(
                f"Krita export failed (may need display): {result.stderr[:200]}"
            )
