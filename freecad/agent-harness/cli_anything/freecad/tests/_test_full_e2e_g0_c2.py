# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestIntermediateFilesMixin2:
    def test_save_load_roundtrip(self, tmp_path):
        """Save a project, reload it, verify contents are identical."""
        proj = create_document(name="RoundTrip", units="in", profile="imperial")

        add_part(proj, "box", name="BlockA", params={"length": 5, "width": 5, "height": 5})
        add_part(proj, "cone", name="ConeB",
                 params={"radius1": 3, "radius2": 1, "height": 8})

        create_sketch(proj, name="ProfileSketch", plane="XZ")
        add_line(proj, 0, start=[0, 0], end=[10, 0])
        add_circle(proj, 0, center=[5, 5], radius=3)

        create_material(proj, name="CustomMat", color=[0.5, 0.3, 0.1, 1.0],
                        metallic=0.7, roughness=0.4)
        assign_material(proj, 0, 0)

        path = str(tmp_path / "roundtrip.json")
        save_document(proj, path)

        # Reload
        loaded = open_document(path)

        # Compare key fields (metadata.modified will differ slightly, so skip it)
        assert loaded["name"] == proj["name"]
        assert loaded["units"] == proj["units"]
        assert loaded["version"] == proj["version"]
        assert len(loaded["parts"]) == len(proj["parts"])
        assert len(loaded["sketches"]) == len(proj["sketches"])
        assert len(loaded["bodies"]) == len(proj["bodies"])
        assert len(loaded["materials"]) == len(proj["materials"])

        # Deep-compare parts
        for i, (orig, reloaded) in enumerate(zip(proj["parts"], loaded["parts"])):
            assert orig["name"] == reloaded["name"], f"Part {i} name mismatch"
            assert orig["type"] == reloaded["type"], f"Part {i} type mismatch"
            assert orig["params"] == reloaded["params"], f"Part {i} params mismatch"

        # Deep-compare sketches
        for i, (orig, reloaded) in enumerate(zip(proj["sketches"], loaded["sketches"])):
            assert orig["name"] == reloaded["name"], f"Sketch {i} name mismatch"
            assert orig["plane"] == reloaded["plane"], f"Sketch {i} plane mismatch"
            assert len(orig["elements"]) == len(reloaded["elements"])

        print(f"\n  Round-trip verified: {path} ({os.path.getsize(path):,} bytes)")
