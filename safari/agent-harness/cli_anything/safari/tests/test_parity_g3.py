# ruff: noqa: F403, F405, E501
from .test_parity_helpers import *  # noqa: F403


class TestParityHighValueSchemas:
    """Spot-check schemas that had known drift bugs in previous revisions.

    Each test here is a regression lock: if the parser or upstream
    safari-mcp changes these shapes, the test fails loud and the
    contributor has to decide whether to update the pin or fix the parser.
    """

    def setup_method(self):
        self.registry = load_registry()

    def test_scroll_uses_direction_not_xy(self):
        tool = self.registry.get("safari_scroll")
        assert tool is not None
        names = {p.name for p in tool.params}
        assert "direction" in names
        assert "amount" in names
        assert "x" not in names  # previously (wrongly) wrapped as --x/--y
        assert "y" not in names

    def test_drag_uses_source_and_target(self):
        tool = self.registry.get("safari_drag")
        assert tool is not None
        names = {p.name for p in tool.params}
        assert "sourceSelector" in names
        assert "targetSelector" in names

    def test_mock_route_uses_url_pattern(self):
        tool = self.registry.get("safari_mock_route")
        assert tool is not None
        names = {p.name for p in tool.params}
        assert "urlPattern" in names

    def test_throttle_network_has_profile(self):
        tool = self.registry.get("safari_throttle_network")
        assert tool is not None
        names = {p.name for p in tool.params}
        assert "profile" in names

    # ── Nested-schema parser regression locks ────────────────────
    # These test the bugs fixed in extract_tools.py's depth-aware
    # modifier detection. If the parser regresses, `.describe("...")`
    # from a nested schema would leak into the outer field description,
    # and `.optional()` on nested fields would incorrectly mark the
    # outer param as optional.

    def test_mock_route_response_is_required_not_status_description(self):
        """safari_mock_route.response is required and takes a JSON object.

        Regression target: the parser used to pick the nested
        .describe("HTTP status code") from the inner `status` field
        instead of the outer .describe("Mock response to return"),
        and wrongly inferred optional from nested .optional() calls.
        """
        tool = self.registry.get("safari_mock_route")
        assert tool is not None
        response = tool.get_param("response")
        assert response is not None
        assert response.required, "response must be required"
        assert response.type == "object"
        assert "status code" not in (response.description or "").lower(), (
            "parser leaked nested .describe(); expected 'Mock response to return'"
        )
        assert "mock response" in (response.description or "").lower()

    def test_run_script_steps_is_required_and_described_correctly(self):
        """safari_run_script.steps is required (no top-level .optional).

        Regression target: the parser's old naive `.optional(` check
        would find the nested `args: z.record(...).optional()` and
        wrongly mark the outer `steps` as optional.
        """
        tool = self.registry.get("safari_run_script")
        assert tool is not None
        steps = tool.get_param("steps")
        assert steps is not None
        assert steps.required, "steps must be required"
        assert steps.type == "array"
        assert "array of steps" in (steps.description or "").lower()

    def test_fill_form_fields_description_is_outer_not_inner(self):
        """safari_fill_form.fields description must come from the
        OUTER .describe(), not the nested selector's .describe("CSS selector").
        """
        tool = self.registry.get("safari_fill_form")
        assert tool is not None
        fields = tool.get_param("fields")
        assert fields is not None
        assert fields.required
        assert fields.type == "array"
        assert fields.description != "CSS selector", (
            "parser leaked the nested selector description; should be "
            "the outer 'Array of {selector, value} pairs'"
        )
        assert "selector" in fields.description.lower()
        assert "value" in fields.description.lower()

    def test_fill_and_submit_fields_description_is_outer(self):
        tool = self.registry.get("safari_fill_and_submit")
        assert tool is not None
        fields = tool.get_param("fields")
        assert fields is not None
        assert fields.required
        assert fields.description != "CSS selector"

    def test_evaluate_param_is_script_not_code(self):
        """safari_evaluate's parameter is named ``script`` upstream.

        Regression test: every prior version of the docs and a
        TestCallForwarding test exemplar called it ``code`` by mistake,
        which would silently send the wrong arg through ``raw`` calls
        and fail with ``--code`` is unknown option through ``tool``.
        """
        tool = self.registry.get("safari_evaluate")
        assert tool is not None
        param_names = {p.name for p in tool.params}
        assert "script" in param_names, (
            f"safari_evaluate must take 'script', got params: {param_names}"
        )
        assert "code" not in param_names, (
            "Doc/test bug regression: safari_evaluate uses 'script' upstream"
        )
        script_param = tool.get_param("script")
        assert script_param is not None
        assert script_param.required
        assert script_param.type == "string"

    def test_run_script_param_is_steps(self):
        """safari_run_script takes 'steps' (array). Locks the rename
        regression alongside test_evaluate_param_is_script_not_code."""
        tool = self.registry.get("safari_run_script")
        assert tool is not None
        param_names = {p.name for p in tool.params}
        assert "steps" in param_names
