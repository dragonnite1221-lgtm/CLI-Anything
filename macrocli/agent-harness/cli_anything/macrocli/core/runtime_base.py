# ruff: noqa: E501
"""MacroRuntime — orchestrates the full macro execution lifecycle.

Lifecycle for execute(macro_name, params):

  1. Load macro definition from registry
  2. Resolve + validate parameters (fill defaults, type-check)
  3. Check preconditions
  4. For each step:
       a. substitute ${params} into step.params
       b. route to backend
       c. execute (with retry if configured)
       d. handle on_failure = fail | skip | continue
  5. Check postconditions
  6. Collect declared outputs
  7. Record telemetry in session
  8. Return ExecutionResult
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from cli_anything.macrocli.core.macro_model import (
    MacroCondition,
    MacroDefinition,
    MacroStep,
    substitute,
)
from cli_anything.macrocli.core.registry import MacroRegistry
from cli_anything.macrocli.core.routing import RoutingEngine
from cli_anything.macrocli.core.session import ExecutionSession, RunRecord
from cli_anything.macrocli.backends.base import BackendContext, StepResult


# ── Result types ─────────────────────────────────────────────────────────────

__all__ = [
    "Any",
    "BackendContext",
    "ExecutionSession",
    "MacroCondition",
    "MacroDefinition",
    "MacroRegistry",
    "MacroStep",
    "Optional",
    "RoutingEngine",
    "RunRecord",
    "StepResult",
    "annotations",
    "dataclass",
    "field",
    "os",
    "substitute",
    "time",
]
