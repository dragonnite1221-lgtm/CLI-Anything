# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestGradients:
    def _make_doc(self):
        return create_document()

    def test_add_linear_gradient(self):
        proj = self._make_doc()
        grad = add_linear_gradient(proj)
        assert grad["type"] == "linear"
        assert len(grad["stops"]) == 2
        assert len(proj["gradients"]) == 1

    def test_add_linear_gradient_custom_stops(self):
        proj = self._make_doc()
        stops = [
            {"offset": 0, "color": "#ff0000"},
            {"offset": 0.5, "color": "#00ff00"},
            {"offset": 1, "color": "#0000ff"},
        ]
        grad = add_linear_gradient(proj, stops=stops)
        assert len(grad["stops"]) == 3

    def test_add_radial_gradient(self):
        proj = self._make_doc()
        grad = add_radial_gradient(proj, cx=0.5, cy=0.5, r=0.5)
        assert grad["type"] == "radial"
        assert grad["cx"] == 0.5

    def test_gradient_invalid_stops(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="at least 2"):
            add_linear_gradient(proj, stops=[{"offset": 0, "color": "#000"}])

    def test_gradient_missing_offset(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="missing 'offset'"):
            add_linear_gradient(
                proj,
                stops=[
                    {"color": "#000"},
                    {"offset": 1, "color": "#fff"},
                ],
            )

    def test_gradient_invalid_offset(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="0-1"):
            add_linear_gradient(
                proj,
                stops=[
                    {"offset": -0.5, "color": "#000"},
                    {"offset": 1, "color": "#fff"},
                ],
            )

    def test_apply_gradient_fill(self):
        proj = self._make_doc()
        add_rect(proj, name="Shape")
        add_linear_gradient(proj, name="MyGrad")
        result = apply_gradient(proj, 0, 0, "fill")
        style = parse_style(proj["objects"][0]["style"])
        assert "url(#" in style["fill"]

    def test_apply_gradient_stroke(self):
        proj = self._make_doc()
        add_rect(proj, name="Shape")
        add_linear_gradient(proj, name="MyGrad")
        result = apply_gradient(proj, 0, 0, "stroke")
        style = parse_style(proj["objects"][0]["style"])
        assert "url(#" in style["stroke"]

    def test_apply_gradient_invalid_target(self):
        proj = self._make_doc()
        add_rect(proj)
        add_linear_gradient(proj)
        with pytest.raises(ValueError, match="fill.*stroke"):
            apply_gradient(proj, 0, 0, "background")

    def test_list_gradients(self):
        proj = self._make_doc()
        add_linear_gradient(proj, name="A")
        add_radial_gradient(proj, name="B")
        result = list_gradients(proj)
        assert len(result) == 2

    def test_get_gradient(self):
        proj = self._make_doc()
        add_linear_gradient(proj, name="Test")
        grad = get_gradient(proj, 0)
        assert grad["name"] == "Test"

    def test_remove_gradient(self):
        proj = self._make_doc()
        add_linear_gradient(proj, name="ToRemove")
        removed = remove_gradient(proj, 0)
        assert removed["name"] == "ToRemove"
        assert len(proj["gradients"]) == 0

    def test_invalid_gradient_units(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="Invalid gradientUnits"):
            add_linear_gradient(proj, gradient_units="invalidUnits")
