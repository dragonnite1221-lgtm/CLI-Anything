# ruff: noqa: F403, F405, E501
from .semantic_ui_base import *  # noqa: F403
from .semantic_ui_p0 import _osascript  # noqa: F401,E501


def _macos_menu_click(app_name: str, menu_path: list[str]) -> None:
    if len(menu_path) < 2:
        raise ValueError("menu_path needs at least 2 elements (menu name + item).")
    menu_name = menu_path[0]
    items = menu_path[1:]
    # Build nested AppleScript path
    item_script = " of menu ".join(
        [f'menu item "{i}"' for i in reversed(items)]
    )
    script = f"""
    tell application "{app_name}"
        activate
    end tell
    tell application "System Events"
        tell process "{app_name}"
            click {item_script} of menu "{menu_name}" of menu bar 1
        end tell
    end tell
    """
    _osascript(script)


def _win_find_app(title_fragment: str):
    from pywinauto import Application, findwindows
    handles = findwindows.find_windows(title_re=f".*{title_fragment}.*")
    if not handles:
        raise RuntimeError(f"Window not found: '{title_fragment}'")
    app = Application().connect(handle=handles[0])
    return app.window(handle=handles[0])
