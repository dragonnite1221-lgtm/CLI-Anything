# ruff: noqa: F403, F405, E402, F401, E501
from .discovery_base import *

from . import discovery_base as _coupbase  # noqa: E402


def _scan_directory(directory: str) -> dict[str, str]:
    """Scan a directory for known Nsight binaries."""
    found: dict[str, str] = {}
    base = Path(directory)
    if not base.is_dir():
        return found
    for key, candidates in _BINARY_CANDIDATES.items():
        for candidate in candidates:
            path = base / candidate
            if path.is_file():
                found[key] = str(path.resolve())
                break
    return found


def _candidate_dirs_from_env(path_value: str) -> list[str]:
    """Resolve environment override into candidate directories."""
    if not path_value:
        return []
    path = Path(path_value)
    candidates: list[str] = []
    if path.is_file():
        candidates.append(str(path.parent))
    else:
        candidates.append(str(path))
        candidates.append(str(path / "host" / "windows-desktop-nomad-x64"))
        candidates.append(str(path / "windows-desktop-nomad-x64"))
    return _dedupe([p for p in candidates if Path(p).exists()])


def _fixed_windows_drive_roots() -> list[str]:
    """Return fixed-drive roots such as C: and D: on Windows."""
    if platform.system() != "Windows":
        return []
    try:
        drive_mask = ctypes.windll.kernel32.GetLogicalDrives()
        get_drive_type = ctypes.windll.kernel32.GetDriveTypeW
    except Exception:
        return []
    DRIVE_FIXED = 3
    drives: list[str] = []
    for index in range(26):
        if not drive_mask & 1 << index:
            continue
        letter = chr(ord("A") + index)
        root = f"{letter}:\\"
        try:
            if get_drive_type(root) == DRIVE_FIXED:
                drives.append(f"{letter}:")
        except Exception:
            continue
    return drives


def _default_windows_install_dirs(glob_func: Callable[[str], list[str]]) -> list[str]:
    """Return default Windows install directories for Nsight Graphics."""
    drive_roots = _coupbase._COUP_GLOBALS["_fixed_windows_drive_roots"]()
    if not drive_roots:
        drive_roots = ["C:"]
    patterns: list[str] = []
    for drive in drive_roots:
        patterns.extend(
            [
                f"{drive}/Program Files/NVIDIA Corporation/Nsight Graphics */host/windows-desktop-nomad-x64",
                f"{drive}/Program Files (x86)/NVIDIA Corporation/Nsight Graphics */host/windows-desktop-nomad-x64",
            ]
        )
    matches: list[str] = []
    for pattern in patterns:
        matches.extend(glob_func(pattern))
    return _dedupe(
        sorted(
            matches,
            key=lambda path: (
                _version_sort_key(_extract_version_from_path(path)),
                path,
            ),
            reverse=True,
        )
    )
