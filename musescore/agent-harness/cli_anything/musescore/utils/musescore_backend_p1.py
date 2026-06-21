# ruff: noqa: F403, F405, E501
from .musescore_backend_base import *  # noqa: F403


def find_musescore() -> str:
    """Locate the mscore executable.

    Search order:
    1. MUSESCORE_PATH environment variable
    2. shutil.which("mscore")
    3. macOS app bundle: /Applications/MuseScore 4.app/Contents/MacOS/mscore
    4. Common Linux paths: /usr/bin/mscore4, /usr/local/bin/mscore4
    5. Windows: C:\\Program Files\\MuseScore 4\\bin\\MuseScore4.exe

    Returns:
        Absolute path to the mscore binary.

    Raises:
        RuntimeError: If mscore cannot be found.
    """
    # 1. Environment variable override
    env_path = os.environ.get("MUSESCORE_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path

    # 2. On PATH
    which = shutil.which("mscore")
    if which:
        return which

    # 3. Platform-specific paths
    system = platform.system()
    candidates = []

    if system == "Darwin":
        candidates = [
            "/Applications/MuseScore 4.app/Contents/MacOS/mscore",
            os.path.expanduser("~/Applications/MuseScore 4.app/Contents/MacOS/mscore"),
        ]
    elif system == "Linux":
        candidates = [
            "/usr/bin/mscore4",
            "/usr/local/bin/mscore4",
            "/usr/bin/mscore",
            "/usr/local/bin/mscore",
            "/snap/musescore/current/bin/mscore4",
        ]
    elif system == "Windows":
        candidates = [
            r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe",
            r"C:\Program Files (x86)\MuseScore 4\bin\MuseScore4.exe",
        ]

    for path in candidates:
        if os.path.isfile(path):
            return path

    raise RuntimeError(
        "MuseScore 4 (mscore) not found.\n\n"
        "Install MuseScore 4 from https://musescore.org/en/download\n\n"
        "Or set the MUSESCORE_PATH environment variable:\n"
        "  export MUSESCORE_PATH=/path/to/mscore\n\n"
        "Expected locations:\n"
        "  macOS:   /Applications/MuseScore 4.app/Contents/MacOS/mscore\n"
        "  Linux:   /usr/bin/mscore4\n"
        "  Windows: C:\\Program Files\\MuseScore 4\\bin\\MuseScore4.exe"
    )


def _filter_qt_noise(stderr: str) -> str:
    """Filter harmless Qt/QML warnings from mscore stderr."""
    if not stderr:
        return ""
    lines = []
    for line in stderr.splitlines():
        # Skip known Qt noise
        if any(
            pat in line
            for pat in [
                "qt.qml.typeregistration",
                "QML",
                "Qt WebEngine",
                "Fontconfig",
                "MESA-LOADER",
                "libpng warning",
                "IMKClient",
                "IMKInputSession",
            ]
        ):
            continue
        if line.strip():
            lines.append(line)
    return "\n".join(lines)


def run_mscore(
    args: list[str], capture_stdout: bool = True, timeout: int = 120
) -> subprocess.CompletedProcess:
    """Run mscore with the given arguments.

    Args:
        args: Command-line arguments (not including the mscore binary itself).
        capture_stdout: Whether to capture stdout.
        timeout: Timeout in seconds.

    Returns:
        CompletedProcess result.

    Raises:
        RuntimeError: If mscore exits with a non-zero code.
    """
    mscore = find_musescore()
    cmd = [mscore] + args

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    filtered_stderr = _filter_qt_noise(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(
            f"mscore exited with code {result.returncode}\n"
            f"Command: {' '.join(cmd)}\n"
            f"stderr: {filtered_stderr or result.stderr}"
        )

    result.stderr = filtered_stderr
    return result
