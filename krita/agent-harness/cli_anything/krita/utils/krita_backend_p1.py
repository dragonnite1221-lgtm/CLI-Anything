# ruff: noqa: F403, F405, E501
from .krita_backend_base import *  # noqa: F403


def find_krita() -> str:
    """Locate the Krita executable on the system.

    Search order:
      1. ``KRITA_PATH`` environment variable (explicit override).
      2. ``krita`` / ``krita.exe`` on ``PATH`` (via :func:`shutil.which`).
      3. Common Windows install directories (glob-matched).
      4. Common macOS application bundle path.

    Returns:
        Absolute path to the Krita executable.

    Raises:
        RuntimeError: If Krita cannot be found, with installation
            instructions in the message.
    """
    # 1. Environment variable override
    env_path = os.environ.get("KRITA_PATH")
    if env_path and os.path.isfile(env_path):
        return os.path.abspath(env_path)

    # 2. On PATH
    which = shutil.which("krita")
    if which:
        return os.path.abspath(which)

    # 3. Windows common locations
    if platform.system() == "Windows":
        win_patterns = [
            "C:/Program Files/Krita*/bin/krita.exe",
            "C:/Program Files (x86)/Krita*/bin/krita.exe",
            "C:/Program Files/Krita*/bin/krita-*.exe",
            "C:/Program Files (x86)/Krita*/bin/krita-*.exe",
        ]
        for pattern in win_patterns:
            matches = sorted(glob.glob(pattern), reverse=True)
            if matches:
                return os.path.abspath(matches[0])

    # 4. macOS application bundle
    if platform.system() == "Darwin":
        mac_path = "/Applications/krita.app/Contents/MacOS/krita"
        if os.path.isfile(mac_path):
            return mac_path

    raise RuntimeError(_INSTALL_INSTRUCTIONS)


def _run(
    args: list[str],
    *,
    timeout: int = 300,
    check: bool = False,
) -> Dict[str, Any]:
    """Run a subprocess and return a normalised result dict."""
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        result: Dict[str, Any] = {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "command": args,
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
            "command": args,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Krita process timed out after {timeout}s",
            "command": args,
        }


def _write_temp_script(content: str) -> str:
    """Write *content* to a temporary ``.py`` file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".py", prefix="krita_script_")
    try:
        os.write(fd, content.encode("utf-8"))
    finally:
        os.close(fd)
    return path


def get_version() -> str:
    """Return the Krita version string (e.g. ``"5.2.2"``)."""
    krita = find_krita()
    result = _run([krita, "--version"])
    if result["ok"] and result["stdout"]:
        # Output is typically "krita 5.2.2"
        line = result["stdout"].splitlines()[0]
        parts = line.strip().split()
        if len(parts) >= 2:
            return parts[-1]
        return line.strip()
    if result["stderr"]:
        raise RuntimeError(f"Failed to get Krita version: {result['stderr']}")
    raise RuntimeError("Failed to get Krita version (no output)")
