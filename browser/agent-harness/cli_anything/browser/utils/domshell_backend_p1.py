# ruff: noqa: F403, F405, E501
from .domshell_backend_base import *  # noqa: F403


def _build_server_args() -> list[str]:
    """Build server args at call time so env var changes are honored."""
    token = os.environ.get("DOMSHELL_TOKEN", "")
    if not token:
        raise RuntimeError(
            "DOMSHELL_TOKEN environment variable is required.\n"
            "Set it to the auth token of your running DOMShell server.\n"
            "Example: export DOMSHELL_TOKEN=<token from DOMShell startup>"
        )
    port = os.environ.get("DOMSHELL_PORT", "3001")
    return [
        "-p",
        "@apireno/domshell",
        "domshell-proxy",
        "--port",
        port,
        "--token",
        token,
    ]


_daemon_session: Optional[ClientSession] = None
_daemon_read: Optional[Any] = None
_daemon_write: Optional[Any] = None
_daemon_client_context: Optional[Any] = None  # Store stdio_client context manager


def _check_npx() -> bool:
    """Check if npx is available."""
    return shutil.which("npx") is not None


def _check_npx_has_domshell() -> bool:
    """Check if DOMShell package is available to npx."""
    try:
        result = subprocess.run(
            ["npx", "@apireno/domshell", "--version"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def is_available() -> tuple[bool, str]:
    """Check if DOMShell MCP server is available.

    Returns:
        (available, message): Tuple of availability status and descriptive message.

    Examples:
        >>> is_available()
        (True, "DOMShell v1.0.0 is available")
        >>> is_available()
        (False, "npx not found. Install Node.js from https://nodejs.org/")
    """
    if not _check_npx():
        return (
            False,
            "npx not found. Install Node.js from https://nodejs.org/ "
            "Then run: npm install -g npx",
        )

    if not _check_npx_has_domshell():
        return (
            False,
            "DOMShell not found. Run `npx @apireno/domshell --version` once\n"
            "Note: The first run may download the package (10-50 MB).",
        )

    # Try to get version
    try:
        result = subprocess.run(
            ["npx", "@apireno/domshell", "--version"],
            capture_output=True,
            timeout=10,
            text=True,
        )
        version = result.stdout.strip() or "unknown"
        return True, f"DOMShell {version} is available"
    except Exception as e:
        return False, f"DOMShell check failed: {e}"


async def _stop_daemon() -> None:
    """Stop persistent daemon mode."""
    global _daemon_session, _daemon_read, _daemon_write, _daemon_client_context

    if _daemon_session is None:
        return

    try:
        await _daemon_session.__aexit__(None, None, None)
        if _daemon_client_context:
            await _daemon_client_context.__aexit__(None, None, None)
    except Exception:
        pass  # Ignore cleanup errors
    finally:
        _daemon_session = None
        _daemon_read = None
        _daemon_write = None
        _daemon_client_context = None
