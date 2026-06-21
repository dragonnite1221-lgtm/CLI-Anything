# ruff: noqa: F403, F405, E402, F401, E501
from .pm2_backend_base import *

from . import pm2_backend_base as _coupbase  # noqa: E402


def _augmented_path(base_path: str | None = None) -> str:
    """Return PATH string with _EXTRA_PATH_DIRS prepended if missing."""
    path = base_path if base_path is not None else os.environ.get("PATH", "")
    for p in _EXTRA_PATH_DIRS:
        if p not in path:
            path = f"{p}:{path}"
    return path


def _find_pm2() -> str:
    """Locate the pm2 binary on the system.

    Checks common Homebrew and global npm paths in addition to PATH.

    Returns:
        Absolute path to the pm2 binary.

    Raises:
        RuntimeError: If pm2 is not found.
    """
    pm2_path = shutil.which("pm2", path=_augmented_path())
    if pm2_path is None:
        raise RuntimeError(
            "pm2 not found on this system. Install it with: npm install -g pm2"
        )
    return pm2_path


_PM2_BIN: str | None = None


def _get_pm2() -> str:
    """Get cached pm2 binary path."""
    global _PM2_BIN
    if _PM2_BIN is None:
        _PM2_BIN = _find_pm2()
    return _PM2_BIN


def _build_env() -> dict[str, str]:
    """Build environment dict with proper PATH for subprocess."""
    env = os.environ.copy()
    env["PATH"] = _augmented_path(env.get("PATH", ""))
    return env


def run_pm2(
    *args: str, capture_json: bool = False, timeout: int = 30
) -> dict[str, Any]:
    """Run a pm2 command and return the result.

    Args:
        *args: Arguments to pass to pm2 (e.g., "jlist", "restart", "myapp").
        capture_json: If True, attempt to parse stdout as JSON.
        timeout: Command timeout in seconds.

    Returns:
        Dict with keys:
            - success (bool): Whether command exited with code 0.
            - returncode (int): Process return code.
            - stdout (str): Raw stdout.
            - stderr (str): Raw stderr.
            - data (Any): Parsed JSON data if capture_json=True, else None.
    """
    pm2 = _coupbase._COUP_GLOBALS["_get_pm2"]()
    cmd = [pm2, *args]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, env=_build_env()
        )
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s: {' '.join(cmd)}",
            "data": None,
        }
    except FileNotFoundError:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"pm2 binary not found at: {pm2}",
            "data": None,
        }
    parsed_data = None
    if capture_json and result.returncode == 0:
        try:
            parsed_data = json.loads(result.stdout)
        except (json.JSONDecodeError, ValueError):
            stdout = result.stdout.strip()
            for start_char, end_char in [("[", "]"), ("{", "}")]:
                idx_start = stdout.find(start_char)
                idx_end = stdout.rfind(end_char)
                if idx_start != -1 and idx_end > idx_start:
                    try:
                        parsed_data = json.loads(stdout[idx_start : idx_end + 1])
                        break
                    except (json.JSONDecodeError, ValueError):
                        continue
    return {
        "success": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "data": parsed_data,
    }


def pm2_jlist() -> list[dict[str, Any]]:
    """Get JSON list of all PM2 processes.

    Returns:
        List of process info dicts, or empty list on failure.
    """
    result = run_pm2("jlist", capture_json=True)
    if result["success"] and isinstance(result["data"], list):
        return result["data"]
    return []
