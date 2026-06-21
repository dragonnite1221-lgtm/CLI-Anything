# ruff: noqa: F403, F405, E501
from .semantic_ui_base import *  # noqa: F403
from .semantic_ui_p0 import _atspi_available, _atspi_find_app  # noqa: F401,E501
from .semantic_ui_p1 import _win_find_app  # noqa: F401,E501


class SemanticUIBackendMixin3:
    def _get_controls(self, p: dict, context: BackendContext) -> dict:
        """List interactive controls in a window (for macro authoring / discovery)."""
        window_title: str = p.get("window_title", "")
        max_depth: int = int(p.get("max_depth", 5))

        if _SYSTEM == "Linux" and _atspi_available():
            import pyatspi
            app = _atspi_find_app(window_title) if window_title else None
            root = app or pyatspi.Registry.getDesktop(0)
            controls = []
            interactive_roles = {
                pyatspi.ROLE_PUSH_BUTTON,
                pyatspi.ROLE_MENU,
                pyatspi.ROLE_MENU_ITEM,
                pyatspi.ROLE_TEXT,
                pyatspi.ROLE_COMBO_BOX,
                pyatspi.ROLE_CHECK_BOX,
                pyatspi.ROLE_RADIO_BUTTON,
                pyatspi.ROLE_TOGGLE_BUTTON,
            }
            from collections import deque
            queue = deque([(root, 0)])
            while queue:
                node, depth = queue.popleft()
                if depth > max_depth:
                    continue
                try:
                    if node.getRole() in interactive_roles:
                        controls.append({
                            "role": node.getRoleName(),
                            "name": node.name,
                        })
                    for i in range(node.childCount):
                        child = node.getChildAtIndex(i)
                        if child:
                            queue.append((child, depth + 1))
                except Exception:
                    continue
            return {"controls": controls, "count": len(controls)}

        elif _SYSTEM == "Windows":
            win = _win_find_app(window_title)
            controls = []
            for ctrl in win.descendants():
                try:
                    controls.append({
                        "role": ctrl.element_info.control_type,
                        "name": ctrl.element_info.name,
                    })
                except Exception:
                    pass
            return {"controls": controls, "count": len(controls)}

        raise NotImplementedError(
            f"get_controls not implemented for {_SYSTEM} without AT-SPI / pywinauto."
        )
