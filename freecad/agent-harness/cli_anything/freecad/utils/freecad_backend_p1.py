# ruff: noqa: F403, F405, E501
from .freecad_backend_base import *  # noqa: F403


def find_freecad(gui_required: bool = False) -> str:
    """Locate the FreeCAD console executable on the system.

    Search order:
      1. ``FREECAD_PATH`` environment variable (explicit override).
      2. Known executable names on ``PATH`` (via :func:`shutil.which`).
      3. Common Windows install directories (glob-matched).
      4. Common macOS application bundle path.
      5. Common Linux paths.

    Returns
    -------
    str
        Absolute path to the FreeCAD console executable.

    Raises
    ------
    RuntimeError
        If FreeCAD cannot be found, with installation instructions in
        the message.
    """
    # 1. Environment variable override
    env_path = os.environ.get("FREECAD_PATH")
    if env_path and os.path.isfile(env_path):
        return os.path.abspath(env_path)

    names = _FREECAD_GUI_NAMES if gui_required else _FREECAD_CMD_NAMES

    # 2. On PATH
    for name in names:
        which = shutil.which(name)
        if which:
            return os.path.abspath(which)

    # 3. Windows common locations
    if platform.system() == "Windows":
        win_patterns = [
            "C:/Program Files/FreeCAD*/bin/FreeCADCmd.exe",
            "C:/Program Files (x86)/FreeCAD*/bin/FreeCADCmd.exe",
            "C:/Program Files/FreeCAD*/bin/FreeCAD.exe",
            "C:/Program Files (x86)/FreeCAD*/bin/FreeCAD.exe",
        ]
        for pattern in win_patterns:
            matches = sorted(glob.glob(pattern), reverse=True)
            if matches:
                return os.path.abspath(matches[0])

    # 4. macOS application bundle
    if platform.system() == "Darwin":
        mac_paths = [
            "/Applications/FreeCAD.app/Contents/MacOS/FreeCADCmd",
            "/Applications/FreeCAD.app/Contents/MacOS/FreeCAD",
        ]
        for mac_path in mac_paths:
            if os.path.isfile(mac_path):
                return mac_path

    # 5. Common Linux paths
    if platform.system() == "Linux":
        linux_paths = [
            "/usr/bin/freecadcmd",
            "/usr/bin/freecad",
            "/usr/local/bin/freecadcmd",
            "/usr/local/bin/freecad",
            "/snap/bin/freecad",
        ]
        for linux_path in linux_paths:
            if os.path.isfile(linux_path):
                return linux_path

    raise RuntimeError(_INSTALL_INSTRUCTIONS)


def _run(
    args: list[str],
    *,
    timeout: int = 120,
    check: bool = False,
    env: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Run a subprocess and return a normalised result dict."""
    try:
        proc_env = os.environ.copy()
        if env:
            proc_env.update(env)
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=proc_env,
        )
        result: Dict[str, Any] = {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "command": " ".join(args),
        }
        if check and proc.returncode != 0:
            raise subprocess.CalledProcessError(
                proc.returncode,
                args,
                proc.stdout,
                proc.stderr,
            )
        return result
    except FileNotFoundError as exc:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc),
            "command": " ".join(args),
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"FreeCAD process timed out after {timeout}s",
            "command": " ".join(args),
        }


def _write_temp_script(content: str) -> str:
    """Write *content* to a temporary ``.py`` file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".py", prefix="freecad_macro_")
    try:
        os.write(fd, content.encode("utf-8"))
    finally:
        os.close(fd)
    return path
