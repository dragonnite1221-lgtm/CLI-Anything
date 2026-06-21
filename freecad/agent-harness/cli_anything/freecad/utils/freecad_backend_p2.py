# ruff: noqa: F403, F405, E501
from .freecad_backend_base import *  # noqa: F403

# fmt: off
from .freecad_backend_p1 import _run, _write_temp_script, find_freecad  # noqa: E402,E501
# fmt: on


def _is_gui_wrapper_script(path: str) -> bool:
    """Return True when *path* looks like the local GUI-launch wrapper.

    On this machine the `freecad` command is a shell wrapper that dispatches to
    either the GUI binary or `freecadcmd`. When a Python script path is passed,
    the wrapper defaults to console mode unless we explicitly ask for the GUI
    binary.
    """
    try:
        resolved = Path(path).resolve()
        if not resolved.is_file():
            return False
        head = resolved.read_bytes()[:4096]
    except OSError:
        return False
    return b"SCRIPT_MODE" in head and b"xvfb-run" in head and b"freecadcmd" in head


def _macro_command(freecad: str, script_path: str, *, gui_required: bool) -> list[str]:
    """Build the argv used to execute a FreeCAD macro script."""
    if gui_required and _is_gui_wrapper_script(freecad):
        return [freecad, "freecad", script_path]
    return [freecad, script_path]


def get_version() -> str:
    """Return the FreeCAD version string (e.g. ``"0.21.2"``).

    Runs ``FreeCADCmd --version`` and parses the output.

    Returns
    -------
    str
        Version string extracted from FreeCAD's output.

    Raises
    ------
    RuntimeError
        If the version cannot be determined.
    """
    freecad = find_freecad()
    result = _run([freecad, "--version"])
    if result["ok"] and result["stdout"]:
        # Output is typically "FreeCAD 0.21.2" or similar
        for line in result["stdout"].splitlines():
            line = line.strip()
            if not line:
                continue
            # Try to extract version number
            parts = line.split()
            for part in parts:
                # Look for something that looks like a version number
                if any(c.isdigit() for c in part) and "." in part:
                    return part.strip(",").strip()
            # Fallback: return the whole first line
            return line
    if result["stderr"]:
        raise RuntimeError(f"Failed to get FreeCAD version: {result['stderr']}")
    raise RuntimeError("Failed to get FreeCAD version (no output)")


def run_macro(
    script_path: str,
    timeout: int = 120,
    gui_required: bool = False,
    env: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Execute a FreeCAD Python macro script headlessly.

    Parameters
    ----------
    script_path : str
        Path to the ``.py`` macro file to execute.
    timeout : int
        Maximum seconds to wait for execution.

    Returns
    -------
    dict
        ``{"command": str, "returncode": int, "stdout": str, "stderr": str}``
    """
    freecad = find_freecad(gui_required=gui_required)
    script_path = str(Path(script_path).resolve())

    result = _run(
        _macro_command(freecad, script_path, gui_required=gui_required),
        timeout=timeout,
        env=env,
    )

    return {
        "command": result["command"],
        "returncode": result["returncode"],
        "stdout": result["stdout"],
        "stderr": result["stderr"],
    }


def run_macro_content(
    script_content: str,
    timeout: int = 120,
    gui_required: bool = False,
    env: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Execute macro content by writing it to a temp file first."""
    script_path = _write_temp_script(script_content)
    try:
        return run_macro(
            script_path,
            timeout=timeout,
            gui_required=gui_required,
            env=env,
        )
    finally:
        try:
            os.unlink(script_path)
        except OSError:
            pass
