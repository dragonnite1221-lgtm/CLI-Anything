# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import _make_project  # noqa: F401,E501


class TestSketch:
    """Tests for the sketch module."""

    def test_create_sketch(self):
        proj = _make_project()
        sk = create_sketch(proj, name="MySketch", plane="XZ", offset=5.0)
        assert sk["name"] == "MySketch"
        assert sk["plane"] == "XZ"
        assert sk["offset"] == 5.0
        assert sk["elements"] == []
        assert sk["constraints"] == []
        assert sk["closed"] is False
        assert len(proj["sketches"]) == 1

        # Invalid plane
        with pytest.raises(ValueError, match="Invalid plane"):
            create_sketch(proj, plane="AB")

    def test_add_line(self):
        proj = _make_project()
        create_sketch(proj)
        line = add_line(proj, 0, start=[0.0, 0.0], end=[10.0, 5.0])
        assert line["type"] == "line"
        assert line["start"] == [0.0, 0.0]
        assert line["end"] == [10.0, 5.0]
        assert len(proj["sketches"][0]["elements"]) == 1

    def test_add_circle(self):
        proj = _make_project()
        create_sketch(proj)
        circle = add_circle(proj, 0, center=[1.0, 2.0], radius=8.0)
        assert circle["type"] == "circle"
        assert circle["center"] == [1.0, 2.0]
        assert circle["radius"] == 8.0

        with pytest.raises(ValueError, match="positive"):
            add_circle(proj, 0, radius=-1.0)

    def test_add_rectangle(self):
        proj = _make_project()
        create_sketch(proj)
        result = add_rectangle(proj, 0, corner=[0.0, 0.0], width=20.0, height=10.0)

        assert result["type"] == "rectangle"
        assert len(result["line_ids"]) == 4
        assert len(result["constraint_ids"]) == 4
        assert result["width"] == 20.0
        assert result["height"] == 10.0

        # 4 line elements and 4 constraints should be in the sketch
        sk = proj["sketches"][0]
        assert len(sk["elements"]) == 4
        assert len(sk["constraints"]) == 4

    def test_add_arc(self):
        proj = _make_project()
        create_sketch(proj)
        arc = add_arc(proj, 0, center=[0.0, 0.0], radius=10.0, start_angle=0.0, end_angle=90.0)
        assert arc["type"] == "arc"
        assert arc["radius"] == 10.0
        assert arc["start_angle"] == 0.0
        assert arc["end_angle"] == 90.0
        # Check computed start/end points
        assert arc["start_point"][0] == pytest.approx(10.0)
        assert arc["start_point"][1] == pytest.approx(0.0)
        assert arc["end_point"][0] == pytest.approx(0.0, abs=1e-10)
        assert arc["end_point"][1] == pytest.approx(10.0)

    def test_add_constraint_distance(self):
        proj = _make_project()
        create_sketch(proj)
        line = add_line(proj, 0, start=[0.0, 0.0], end=[10.0, 0.0])

        constraint = add_constraint(
            proj, 0, constraint_type="distance", elements=[line["id"]], value=15.0
        )
        assert constraint["type"] == "distance"
        assert constraint["value"] == 15.0
        assert constraint["elements"] == [line["id"]]

        # Missing value for dimensional constraint
        with pytest.raises(ValueError, match="requires a numeric value"):
            add_constraint(proj, 0, constraint_type="distance", elements=[line["id"]])

        # Unknown constraint type
        with pytest.raises(ValueError, match="Unknown constraint type"):
            add_constraint(proj, 0, constraint_type="magical", elements=[line["id"]])

    def test_close_sketch(self):
        proj = _make_project()
        create_sketch(proj)
        add_line(proj, 0)

        closed = close_sketch(proj, 0)
        assert closed["closed"] is True

        # Cannot add elements to a closed sketch
        with pytest.raises(ValueError, match="closed sketch"):
            add_line(proj, 0)

        # Cannot close an already closed sketch
        with pytest.raises(ValueError, match="already closed"):
            close_sketch(proj, 0)

    def test_list_and_get_sketch(self):
        proj = _make_project()
        create_sketch(proj, name="S1", plane="XY")
        create_sketch(proj, name="S2", plane="YZ")
        add_line(proj, 0)

        summaries = list_sketches(proj)
        assert len(summaries) == 2
        assert summaries[0]["name"] == "S1"
        assert summaries[0]["plane"] == "XY"
        assert summaries[0]["element_count"] == 1
        assert summaries[1]["name"] == "S2"
        assert summaries[1]["plane"] == "YZ"

        sk = get_sketch(proj, 1)
        assert sk["name"] == "S2"

        with pytest.raises(IndexError):
            get_sketch(proj, 99)
