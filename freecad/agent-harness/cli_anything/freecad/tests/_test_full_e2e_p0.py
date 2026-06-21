# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


@pytest.mark.skipif(not _has_freecad(), reason="FreeCAD not installed")
class TestFreeCADBackend:
    """Tests that require the real FreeCAD headless backend."""

    def test_find_freecad(self):
        """Verify that find_freecad returns a valid path."""
        from cli_anything.freecad.utils.freecad_backend import find_freecad

        path = find_freecad()
        assert os.path.isfile(path), f"FreeCAD not found at: {path}"
        print(f"\n  FreeCAD found: {path}")

    def test_get_version(self):
        """Verify that get_version returns a version string."""
        from cli_anything.freecad.utils.freecad_backend import get_version

        version = get_version()
        assert isinstance(version, str)
        assert len(version) > 0
        # Should contain at least one digit and a dot
        assert any(c.isdigit() for c in version), f"No digits in version: {version}"
        print(f"\n  FreeCAD version: {version}")

    def test_export_box_step(self, tmp_path):
        """Create a project with a box, export to STEP, validate format."""
        proj = create_document(name="StepExport")
        add_part(proj, "box", name="ExportBox",
                 params={"length": 20, "width": 15, "height": 10})

        output = str(tmp_path / "box.step")
        result = export_project(proj, output, preset="step")

        assert os.path.isfile(output)
        size = os.path.getsize(output)
        assert size > 0, "STEP file is empty"

        # Validate STEP header
        with open(output, "r", encoding="utf-8", errors="ignore") as f:
            header = f.read(64)
        assert header.strip().startswith("ISO-10303-21"), (
            f"Invalid STEP header: {header[:40]!r}"
        )

        print(f"\n  STEP: {output} ({size:,} bytes)")

    def test_export_multi_part_stl(self, tmp_path):
        """Export multiple parts to STL, validate format."""
        proj = create_document(name="StlExport")
        add_part(proj, "box", name="Block",
                 params={"length": 10, "width": 10, "height": 10})
        add_part(proj, "cylinder", name="Rod",
                 params={"radius": 3, "height": 20},
                 position=[15, 0, 0])

        output = str(tmp_path / "multi.stl")
        result = export_project(proj, output, preset="stl")

        assert os.path.isfile(output)
        size = os.path.getsize(output)
        assert size > 0, "STL file is empty"

        # Validate STL: ASCII starts with "solid", binary has 80-byte header
        with open(output, "rb") as f:
            head = f.read(80)

        text_head = head.decode("ascii", errors="ignore").strip().lower()
        is_ascii = text_head.startswith("solid")

        is_binary = False
        if not is_ascii:
            with open(output, "rb") as f:
                f.seek(80)
                count_bytes = f.read(4)
                if len(count_bytes) == 4:
                    tri_count = struct.unpack("<I", count_bytes)[0]
                    is_binary = tri_count > 0

        assert is_ascii or is_binary, "File is neither ASCII nor binary STL"

        fmt = "ASCII" if is_ascii else "binary"
        print(f"\n  STL ({fmt}): {output} ({size:,} bytes)")

    def test_export_fcstd(self, tmp_path):
        """Export to native FCStd format."""
        proj = create_document(name="FcstdExport")
        add_part(proj, "box", name="NativeBox",
                 params={"length": 25, "width": 25, "height": 25})

        output = str(tmp_path / "native.FCStd")
        result = export_project(proj, output, preset="fcstd")

        assert os.path.isfile(output)
        size = os.path.getsize(output)
        assert size > 0, "FCStd file is empty"

        print(f"\n  FCStd: {output} ({size:,} bytes)")

    @pytest.mark.skipif(not _has_freecad_preview(), reason="GUI-capable FreeCAD not installed")
    def test_preview_capture_bundle(self, tmp_path):
        proj = create_document(name="PreviewPart")
        add_part(proj, "box", name="MainBlock", params={"length": 30, "width": 20, "height": 12})
        add_part(
            proj,
            "cylinder",
            name="SideBoss",
            params={"radius": 4, "height": 14},
            position=[18, 0, 0],
        )

        project_path = str(tmp_path / "preview.json")
        save_document(proj, project_path)

        sess = Session()
        sess.set_project(proj, path=project_path)

        manifest = preview_mod.capture(sess, root_dir=str(tmp_path), force=True)
        assert manifest["software"] == "freecad"
        assert manifest["bundle_kind"] == "capture"
        assert manifest["status"] in ("ok", "partial")

        hero_path = _artifact_path(manifest, "hero")
        front_path = _artifact_path(manifest, "front")
        top_path = _artifact_path(manifest, "top")
        right_path = _artifact_path(manifest, "right")
        _assert_png(hero_path)
        _assert_png(front_path)
        _assert_png(top_path)
        _assert_png(right_path)

        latest = preview_mod.latest(project_path=project_path, recipe="quick", root_dir=str(tmp_path))
        assert latest["bundle_id"] == manifest["bundle_id"]

        print(f"\n  FreeCAD preview bundle: {manifest['_bundle_dir']}")
        print(f"  FreeCAD preview hero: {hero_path}")
        print(f"  FreeCAD preview front: {front_path}")
        print(f"  FreeCAD preview top: {top_path}")
        print(f"  FreeCAD preview right: {right_path}")

    @pytest.mark.skipif(not _has_freecad_preview(), reason="GUI-capable FreeCAD not installed")
    def test_preview_capture_bundle_body_patterns(self, tmp_path):
        proj = create_document(name="PreviewBodyTower")
        create_body(proj, name="TowerBody")
        additive_box(proj, 0, length=34, width=34, height=18, position=[0, 0, 0])
        additive_box(proj, 0, length=8, width=6, height=4, position=[21, 0, 7])
        polar_pattern(proj, 0, axis="Z", angle=360, occurrences=4)
        additive_box(proj, 0, length=30, width=30, height=16, position=[0, 0, 18])
        additive_box(proj, 0, length=7, width=5, height=3, position=[18.5, 0, 24])
        polar_pattern(proj, 0, axis="Z", angle=360, occurrences=4)
        additive_cylinder(proj, 0, radius=2.2, height=18, position=[0, 0, 34])
        additive_cone(proj, 0, radius1=2.5, radius2=0.4, height=10, position=[0, 0, 52])

        project_path = str(tmp_path / "preview_body.json")
        save_document(proj, project_path)

        sess = Session()
        sess.set_project(proj, path=project_path)

        manifest = preview_mod.capture(sess, root_dir=str(tmp_path), force=True)
        assert manifest["software"] == "freecad"
        assert manifest["bundle_kind"] == "capture"
        assert manifest["status"] in ("ok", "partial")

        hero_path = _artifact_path(manifest, "hero")
        front_path = _artifact_path(manifest, "front")
        _assert_png_not_blank(hero_path)
        _assert_png_not_blank(front_path)

        print(f"\n  FreeCAD body preview bundle: {manifest['_bundle_dir']}")
        print(f"  FreeCAD body preview hero: {hero_path}")
        print(f"  FreeCAD body preview front: {front_path}")
