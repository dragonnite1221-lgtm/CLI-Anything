# ruff: noqa: E501
"""
Pipeline diff -- compare two pipeline snapshots and output only differences.

Usage:
    from core.diff import diff_pipeline
    result = diff_pipeline(controller_a, event_a, controller_b, event_b)

The result dict only contains sections that have at least one difference.
Sections that are completely identical are either omitted or marked "SAME".

The snapshot format matches the output of ``dump_pipeline_for_diff``:

    {
      "eventId": ...,
      "PipelineState": {
        "pipelineType": ...,
        "vertexInputs": [...],
        "outputTargets": [...],
        "depthTarget": {...},
        "viewport": {...},
        "rasterizer": {...},
        "blend": {...},
        "depthStencil": {...},
        "stages": {
          "Vertex": {
            "shader": "ResourceId::...",
            "entryPoint": "...",
            "ShaderReflection": { ... },
            "bindings": {
              "constantBlocks": [ { ..., "variables": [...] } ],
              "readOnlyResources": [...],
              "readWriteResources": [...],
              "samplers": [...]
            }
          },
          ...
        }
      }
    }
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from cli_anything.renderdoc.core.pipeline import dump_pipeline_for_diff


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FLOAT_TOL = 1e-6

__all__ = [
    "Any",
    "Dict",
    "List",
    "Optional",
    "_FLOAT_TOL",
    "annotations",
    "dump_pipeline_for_diff",
    "math",
]
