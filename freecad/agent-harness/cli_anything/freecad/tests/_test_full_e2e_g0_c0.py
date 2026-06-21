# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestIntermediateFilesMixin0:
    """Verify project creation, manipulation, and macro generation
    using only the Python API -- no FreeCAD binary needed."""
    def test_full_project_json_structure(self, tmp_path):
        """Create a complex project and verify the JSON schema."""
        proj = create_document(name="StructureTest", units="mm")

        # Add varied parts
        add_part(proj, "box", name="MainBox", params={"length": 30, "width": 20, "height": 15})
        add_part(proj, "cylinder", name="Shaft", params={"radius": 3, "height": 50})
        add_part(proj, "sphere", name="Ball", params={"radius": 8})

        # Add a sketch with elements
        create_sketch(proj, name="BaseSketch", plane="XY")
        add_rectangle(proj, 0, corner=[0, 0], width=20, height=10)

        # Add a body with a pad
        create_body(proj, name="MainBody")
        pad(proj, 0, 0, length=15)

        # Add a material
        create_material(proj, preset="steel")

        # Save and reload
        path = str(tmp_path / "structure.json")
        save_document(proj, path)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Top-level keys
        required_keys = {"version", "name", "units", "parts", "sketches",
                         "bodies", "materials", "metadata"}
        assert required_keys.issubset(data.keys()), (
            f"Missing keys: {required_keys - set(data.keys())}"
        )

        assert data["name"] == "StructureTest"
        assert data["units"] == "mm"
        assert data["version"] == "1.0"
        assert len(data["parts"]) == 3
        assert len(data["sketches"]) == 1
        assert len(data["bodies"]) == 1
        assert len(data["materials"]) == 1

        # Verify part structure
        box = data["parts"][0]
        assert box["type"] == "box"
        assert box["name"] == "MainBox"
        assert box["params"]["length"] == 30.0
        assert "placement" in box
        assert box["placement"]["position"] == [0.0, 0.0, 0.0]

        # Metadata
        assert "created" in data["metadata"]
        assert "modified" in data["metadata"]
        assert "software" in data["metadata"]

        print(f"\n  JSON structure validated: {path} ({os.path.getsize(path):,} bytes)")
    def test_multi_part_boolean_workflow(self):
        """Parts + booleans + materials, verify all state is consistent."""
        proj = create_document(name="BooleanTest")

        # Add base and tool
        box = add_part(proj, "box", name="Base", params={"length": 20, "width": 20, "height": 20})
        cyl = add_part(proj, "cylinder", name="Hole",
                       params={"radius": 5, "height": 30},
                       position=[10, 10, -5])

        assert len(list_parts(proj)) == 2
        assert box["id"] == 1
        assert cyl["id"] == 2

        # Boolean cut
        cut_result = boolean_op(proj, "cut", base_index=0, tool_index=1, name="CutResult")
        assert cut_result["type"] == "cut"
        assert cut_result["params"]["base_id"] == box["id"]
        assert cut_result["params"]["tool_id"] == cyl["id"]
        assert cut_result["visible"] is True

        # Source parts should now be hidden
        assert get_part(proj, 0)["visible"] is False
        assert get_part(proj, 1)["visible"] is False

        # Total parts now 3 (box, cylinder, cut-result)
        assert len(list_parts(proj)) == 3

        # Create material and assign to cut result
        mat = create_material(proj, preset="aluminum")
        assignment = assign_material(proj, material_index=0, part_index=2)
        assert assignment["material"] == mat["name"]
        assert assignment["part"] == "CutResult"

        # Verify material assignment on part
        cut_part = get_part(proj, 2)
        assert cut_part["material_index"] == 0

        # Verify material tracking
        materials = list_materials(proj)
        assert len(materials) == 1
        assert 2 in materials[0]["assigned_to"]

        print("\n  Boolean workflow verified: 2 primitives + cut + material assignment")
