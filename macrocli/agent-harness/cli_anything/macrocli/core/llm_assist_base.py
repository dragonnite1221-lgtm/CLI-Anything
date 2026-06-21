# ruff: noqa: E501
"""LLMAssist — use a vision model to generate macro steps from screenshots.

This module is OPTIONAL. It requires:
    pip install openai mss Pillow

Uses the OpenAI SDK, which is compatible with any OpenAI-compatible API
provider (OpenAI, Azure, local vLLM, Ollama, LiteLLM, etc.).

Configure via environment variables:
    MACROCLI_MODEL    — model name (required)
    MACROCLI_API_KEY  — API key
    MACROCLI_BASE_URL — base URL (only needed for non-OpenAI hosts)

How it works:
  1. Capture a screenshot of the current screen (or use a provided image)
  2. Send the image + user goal to the vision model with a strict system prompt
  3. The model returns a JSON array of steps (constrained action space)
  4. Steps are validated and written as a macro YAML file

The action space the model is allowed to produce:

    {"type": "click_image",    "description": "...", "confidence": 0.85}
    {"type": "click_relative", "window_title": "...", "x_pct": 0.5, "y_pct": 0.1}
    {"type": "type_text",      "text": "..."}
    {"type": "hotkey",         "keys": "ctrl+s"}
    {"type": "wait_image",     "description": "...", "timeout_ms": 5000}
    {"type": "wait_for_window","title_contains": "...", "timeout_ms": 5000}
    {"type": "menu_click",     "app_name": "...", "menu_path": ["File", "Export"]}
    {"type": "scroll",         "description": "...", "dy": -3}

The model is NOT allowed to:
  - Produce shell commands, Python code, or arbitrary actions
  - Use absolute pixel coordinates
  - Output anything other than the JSON array

The "description" field in click_image / wait_image / scroll tells the user
what template image to capture with 'macro record' or 'capture_region'.

Usage:
    cli-anything-macrocli macro define my_export --assist \\
        --goal "Export the current diagram as PNG to /tmp/out.png" \\
        --screenshot current         # takes a fresh screenshot
        --screenshot /path/to/img.png   # use existing image
"""

from __future__ import annotations


import json
import os
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML required: pip install PyYAML")


# ── Strict system prompt ──────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are a GUI macro step generator. Given a screenshot and a user goal, \
output ONLY a valid JSON array of macro steps.

ALLOWED step types (use EXACTLY these schemas):

1. Click a UI element by visual description (template matching will be used):
   {"type": "click_image", "description": "<what the element looks like>", \
"confidence": 0.85, "timeout_ms": 5000}

2. Click at a fractional position within a named window:
   {"type": "click_relative", "window_title": "<partial title>", \
"x_pct": 0.0-1.0, "y_pct": 0.0-1.0}

3. Type text into the focused field:
   {"type": "type_text", "text": "<text to type>"}

4. Send a keyboard shortcut:
   {"type": "hotkey", "keys": "<key1+key2+...>"}

5. Wait for a visual element to appear:
   {"type": "wait_image", "description": "<what to wait for>", \
"timeout_ms": 5000}

6. Wait for a window with a certain title:
   {"type": "wait_for_window", "title_contains": "<partial title>", \
"timeout_ms": 5000}

7. Click a menu item by path:
   {"type": "menu_click", "app_name": "<app name>", \
"menu_path": ["Menu", "Submenu", "Item"]}

8. Scroll near a visual element:
   {"type": "scroll", "description": "<near what element>", "dy": -3}

STRICT RULES:
- Output RAW JSON ONLY. No markdown, no explanation, no code blocks.
- The output must be a JSON array: [step1, step2, ...]
- NEVER use absolute pixel coordinates (x, y numbers).
- NEVER output shell commands, Python, or any non-JSON content.
- NEVER invent step types not listed above.
- Prefer menu_click and hotkey over click_image when possible.
- For click_image: describe the element clearly so a human can find and \
photograph it.
- Keep the plan minimal: use the fewest steps that achieve the goal.
"""


# ── Screenshot helpers ────────────────────────────────────────────────────────

__all__ = ["Optional", "Path", "_SYSTEM_PROMPT", "annotations", "json", "os", "yaml"]
