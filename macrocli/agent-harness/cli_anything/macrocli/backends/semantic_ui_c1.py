# ruff: noqa: F403, F405, E501
from .semantic_ui_base import *  # noqa: F403
from .semantic_ui_p0 import _atspi_available, _atspi_find_app, _atspi_find_control, _atspi_menu_path, _osascript  # noqa: F401,E501
from .semantic_ui_p1 import _macos_menu_click, _win_find_app  # noqa: F401,E501


class SemanticUIBackendMixin1:
    def _menu_click(self, p: dict, context: BackendContext) -> dict:
        menu_path: list = p.get("menu_path", [])
        app_name: str = p.get("app_name", "")

        if not menu_path:
            raise ValueError("menu_click requires 'menu_path' param (list of strings).")

        if _SYSTEM == "Linux":
            if _atspi_available():
                if not app_name:
                    raise ValueError(
                        "menu_click on Linux AT-SPI requires 'app_name' param."
                    )
                app = _atspi_find_app(app_name)
                if app is None:
                    raise RuntimeError(f"AT-SPI: application '{app_name}' not found.")
                _atspi_menu_path(app, menu_path)
                return {"menu_path": menu_path, "method": "at-spi"}
            else:
                raise RuntimeError(
                    "menu_click on Linux requires AT-SPI.\n"
                    "  apt install python3-pyatspi\n"
                    "  Or use visual_anchor backend instead."
                )

        elif _SYSTEM == "Darwin":
            if not app_name:
                raise ValueError("menu_click on macOS requires 'app_name' param.")
            _macos_menu_click(app_name, menu_path)
            return {"menu_path": menu_path, "method": "osascript"}

        elif _SYSTEM == "Windows":
            if not app_name:
                raise ValueError("menu_click on Windows requires 'app_name' param.")
            win = _win_find_app(app_name)
            # pywinauto menu navigation
            menu = win.menu()
            for item in menu_path:
                menu = menu.item_by_path(item)
            menu.click_input()
            return {"menu_path": menu_path, "method": "pywinauto"}

        raise NotImplementedError(f"menu_click not implemented for {_SYSTEM}")
    def _button_click(self, p: dict, context: BackendContext) -> dict:
        label: str = p.get("label", "")
        app_name: str = p.get("app_name", "")

        if not label:
            raise ValueError("button_click requires 'label' param.")

        if _SYSTEM == "Linux" and _atspi_available():
            if not app_name:
                raise ValueError("button_click on Linux AT-SPI requires 'app_name'.")
            app = _atspi_find_app(app_name)
            if app is None:
                raise RuntimeError(f"AT-SPI: application '{app_name}' not found.")
            btn = _atspi_find_control(app, "button", label)
            if btn is None:
                raise RuntimeError(f"AT-SPI: button '{label}' not found in '{app_name}'.")
            action = btn.queryAction()
            for i in range(action.nActions):
                if action.getName(i).lower() == "click":
                    action.doAction(i)
                    return {"clicked": label, "method": "at-spi"}
            raise RuntimeError(f"AT-SPI: no click action on button '{label}'.")

        elif _SYSTEM == "Darwin":
            script = f"""
            tell application "System Events"
                click button "{label}" of front window of (first process whose frontmost is true)
            end tell
            """
            _osascript(script)
            return {"clicked": label, "method": "osascript"}

        elif _SYSTEM == "Windows":
            win = _win_find_app(app_name or "")
            win.child_window(title=label, control_type="Button").click_input()
            return {"clicked": label, "method": "pywinauto"}

        raise NotImplementedError(
            f"button_click not fully implemented for {_SYSTEM} without AT-SPI.\n"
            "Use visual_anchor backend as fallback."
        )
