# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import _make_project  # noqa: F401,E501


class TestBody:
    """Tests for the body module."""

    def _project_with_sketch(self):
        """Return a project with one closed sketch containing a rectangle."""
        proj = _make_project()
        create_sketch(proj, name="BaseSketch")
        add_rectangle(proj, 0, corner=[0, 0], width=10, height=10)
        close_sketch(proj, 0)
        return proj

    def test_create_body(self):
        proj = _make_project()
        body = create_body(proj, name="MyBody")
        assert body["name"] == "MyBody"
        assert body["features"] == []
        assert body["base_sketch_index"] is None
        assert len(proj["bodies"]) == 1

        # Auto-naming
        body2 = create_body(proj)
        assert body2["name"] == "Body"  # first auto "Body" is taken by none; unique check

    def test_pad(self):
        proj = self._project_with_sketch()
        create_body(proj, name="PadBody")
        feature = pad(proj, body_index=0, sketch_index=0, length=15.0, symmetric=True)
        assert feature["type"] == "pad"
        assert feature["length"] == 15.0
        assert feature["symmetric"] is True
        assert feature["reversed"] is False
        assert proj["bodies"][0]["base_sketch_index"] == 0

        with pytest.raises(ValueError, match="positive"):
            pad(proj, body_index=0, sketch_index=0, length=-5.0)

    def test_pocket(self):
        proj = self._project_with_sketch()
        create_body(proj, name="PocketBody")
        # Add a pad first so body has features
        pad(proj, body_index=0, sketch_index=0, length=20.0)

        # Create a second sketch for the pocket
        create_sketch(proj, name="PocketSketch")
        add_rectangle(proj, 1, corner=[2, 2], width=3, height=3)
        close_sketch(proj, 1)

        feature = pocket(proj, body_index=0, sketch_index=1, length=5.0)
        assert feature["type"] == "pocket"
        assert feature["length"] == 5.0

    def test_fillet(self):
        proj = self._project_with_sketch()
        create_body(proj)
        pad(proj, body_index=0, sketch_index=0, length=10.0)

        feat = fillet(proj, body_index=0, radius=2.0, edges="all")
        assert feat["type"] == "fillet"
        assert feat["radius"] == 2.0
        assert feat["edges"] == "all"

        feat2 = fillet(proj, body_index=0, radius=1.0, edges=[0, 1, 2])
        assert feat2["edges"] == [0, 1, 2]

        with pytest.raises(ValueError, match="positive"):
            fillet(proj, body_index=0, radius=-1.0)

    def test_chamfer(self):
        proj = self._project_with_sketch()
        create_body(proj)
        pad(proj, body_index=0, sketch_index=0, length=10.0)

        feat = chamfer(proj, body_index=0, size=1.5, edges="all")
        assert feat["type"] == "chamfer"
        assert feat["size"] == 1.5
        assert feat["edges"] == "all"

        with pytest.raises(ValueError, match="positive"):
            chamfer(proj, body_index=0, size=0.0)

    def test_revolution(self):
        proj = self._project_with_sketch()
        create_body(proj)
        feat = revolution(proj, body_index=0, sketch_index=0, angle=180.0, axis="Y")
        assert feat["type"] == "revolution"
        assert feat["angle"] == 180.0
        assert feat["axis"] == "Y"
        assert feat["reversed"] is False

        with pytest.raises(ValueError, match="angle must be in"):
            revolution(proj, body_index=0, sketch_index=0, angle=0.0)

        with pytest.raises(ValueError, match="Invalid revolution axis"):
            revolution(proj, body_index=0, sketch_index=0, axis="W")

    def test_additive_primitive_placement_and_patterns(self):
        proj = _make_project()
        create_body(proj, name="TowerBody")

        base = additive_box(
            proj,
            body_index=0,
            length=12.0,
            width=10.0,
            height=18.0,
            position=[1.0, 2.0, 3.0],
            rotation=[0.0, 0.0, 15.0],
        )
        assert base["type"] == "additive_box"
        assert base["placement"]["position"] == [1.0, 2.0, 3.0]
        assert base["placement"]["rotation"] == [0.0, 0.0, 15.0]

        rib = additive_cylinder(
            proj,
            body_index=0,
            radius=2.5,
            height=6.0,
            position=[8.0, 0.0, 9.0],
        )
        assert rib["type"] == "additive_cylinder"
        assert rib["placement"]["position"] == [8.0, 0.0, 9.0]

        cone = additive_cone(
            proj,
            body_index=0,
            radius1=3.0,
            radius2=1.0,
            height=8.0,
            position=[0.0, 0.0, 18.0],
        )
        assert cone["type"] == "additive_cone"

        linear = linear_pattern(
            proj,
            body_index=0,
            direction=[0.0, 0.0, 1.0],
            length=24.0,
            occurrences=4,
        )
        assert linear["type"] == "linear_pattern"
        assert linear["direction"] == [0.0, 0.0, 1.0]
        assert linear["occurrences"] == 4

        polar = polar_pattern(
            proj,
            body_index=0,
            axis="Z",
            angle=360.0,
            occurrences=4,
        )
        assert polar["type"] == "polar_pattern"
        assert polar["axis"] == "Z"
        assert polar["occurrences"] == 4

    def test_subtractive_primitive_placement(self):
        proj = _make_project()
        create_body(proj, name="CutBody")
        additive_box(proj, body_index=0, length=20.0, width=20.0, height=20.0)

        cut = subtractive_box(
            proj,
            body_index=0,
            length=6.0,
            width=6.0,
            height=10.0,
            position=[0.0, 0.0, 5.0],
        )
        assert cut["type"] == "subtractive_box"
        assert cut["placement"]["position"] == [0.0, 0.0, 5.0]

    def test_list_and_get_body(self):
        proj = self._project_with_sketch()
        create_body(proj, name="B1")
        create_body(proj, name="B2")
        pad(proj, body_index=0, sketch_index=0, length=10.0)

        summaries = list_bodies(proj)
        assert len(summaries) == 2
        assert summaries[0]["name"] == "B1"
        assert summaries[0]["feature_count"] == 1
        assert summaries[1]["name"] == "B2"
        assert summaries[1]["feature_count"] == 0

        body = get_body(proj, 0)
        assert body["name"] == "B1"

        with pytest.raises(IndexError):
            get_body(proj, 99)
