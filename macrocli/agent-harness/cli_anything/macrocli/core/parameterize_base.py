# ruff: noqa: E501
"""Parameterization helpers — interactive and LLM-assisted.

Interactive flow (no external deps):
    assignments = interactive_parameterize(type_steps)
    parameters  = recorder.apply_parameterization(assignments)
    recorder.save(parameters=parameters)

Post-hoc flow on an existing YAML file:
    parameterize_yaml_file(yaml_path)   # modifies in-place

LLM-assisted flow (optional, requires openai):
    assignments = llm_suggest_parameters(type_steps, api_key=...)
    # returns same shape as interactive_parameterize, can be passed directly
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML required: pip install PyYAML")


# ── Parameter name validation ─────────────────────────────────────────────────

_PARAM_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")

__all__ = ["Optional", "Path", "_PARAM_NAME_RE", "annotations", "re", "sys", "yaml"]
