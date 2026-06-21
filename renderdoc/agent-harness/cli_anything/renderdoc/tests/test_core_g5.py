# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestDiffModule:
    """Unit tests for diff_pipeline_from_snapshots and helpers."""

    @staticmethod
    def _make_snapshot(event_id, pipeline_state=None):
        """Build a minimal snapshot dict."""
        return {
            "eventId": event_id,
            "PipelineState": pipeline_state or {},
        }

    def test_identical_snapshots(self):
        from cli_anything.renderdoc.core.diff import diff_pipeline_from_snapshots

        ps = {
            "pipelineType": "Graphics",
            "viewport": {"x": 0, "y": 0, "width": 1920, "height": 1080},
            "rasterizer": {"fillMode": "Solid"},
            "depthStencil": {"depthEnable": True},
            "stages": {},
        }
        snap = self._make_snapshot(100, ps)
        result = diff_pipeline_from_snapshots(snap, snap)
        assert result["identical"] is True

    def test_different_viewport(self):
        from cli_anything.renderdoc.core.diff import diff_pipeline_from_snapshots

        ps_a = {"viewport": {"x": 0, "y": 0, "width": 1920, "height": 1080}}
        ps_b = {"viewport": {"x": 0, "y": 0, "width": 1280, "height": 720}}
        result = diff_pipeline_from_snapshots(
            self._make_snapshot(1, ps_a),
            self._make_snapshot(2, ps_b),
        )
        assert result["identical"] is False
        assert "viewport" in result
        assert result["viewport"]["width"]["A"] == 1920
        assert result["viewport"]["width"]["B"] == 1280

    def test_float_tolerance(self):
        from cli_anything.renderdoc.core.diff import _values_equal

        assert _values_equal(1.0, 1.0 + 1e-9) is True
        assert _values_equal(1.0, 1.1) is False

    def test_float_nan_equal(self):
        import math
        from cli_anything.renderdoc.core.diff import _values_equal

        assert _values_equal(float("nan"), float("nan")) is True
        assert _values_equal(float("inf"), float("inf")) is True
        assert _values_equal(float("inf"), float("-inf")) is False

    def test_diff_lists_only_in_one_side(self):
        from cli_anything.renderdoc.core.diff import diff_pipeline_from_snapshots

        ps_a = {
            "vertexInputs": [
                {"name": "POSITION", "format": "R32G32B32_FLOAT"},
            ],
        }
        ps_b = {
            "vertexInputs": [
                {"name": "POSITION", "format": "R32G32B32_FLOAT"},
                {"name": "TEXCOORD", "format": "R32G32_FLOAT"},
            ],
        }
        result = diff_pipeline_from_snapshots(
            self._make_snapshot(1, ps_a),
            self._make_snapshot(2, ps_b),
        )
        assert result["identical"] is False
        assert isinstance(result["vertexInputs"], list)
        statuses = [d["status"] for d in result["vertexInputs"]]
        assert "only_in_B" in statuses

    def test_diff_dicts_missing_key(self):
        from cli_anything.renderdoc.core.diff import _diff_dicts

        a = {"x": 1, "y": 2}
        b = {"x": 1, "z": 3}
        result = _diff_dicts(a, b)
        assert result is not None
        assert "y" in result
        assert "z" in result

    def test_diff_dicts_identical(self):
        from cli_anything.renderdoc.core.diff import _diff_dicts

        a = {"x": 1, "y": 2}
        result = _diff_dicts(a, a)
        assert result is None

    def test_diff_dicts_none_inputs(self):
        from cli_anything.renderdoc.core.diff import _diff_dicts

        assert _diff_dicts(None, None) is None
        result = _diff_dicts(None, {"x": 1})
        assert result is not None
        assert result["A"] is None

    def test_stage_diff_shader_changed(self):
        from cli_anything.renderdoc.core.diff import diff_pipeline_from_snapshots

        ps_a = {
            "stages": {
                "Vertex": {
                    "shader": "ResourceId::100",
                    "entryPoint": "main",
                    "ShaderReflection": {},
                    "bindings": {
                        "constantBlocks": [],
                        "readOnlyResources": [],
                        "readWriteResources": [],
                        "samplers": [],
                    },
                },
            },
        }
        ps_b = {
            "stages": {
                "Vertex": {
                    "shader": "ResourceId::200",
                    "entryPoint": "main",
                    "ShaderReflection": {},
                    "bindings": {
                        "constantBlocks": [],
                        "readOnlyResources": [],
                        "readWriteResources": [],
                        "samplers": [],
                    },
                },
            },
        }
        result = diff_pipeline_from_snapshots(
            self._make_snapshot(1, ps_a),
            self._make_snapshot(2, ps_b),
        )
        assert result["identical"] is False
        assert result["stages"]["Vertex"]["shader"]["shader"]["A"] == "ResourceId::100"
        assert result["stages"]["Vertex"]["shader"]["shader"]["B"] == "ResourceId::200"

    def test_cbuffer_variable_diff(self):
        from cli_anything.renderdoc.core.diff import _diff_cbuffer_vars

        vars_a = [
            {"name": "color", "values": [1.0, 0.0, 0.0, 1.0]},
            {"name": "intensity", "values": [0.5]},
        ]
        vars_b = [
            {"name": "color", "values": [0.0, 1.0, 0.0, 1.0]},
            {"name": "intensity", "values": [0.5]},
        ]
        result = _diff_cbuffer_vars(vars_a, vars_b)
        assert result is not None
        assert len(result) == 1
        assert result[0]["name"] == "color"
        assert result[0]["status"] == "changed"

    def test_cbuffer_variable_identical(self):
        from cli_anything.renderdoc.core.diff import _diff_cbuffer_vars

        vars_a = [{"name": "x", "values": [1.0]}]
        result = _diff_cbuffer_vars(vars_a, vars_a)
        assert result is None

    def test_output_table_extra_columns(self):
        """Verify output_table truncates rows longer than headers."""
        from cli_anything.renderdoc.utils.output import output_table
        import io

        buf = io.StringIO()
        output_table(
            [["Alice", 30, "extra_col"]],
            ["Name", "Age"],
            file=buf,
        )
        text = buf.getvalue()
        assert "Alice" in text
        assert "extra_col" not in text
