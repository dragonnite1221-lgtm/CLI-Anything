# ruff: noqa: F403, F405, E501
"""GUIAgentBackend — execute a macro step by letting a vision model
look at the screen and decide what to do.

This backend is used for steps that cannot be expressed as fixed
coordinates or hotkeys because the interface state is unpredictable.
The macro author provides:
  - description:           what needs to be accomplished in this step
  - end_state_description: text description of the desired end state
  - end_state_snapshot:    screenshot of the desired end state (taken
                           by the macro author at recording time)

At runtime the backend:
  1. Takes a screenshot of the current screen
  2. Sends current screenshot + end_state_snapshot + description to the model
  3. Model returns the next action (click x,y / type text / hotkey)
  4. Executes the action
  5. Takes another screenshot
  6. Asks model: "have we reached the end state?"
  7. Loops until end state reached or max_steps exceeded

The backend uses the OpenAI SDK, which is compatible with any
OpenAI-compatible API provider (OpenAI, Azure, local vLLM, Ollama,
LiteLLM, etc.).  Configure model and endpoint via environment
variables or per-step YAML params:

  Environment variables:
    MACROCLI_MODEL    — model name (required, no default)
    MACROCLI_API_KEY  — API key
    MACROCLI_BASE_URL — base URL for non-OpenAI providers

Example YAML step:

    - id: select_png_format
      backend: gui_agent
      action: instruct
      params:
        description: >
          The export dialog is open. Find the Format dropdown and
          select PNG. Then ensure Resolution shows 300.
        end_state_description: >
          Format dropdown shows PNG, Resolution input shows 300.
        end_state_snapshot: snapshots/step_003_end_state.png
        max_steps: 8
        model: ${MACROCLI_MODEL}
        api_key: ${MACROCLI_API_KEY}
        base_url: ${MACROCLI_BASE_URL}
"""
from __future__ import annotations
import base64
import json
import os
import time
from pathlib import Path
from typing import Optional
from cli_anything.macrocli.backends.base import Backend, BackendContext, StepResult
from cli_anything.macrocli.core.macro_model import MacroStep, substitute


_SYSTEM_PROMPT = """\
You are a GUI automation agent. You will be shown:
1. A screenshot of the CURRENT screen state
2. A screenshot of the TARGET end state (optional)
3. A description of what needs to be accomplished

Your job is to figure out what single action to take next.

OUTPUT FORMAT: Respond with ONLY a JSON object, one of:

  {"action": "click", "x": <int>, "y": <int>, "button": "left"}
  {"action": "double_click", "x": <int>, "y": <int>}
  {"action": "right_click", "x": <int>, "y": <int>}
  {"action": "drag", "from_x": <int>, "from_y": <int>, "to_x": <int>, "to_y": <int>, "duration_ms": 300}
  {"action": "type", "text": "<string>"}
  {"action": "hotkey", "keys": "<key1+key2+...>"}
  {"action": "scroll", "x": <int>, "y": <int>, "dy": <int>}
  {"action": "done"}

Use {"action": "done"} ONLY when the current state matches the target state.

RULES:
- Output RAW JSON ONLY. No markdown, no explanation.
- Use pixel coordinates from the CURRENT screenshot.
- For drag: from_x/from_y is where you start pressing, to_x/to_y is where you release.
- Prefer clicking on visible labeled controls over guessing coordinates.
- If the target state is already achieved, output {"action": "done"}.
- Never output any action not listed above.
"""


_CHECK_PROMPT = """\
Compare these two screenshots:
1. CURRENT state
2. TARGET end state

Has the current state reached the target end state?
Answer with ONLY: {"reached": true} or {"reached": false, "reason": "<brief reason>"}
"""


def _screenshot_b64() -> str:
    """Take a screenshot and return as base64 PNG string."""
    try:
        import mss
        from PIL import Image
        import io
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            raw = sct.grab(monitor)
            img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return base64.b64encode(buf.getvalue()).decode("utf-8")
    except ImportError:
        raise ImportError("mss and Pillow required: pip install mss Pillow")


def _file_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _execute_action(action_dict: dict, context: BackendContext) -> None:
    """Execute a single action returned by the model."""
    from cli_anything.macrocli.backends.visual_anchor import (
        _mouse_click, _mouse_drag, _require_pynput
    )

    action = action_dict.get("action", "")

    if action == "click":
        x, y = int(action_dict["x"]), int(action_dict["y"])
        _mouse_click(x, y, button=action_dict.get("button", "left"))

    elif action == "double_click":
        x, y = int(action_dict["x"]), int(action_dict["y"])
        _mouse_click(x, y, double=True)

    elif action == "right_click":
        x, y = int(action_dict["x"]), int(action_dict["y"])
        _mouse_click(x, y, button="right")

    elif action == "type":
        text = action_dict.get("text", "")
        _, keyboard_mod = _require_pynput()
        ctrl = keyboard_mod.Controller()
        for char in text:
            ctrl.press(char)
            ctrl.release(char)
            time.sleep(0.03)

    elif action == "hotkey":
        keys_str = action_dict.get("keys", "")
        _, keyboard_mod = _require_pynput()
        Key = keyboard_mod.Key
        ctrl = keyboard_mod.Controller()
        _KEY_MAP = {
            "ctrl": Key.ctrl, "shift": Key.shift, "alt": Key.alt,
            "enter": Key.enter, "tab": Key.tab, "esc": Key.esc,
            "escape": Key.esc, "space": Key.space, "backspace": Key.backspace,
        }
        keys = [_KEY_MAP.get(k.lower(), k) for k in keys_str.split("+")]
        for k in keys:
            ctrl.press(k)
        for k in reversed(keys):
            ctrl.release(k)

    elif action == "scroll":
        x, y = int(action_dict["x"]), int(action_dict["y"])
        dy = int(action_dict.get("dy", -3))
        mouse_mod, _ = _require_pynput()
        ctrl = mouse_mod.Controller()
        ctrl.position = (x, y)
        ctrl.scroll(0, dy)

    elif action == "drag":
        fx, fy = int(action_dict["from_x"]), int(action_dict["from_y"])
        tx, ty = int(action_dict["to_x"]), int(action_dict["to_y"])
        duration_ms = int(action_dict.get("duration_ms", 300))
        from cli_anything.macrocli.backends.visual_anchor import _mouse_drag
        _mouse_drag(fx, fy, tx, ty, duration_ms=duration_ms)

    elif action == "done":
        pass  # caller checks for done

    else:
        raise ValueError(f"GUIAgentBackend: unknown action '{action}'")


# fmt: off
__all__ = ['Backend', 'BackendContext', 'MacroStep', 'Optional', 'Path', 'StepResult', '_CHECK_PROMPT', '_SYSTEM_PROMPT', '_execute_action', '_file_to_b64', '_screenshot_b64', 'annotations', 'base64', 'json', 'os', 'substitute', 'time']  # noqa: E501
# fmt: on
