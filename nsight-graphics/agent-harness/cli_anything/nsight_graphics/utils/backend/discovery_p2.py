# ruff: noqa: F403, F405, E501
from .discovery_base import *  # noqa: F403


def _read_registry_installations(
    platform_system: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Read Nsight Graphics install records from the Windows uninstall registry."""
    platform_system = platform.system() if platform_system is None else platform_system
    if platform_system != "Windows":
        return []

    try:
        import winreg
    except ImportError:
        return []

    uninstall_roots = [
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        ),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
        ),
    ]

    def _query_value(key, name: str) -> Optional[str]:
        try:
            value, _ = winreg.QueryValueEx(key, name)
        except OSError:
            return None
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    records: list[dict[str, Any]] = []
    for hive, root in uninstall_roots:
        try:
            with winreg.OpenKey(hive, root) as root_key:
                index = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(root_key, index)
                    except OSError:
                        break
                    index += 1
                    try:
                        with winreg.OpenKey(root_key, subkey_name) as subkey:
                            display_name = _query_value(subkey, "DisplayName")
                            if (
                                not display_name
                                or "Nsight Graphics" not in display_name
                            ):
                                continue
                            records.append(
                                {
                                    "display_name": display_name,
                                    "display_version": _query_value(
                                        subkey, "DisplayVersion"
                                    ),
                                    "install_location": _query_value(
                                        subkey, "InstallLocation"
                                    ),
                                    "install_source": _query_value(
                                        subkey, "InstallSource"
                                    ),
                                    "uninstall_string": _query_value(
                                        subkey, "UninstallString"
                                    ),
                                    "publisher": _query_value(subkey, "Publisher"),
                                    "registry_key": f"HKLM\\{root}\\{subkey_name}",
                                }
                            )
                    except OSError:
                        continue
        except OSError:
            continue
    return records


def _normalized_install_key(path: str) -> str:
    """Normalize a path for install-root comparisons across slash styles."""
    normalized = os.path.normcase(os.path.normpath(path))
    return normalized.replace("\\", "/").rstrip("/")


def _override_value(
    env: dict[str, str],
    nsight_path: Optional[str] = None,
) -> str:
    """Resolve the effective override path from CLI or environment."""
    if nsight_path and nsight_path.strip():
        return nsight_path.strip()
    return env.get(ENV_VAR, "").strip()


def detect_tool_mode(binaries: dict[str, Optional[str]]) -> str:
    """Return compatibility mode for the discovered binaries."""
    has_unified = bool(binaries.get("ngfx"))
    has_split = bool(binaries.get("ngfx_capture") or binaries.get("ngfx_replay"))
    if has_unified and has_split:
        return "unified+split"
    if has_split:
        return "split"
    if has_unified:
        return "unified"
    return "missing"
