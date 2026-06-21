# ruff: noqa: F403, F405, E501
from .semantic_ui_base import *  # noqa: F403


def _x_env() -> dict:
    """Return env dict with DISPLAY set, for subprocess calls to X tools."""
    env = os.environ.copy()
    if "DISPLAY" not in env:
        env["DISPLAY"] = ":0"
    return env


def _atspi_available() -> bool:
    try:
        import pyatspi  # noqa: F401
        return True
    except ImportError:
        return False


def _atspi_find_app(name_fragment: str):
    """Return the first AT-SPI application matching name_fragment."""
    import pyatspi
    desktop = pyatspi.Registry.getDesktop(0)
    for app in desktop:
        if app and name_fragment.lower() in (app.name or "").lower():
            return app
    return None


def _atspi_find_control(root, role_name: str, label_fragment: str, max_depth: int = 20):
    """BFS search for a control by role and label."""
    import pyatspi
    role_map = {
        "button": pyatspi.ROLE_PUSH_BUTTON,
        "menu": pyatspi.ROLE_MENU,
        "menu_item": pyatspi.ROLE_MENU_ITEM,
        "menu_bar": pyatspi.ROLE_MENU_BAR,
        "text": pyatspi.ROLE_TEXT,
        "combo_box": pyatspi.ROLE_COMBO_BOX,
        "check_box": pyatspi.ROLE_CHECK_BOX,
        "radio": pyatspi.ROLE_RADIO_BUTTON,
        "list_item": pyatspi.ROLE_LIST_ITEM,
        "dialog": pyatspi.ROLE_DIALOG,
        "window": pyatspi.ROLE_FRAME,
    }
    target_role = role_map.get(role_name.lower())

    from collections import deque
    queue = deque([(root, 0)])
    while queue:
        node, depth = queue.popleft()
        if depth > max_depth:
            continue
        try:
            node_role = node.getRole()
            node_name = node.name or ""
            if (target_role is None or node_role == target_role):
                if label_fragment.lower() in node_name.lower():
                    return node
            for i in range(node.childCount):
                child = node.getChildAtIndex(i)
                if child:
                    queue.append((child, depth + 1))
        except Exception:
            continue
    return None


def _atspi_menu_path(app, menu_path: list[str]):
    """Navigate a menu path and activate the final item."""
    import pyatspi

    # Find the menu bar
    menu_bar = _atspi_find_control(app, "menu_bar", "", max_depth=3)
    if menu_bar is None:
        raise RuntimeError("AT-SPI: menu bar not found in application.")

    current = menu_bar
    for label in menu_path:
        item = _atspi_find_control(current, "menu", label)
        if item is None:
            item = _atspi_find_control(current, "menu_item", label)
        if item is None:
            raise RuntimeError(f"AT-SPI: menu item '{label}' not found.")
        # Activate / click
        try:
            action = item.queryAction()
            for i in range(action.nActions):
                if action.getName(i).lower() in ("click", "activate", "open"):
                    action.doAction(i)
                    break
        except Exception:
            pass
        current = item
        time.sleep(0.15)

    return True


def _xdotool_key(keys: str) -> None:
    if not shutil.which("xdotool"):
        raise RuntimeError("xdotool not found. Install with: apt install xdotool")
    # ctrl+shift+e → ctrl+shift+e (xdotool accepts this format directly)
    subprocess.run(["xdotool", "key", "--clearmodifiers", keys], check=True, env=_x_env())


def _xdotool_type(text: str) -> None:
    if not shutil.which("xdotool"):
        raise RuntimeError("xdotool not found. Install with: apt install xdotool")
    subprocess.run(["xdotool", "type", "--clearmodifiers", "--delay", "30", text], check=True, env=_x_env())


def _xdotool_focus(title: str) -> None:
    if not shutil.which("xdotool"):
        raise RuntimeError("xdotool not found. Install with: apt install xdotool")
    subprocess.run(
        ["xdotool", "search", "--name", title, "windowfocus", "--sync"],
        check=True, env=_x_env(),
    )


def _osascript(script: str) -> str:
    r = subprocess.run(
        ["osascript", "-e", script], capture_output=True, text=True
    )
    if r.returncode != 0:
        raise RuntimeError(f"osascript failed: {r.stderr.strip()}")
    return r.stdout.strip()
