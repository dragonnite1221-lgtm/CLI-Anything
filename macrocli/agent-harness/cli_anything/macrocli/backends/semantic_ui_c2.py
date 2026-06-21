# ruff: noqa: F403, F405, E501
from .semantic_ui_base import *  # noqa: F403
from .semantic_ui_p0 import _osascript, _x_env, _xdotool_focus  # noqa: F401,E501
from .semantic_ui_p1 import _win_find_app  # noqa: F401,E501


class SemanticUIBackendMixin2:
    def _wait_for_window(self, p: dict, context: BackendContext) -> dict:
        title: str = p.get("title_contains", "")
        timeout_ms: int = int(p.get("timeout_ms", 5000))
        poll_ms: int = int(p.get("poll_ms", 300))

        if not title:
            raise ValueError("wait_for_window requires 'title_contains' param.")

        deadline = time.time() + timeout_ms / 1000.0

        if _SYSTEM == "Linux":
            while time.time() < deadline:
                if shutil.which("wmctrl"):
                    r = subprocess.run(
                        ["wmctrl", "-l"], capture_output=True, text=True, env=_x_env()
                    )
                    if title.lower() in r.stdout.lower():
                        return {"found": title, "method": "wmctrl"}
                elif shutil.which("xdotool"):
                    r = subprocess.run(
                        ["xdotool", "search", "--name", title],
                        capture_output=True, text=True, env=_x_env(),
                    )
                    if r.returncode == 0 and r.stdout.strip():
                        return {"found": title, "method": "xdotool"}
                time.sleep(poll_ms / 1000.0)

        elif _SYSTEM == "Darwin":
            while time.time() < deadline:
                script = f"""
                tell application "System Events"
                    set ws to name of every window of every process
                    set found to false
                    repeat with wlist in ws
                        repeat with wname in wlist
                            if "{title}" is in (wname as text) then
                                set found to true
                            end if
                        end repeat
                    end repeat
                    return found
                end tell
                """
                result = _osascript(script)
                if result.lower() == "true":
                    return {"found": title, "method": "osascript"}
                time.sleep(poll_ms / 1000.0)

        elif _SYSTEM == "Windows":
            import pywinauto.findwindows as fw
            while time.time() < deadline:
                try:
                    handles = fw.find_windows(title_re=f".*{title}.*")
                    if handles:
                        return {"found": title, "method": "pywinauto"}
                except Exception:
                    pass
                time.sleep(poll_ms / 1000.0)

        raise TimeoutError(
            f"wait_for_window: window containing '{title}' did not appear "
            f"within {timeout_ms}ms."
        )
    def _focus_window(self, p: dict, context: BackendContext) -> dict:
        title: str = p.get("title_contains", "")
        if not title:
            raise ValueError("focus_window requires 'title_contains' param.")

        if _SYSTEM == "Linux":
            if shutil.which("wmctrl"):
                subprocess.run(["wmctrl", "-a", title], check=True, env=_x_env())
                return {"focused": title, "method": "wmctrl"}
            _xdotool_focus(title)
            return {"focused": title, "method": "xdotool"}

        elif _SYSTEM == "Darwin":
            _osascript(f'tell application "{title}" to activate')
            return {"focused": title, "method": "osascript"}

        elif _SYSTEM == "Windows":
            win = _win_find_app(title)
            win.set_focus()
            return {"focused": title, "method": "pywinauto"}

        raise NotImplementedError(f"focus_window not implemented for {_SYSTEM}")
