# ruff: noqa: E501
"""Manages s&box ProjectSettings/Collision.config files.

Provides functions to load, save, query, and modify collision layers and
pair rules in the s&box Collision.config JSON format.
"""

import json
import uuid
from typing import Optional

# Built-in layers that cannot be removed
BUILTIN_LAYERS = frozenset({"solid", "trigger", "ladder", "water"})

# Valid collision results
VALID_RESULTS = frozenset({"Collide", "Trigger", "Ignore"})

__all__ = ["BUILTIN_LAYERS", "Optional", "VALID_RESULTS", "json", "uuid"]
