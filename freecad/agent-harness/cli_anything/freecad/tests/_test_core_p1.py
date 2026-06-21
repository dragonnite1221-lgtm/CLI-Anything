# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import _make_project  # noqa: F401,E501


class TestParts:
    """Tests for the parts module."""

    def test_add_box_defaults(self):
        proj = _make_project()
        part = add_part(proj, "box")
        assert part["type"] == "box"
        assert part["name"] == "Box"
        assert part["params"]["length"] == 10.0
        assert part["params"]["width"] == 10.0
        assert part["params"]["height"] == 10.0
        assert part["placement"]["position"] == [0.0, 0.0, 0.0]
        assert part["placement"]["rotation"] == [0.0, 0.0, 0.0]
        assert part["visible"] is True
        assert part["material_index"] is None
        assert len(proj["parts"]) == 1

    @pytest.mark.parametrize("ptype", ["box", "cylinder", "sphere", "cone", "torus", "wedge"])
    def test_add_all_primitives(self, ptype):
        proj = _make_project()
        part = add_part(proj, ptype)
        assert part["type"] == ptype
        # All default params from PRIMITIVES should be present
        for key in PRIMITIVES[ptype]:
            assert key in part["params"]
            assert part["params"][key] == PRIMITIVES[ptype][key]

    def test_add_with_position_rotation(self):
        proj = _make_project()
        part = add_part(proj, "box", position=[1.0, 2.0, 3.0], rotation=[45.0, 0.0, 90.0])
        assert part["placement"]["position"] == [1.0, 2.0, 3.0]
        assert part["placement"]["rotation"] == [45.0, 0.0, 90.0]

    def test_add_with_custom_params(self):
        proj = _make_project()
        part = add_part(proj, "box", params={"length": 20.0, "width": 5.0})
        assert part["params"]["length"] == 20.0
        assert part["params"]["width"] == 5.0
        assert part["params"]["height"] == 10.0  # default unchanged

    def test_add_invalid_type(self):
        proj = _make_project()
        with pytest.raises(ValueError, match="Unknown part_type"):
            add_part(proj, "hexagon")

    def test_part_bounds_reports_world_space_box(self):
        proj = _make_project()
        add_part(
            proj,
            "box",
            name="BoundsBox",
            params={"length": 20.0, "width": 8.0, "height": 6.0},
            position=[5.0, 10.0, 15.0],
        )
        bounds = part_bounds(proj, 0)
        assert bounds["local_bounding_box"]["min"] == {"x": 0.0, "y": 0.0, "z": 0.0}
        assert bounds["local_bounding_box"]["max"] == {"x": 20.0, "y": 8.0, "z": 6.0}
        assert bounds["world_bounding_box"]["min"] == {"x": 5.0, "y": 10.0, "z": 15.0}
        assert bounds["world_bounding_box"]["max"] == {"x": 25.0, "y": 18.0, "z": 21.0}

    def test_align_part_matches_bbox_faces(self):
        proj = _make_project()
        add_part(
            proj,
            "box",
            name="Base",
            params={"length": 20.0, "width": 10.0, "height": 6.0},
            position=[0.0, 0.0, 0.0],
        )
        add_part(
            proj,
            "box",
            name="Cap",
            params={"length": 8.0, "width": 6.0, "height": 4.0},
            position=[100.0, 50.0, 20.0],
        )

        result = align_part(
            proj,
            1,
            0,
            x="min",
            to_x="max",
            y="center",
            to_y="center",
            z="min",
            to_z="max",
        )

        assert result["placement"]["position"] == [20.0, 2.0, 6.0]
        aligned = part_bounds(proj, 1)["world_bounding_box"]
        target = part_bounds(proj, 0)["world_bounding_box"]
        assert aligned["min"]["x"] == pytest.approx(target["max"]["x"])
        assert aligned["center"]["y"] == pytest.approx(target["center"]["y"])
        assert aligned["min"]["z"] == pytest.approx(target["max"]["z"])

    def test_align_part_requires_supported_bounds(self):
        proj = _make_project()
        add_part(proj, "box", name="Base")
        add_part(
            proj,
            "cylinder",
            name="Tool",
            params={"radius": 2.0, "height": 12.0},
            position=[4.0, 4.0, -1.0],
        )
        boolean_op(proj, "cut", 0, 1, name="CutResult")
        with pytest.raises(ValueError, match="does not support bounding-box alignment"):
            align_part(proj, 2, 0, x="min", to_x="max")

    def test_remove_part(self):
        proj = _make_project()
        add_part(proj, "box", name="A")
        add_part(proj, "cylinder", name="B")
        assert len(proj["parts"]) == 2

        removed = remove_part(proj, 0)
        assert removed["name"] == "A"
        assert len(proj["parts"]) == 1
        assert proj["parts"][0]["name"] == "B"

    def test_remove_invalid_index(self):
        proj = _make_project()
        add_part(proj, "box")
        with pytest.raises(IndexError):
            remove_part(proj, 5)
        with pytest.raises(IndexError):
            remove_part(proj, -1)

    def test_list_parts(self):
        proj = _make_project()
        assert list_parts(proj) == []
        add_part(proj, "box", name="A")
        add_part(proj, "sphere", name="B")
        parts = list_parts(proj)
        assert len(parts) == 2
        assert parts[0]["name"] == "A"
        assert parts[1]["name"] == "B"

    def test_transform_part(self):
        proj = _make_project()
        add_part(proj, "box")
        updated = transform_part(proj, 0, position=[10.0, 20.0, 30.0])
        assert updated["placement"]["position"] == [10.0, 20.0, 30.0]
        # Rotation unchanged
        assert updated["placement"]["rotation"] == [0.0, 0.0, 0.0]

        updated2 = transform_part(proj, 0, rotation=[90.0, 0.0, 0.0])
        assert updated2["placement"]["rotation"] == [90.0, 0.0, 0.0]
        # Position unchanged from previous transform
        assert updated2["placement"]["position"] == [10.0, 20.0, 30.0]

    def test_boolean_cut(self):
        proj = _make_project()
        add_part(proj, "box", name="Base")
        add_part(proj, "cylinder", name="Tool")
        result = boolean_op(proj, "cut", 0, 1)

        assert result["type"] == "cut"
        assert result["params"]["base_id"] == proj["parts"][0]["id"]
        assert result["params"]["tool_id"] == proj["parts"][1]["id"]
        assert result["visible"] is True
        # Operands should be hidden
        assert proj["parts"][0]["visible"] is False
        assert proj["parts"][1]["visible"] is False
        assert len(proj["parts"]) == 3

    def test_boolean_fuse_common(self):
        proj = _make_project()
        add_part(proj, "box", name="A")
        add_part(proj, "box", name="B")

        fuse_result = boolean_op(proj, "fuse", 0, 1)
        assert fuse_result["type"] == "fuse"

        # Add two more for common test
        add_part(proj, "sphere", name="C")
        add_part(proj, "sphere", name="D")
        common_result = boolean_op(proj, "common", 3, 4)
        assert common_result["type"] == "common"

        with pytest.raises(ValueError, match="Unknown boolean op"):
            boolean_op(proj, "intersect", 0, 1)

        with pytest.raises(ValueError, match="must differ"):
            boolean_op(proj, "cut", 0, 0)
