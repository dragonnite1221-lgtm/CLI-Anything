# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import _make_project  # noqa: F401,E501


class TestFreeCAD11Features:
    """Tests for FreeCAD 1.1 new features across modules."""

    # -- Body: LocalCoordinateSystem --

    def test_local_coordinate_system_default(self):
        proj = _make_project()
        body = create_body(proj, name="LCSBody")
        feat = local_coordinate_system(proj, 0)
        assert feat["type"] == "local_coordinate_system"
        assert feat["position"] == [0.0, 0.0, 0.0]
        assert feat["x_axis"] == [1.0, 0.0, 0.0]
        assert feat["y_axis"] == [0.0, 1.0, 0.0]
        assert feat["z_axis"] == [0.0, 0.0, 1.0]

    def test_local_coordinate_system_custom_axes(self):
        proj = _make_project()
        create_body(proj, name="LCSBody2")
        feat = local_coordinate_system(
            proj, 0,
            position=[10.0, 20.0, 30.0],
            x_axis=[0.0, 1.0, 0.0],
            z_axis=[1.0, 0.0, 0.0],
        )
        assert feat["position"] == [10.0, 20.0, 30.0]
        assert feat["x_axis"] == [0.0, 1.0, 0.0]

    def test_local_coordinate_system_invalid_body(self):
        proj = _make_project()
        with pytest.raises(IndexError):
            local_coordinate_system(proj, 99)

    # -- Body: Datum attachment --

    def test_datum_plane_with_attachment(self):
        proj = _make_project()
        create_body(proj, name="DatumBody")
        feat = datum_plane(proj, 0, attachment_mode="flat_face",
                           attachment_refs=["Body.Face1"])
        assert feat["attachment_mode"] == "flat_face"
        assert feat["attachment_refs"] == ["Body.Face1"]

    def test_datum_line_with_attachment(self):
        proj = _make_project()
        create_body(proj, name="DatumBody2")
        feat = datum_line(proj, 0, attachment_mode="normal_to_edge",
                          attachment_refs=["Body.Edge1"])
        assert feat["attachment_mode"] == "normal_to_edge"

    def test_datum_point_with_attachment(self):
        proj = _make_project()
        create_body(proj, name="DatumBody3")
        feat = datum_point(proj, 0, attachment_mode="translate",
                           attachment_refs=["Body.Vertex1"])
        assert feat["attachment_mode"] == "translate"

    def test_datum_invalid_attachment_mode(self):
        proj = _make_project()
        create_body(proj, name="DatumBody4")
        with pytest.raises(ValueError, match="Invalid attachment_mode"):
            datum_plane(proj, 0, attachment_mode="nonexistent_mode")

    # -- Body: Hole Whitworth threads --

    def test_hole_whitworth_bsw(self):
        proj = _make_project()
        create_body(proj, name="HoleBody")
        sk = create_sketch(proj)
        add_line(proj, 0, [0, 0], [10, 0])
        close_sketch(proj, 0)
        pad(proj, 0, sketch_index=0, length=10.0)
        feat = hole_feature(proj, 0, sketch_index=0, diameter=6.0, depth=10.0,
                            threaded=True, thread_standard="BSW")
        assert feat["thread_standard"] == "BSW"

    def test_hole_npt_auto_taper(self):
        proj = _make_project()
        create_body(proj, name="HoleBody2")
        sk = create_sketch(proj)
        add_line(proj, 0, [0, 0], [10, 0])
        close_sketch(proj, 0)
        pad(proj, 0, sketch_index=0, length=10.0)
        feat = hole_feature(proj, 0, sketch_index=0, diameter=6.0, depth=10.0,
                            threaded=True, thread_standard="NPT", tapered=True)
        assert feat["tapered"] is True
        assert abs(feat["taper_angle"] - 1.7899) < 0.001

    def test_hole_invalid_thread_standard(self):
        proj = _make_project()
        create_body(proj, name="HoleBody3")
        sk = create_sketch(proj)
        add_line(proj, 0, [0, 0], [10, 0])
        close_sketch(proj, 0)
        pad(proj, 0, sketch_index=0, length=10.0)
        with pytest.raises(ValueError, match="Invalid thread_standard"):
            hole_feature(proj, 0, sketch_index=0, diameter=6.0, depth=10.0,
                         thread_standard="INVALID")

    # -- Body: Toggle freeze --

    def test_toggle_freeze(self):
        proj = _make_project()
        create_body(proj, name="FreezeBody")
        create_sketch(proj)
        add_line(proj, 0, [0, 0], [10, 0])
        close_sketch(proj, 0)
        pad(proj, 0, sketch_index=0, length=5.0)
        feat = toggle_freeze(proj, 0, 0)
        assert feat["frozen"] is True
        feat2 = toggle_freeze(proj, 0, 0)
        assert feat2["frozen"] is False

    def test_toggle_freeze_invalid_index(self):
        proj = _make_project()
        create_body(proj, name="FreezeBody2")
        with pytest.raises(IndexError):
            toggle_freeze(proj, 0, 99)
