# ruff: noqa: E501
"""
SKILL.md Generator for CLI-Anything

This module extracts metadata from CLI-Anything harnesses and generates
SKILL.md files following the skill-creator methodology.

The generated SKILL.md files contain:
- YAML frontmatter with name and description (triggering metadata)
- Markdown body with usage instructions
- Command documentation
- Examples for AI agents
"""

import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

__all__ = ["Optional", "Path", "dataclass", "field", "re"]
