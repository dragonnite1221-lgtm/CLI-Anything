# ruff: noqa: F403, F405, E501
from .recorder_base_base import *  # noqa: F403


@dataclass
class RecordedStep:
    index: int
    kind: str  # click | type | hotkey | scroll
    # click fields
    x: int = 0
    y: int = 0
    button: str = "left"
    double: bool = False
    template_path: str = ""  # relative path to saved template png (may be empty)
    window_title: str = ""  # title of window under click
    x_pct: float = 0.5  # click x as fraction of window width
    y_pct: float = 0.5  # click y as fraction of window height
    # type fields
    text: str = ""
    # hotkey fields
    keys: str = ""
    # scroll fields
    dx: int = 0
    dy: int = 0
    # timing
    timestamp: float = field(default_factory=time.time)
    # agent step fields (set during post-recording review)
    is_agent_step: bool = False
    agent_description: str = ""
    agent_end_state_description: str = ""
    agent_end_state_snapshot: str = ""  # relative path to snapshot png

    def to_step_dict(self) -> dict:
        """Convert to a macro YAML step dict.

        If marked as agent step, emits a gui_agent/instruct step.
        Otherwise uses visual_anchor with window-relative coords or template.
        """
        # Agent step overrides everything
        if self.is_agent_step:
            params: dict = {
                "description": self.agent_description,
                "end_state_description": self.agent_end_state_description,
                "max_steps": 8,
            }
            if self.agent_end_state_snapshot:
                params["end_state_snapshot"] = self.agent_end_state_snapshot
            return {
                "id": f"step_{self.index:03d}_agent",
                "backend": "gui_agent",
                "action": "instruct",
                "params": params,
                "on_failure": "fail",
            }
        if self.kind == "click":
            if self.window_title:
                # Best case: window-relative fractional coordinates
                params: dict = {
                    "window_title": self.window_title,
                    "x_pct": self.x_pct,
                    "y_pct": self.y_pct,
                }
                if self.button != "left":
                    params["button"] = self.button
                if self.double:
                    params["double"] = True
                step = {
                    "id": f"step_{self.index:03d}_click",
                    "backend": "visual_anchor",
                    "action": "click_relative",
                    "params": params,
                    "on_failure": "fail",
                }
                # Attach template as a comment if available (for debugging)
                if self.template_path:
                    step["_template"] = self.template_path
                return step

            elif self.template_path:
                # Has a usable template image
                params = {
                    "template": self.template_path,
                    "confidence": 0.85,
                    "timeout_ms": 5000,
                }
                if self.button != "left":
                    params["button"] = self.button
                if self.double:
                    params["double"] = True
                return {
                    "id": f"step_{self.index:03d}_click",
                    "backend": "visual_anchor",
                    "action": "click_image",
                    "params": params,
                    "on_failure": "fail",
                }

            else:
                # Fallback: screen-relative fractional coordinates
                return {
                    "id": f"step_{self.index:03d}_click",
                    "backend": "visual_anchor",
                    "action": "click_relative",
                    "params": {
                        "x_pct": self.x_pct,
                        "y_pct": self.y_pct,
                    },
                    "on_failure": "fail",
                }
        elif self.kind == "type":
            return {
                "id": f"step_{self.index:03d}_type",
                "backend": "visual_anchor",
                "action": "type_text",
                "params": {"text": self.text},
                "on_failure": "fail",
            }
        elif self.kind == "hotkey":
            return {
                "id": f"step_{self.index:03d}_hotkey",
                "backend": "visual_anchor",
                "action": "hotkey",
                "params": {"keys": self.keys},
                "on_failure": "fail",
            }
        elif self.kind == "scroll":
            return {
                "id": f"step_{self.index:03d}_scroll",
                "backend": "visual_anchor",
                "action": "scroll",
                "params": {
                    "template": self.template_path or "",
                    "dx": self.dx,
                    "dy": self.dy,
                },
                "on_failure": "fail",
            }
        return {}
