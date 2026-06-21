# ruff: noqa: F403, F405, E501
from .llm_assist_base import *  # noqa: F403


def _step_to_yaml_step(step: dict, index: int) -> dict:
    """Convert a validated model step to a macro YAML step dict."""
    stype = step["type"]
    sid = f"step_{index:03d}_{stype}"

    if stype == "click_image":
        return {
            "id": sid,
            "backend": "visual_anchor",
            "action": "click_image",
            "params": {
                "template": f"templates/{index:03d}_{stype}.png",
                "confidence": step.get("confidence", 0.85),
                "timeout_ms": step.get("timeout_ms", 5000),
                "_template_description": step.get("description", ""),
            },
            "on_failure": "fail",
            "_model_description": step.get("description", ""),
        }
    elif stype == "click_relative":
        return {
            "id": sid,
            "backend": "visual_anchor",
            "action": "click_relative",
            "params": {
                "window_title": step["window_title"],
                "x_pct": step["x_pct"],
                "y_pct": step["y_pct"],
            },
            "on_failure": "fail",
        }
    elif stype == "type_text":
        return {
            "id": sid,
            "backend": "visual_anchor",
            "action": "type_text",
            "params": {"text": step["text"]},
            "on_failure": "fail",
        }
    elif stype == "hotkey":
        return {
            "id": sid,
            "backend": "visual_anchor",
            "action": "hotkey",
            "params": {"keys": step["keys"]},
            "on_failure": "fail",
        }
    elif stype == "wait_image":
        return {
            "id": sid,
            "backend": "visual_anchor",
            "action": "wait_image",
            "params": {
                "template": f"templates/{index:03d}_{stype}.png",
                "confidence": step.get("confidence", 0.85),
                "timeout_ms": step.get("timeout_ms", 10000),
                "_template_description": step.get("description", ""),
            },
            "on_failure": "fail",
            "_model_description": step.get("description", ""),
        }
    elif stype == "wait_for_window":
        return {
            "id": sid,
            "backend": "semantic_ui",
            "action": "wait_for_window",
            "params": {
                "title_contains": step["title_contains"],
                "timeout_ms": step.get("timeout_ms", 5000),
            },
            "on_failure": "fail",
        }
    elif stype == "menu_click":
        return {
            "id": sid,
            "backend": "semantic_ui",
            "action": "menu_click",
            "params": {
                "app_name": step["app_name"],
                "menu_path": step["menu_path"],
            },
            "on_failure": "fail",
        }
    elif stype == "scroll":
        return {
            "id": sid,
            "backend": "visual_anchor",
            "action": "scroll",
            "params": {
                "template": f"templates/{index:03d}_{stype}.png"
                if step.get("description")
                else "",
                "dy": step.get("dy", -3),
                "dx": step.get("dx", 0),
                "_template_description": step.get("description", ""),
            },
            "on_failure": "fail",
        }
    return {}
