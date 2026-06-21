# ruff: noqa: F403, F405, E402, F401, E501
from .discovery_base import *
from .discovery_p1 import (
    _candidate_dirs_from_env,
    _default_windows_install_dirs,
    _scan_directory,
)
from .discovery_p2 import (
    _normalized_install_key,
    _read_registry_installations,
    detect_tool_mode,
)
from .discovery_p3 import _primary_executable, discover_binaries

from . import discovery_base as _coupbase  # noqa: E402


def list_installations(
    env: Optional[dict[str, str]] = None,
    which: Optional[Callable[[str], Optional[str]]] = None,
    glob_func: Optional[Callable[[str], list[str]]] = None,
    platform_system: Optional[str] = None,
    nsight_path: Optional[str] = None,
) -> dict[str, Any]:
    """List installed Nsight Graphics directories and versions."""
    env = os.environ if env is None else env
    which = shutil.which if which is None else which
    glob_func = glob.glob if glob_func is None else glob_func
    platform_system = platform.system() if platform_system is None else platform_system
    discovered = discover_binaries(
        env=env,
        which=which,
        glob_func=glob_func,
        platform_system=platform_system,
        nsight_path=nsight_path,
    )
    selected_path = _primary_executable(discovered["binaries"])
    candidates: list[str] = []
    for root in discovered["search_roots"]:
        candidates.append(root)
    if platform_system == "Windows":
        candidates.extend(_default_windows_install_dirs(glob_func))
    if nsight_path:
        candidates.extend(_candidate_dirs_from_env(nsight_path))
    if env.get(ENV_VAR, "").strip():
        candidates.extend(_candidate_dirs_from_env(env[ENV_VAR]))
    for key, names in _BINARY_CANDIDATES.items():
        for name in names:
            resolved = which(name)
            if resolved:
                candidates.append(str(Path(resolved).resolve().parent))
                break
    installations: list[dict[str, Any]] = []
    installation_keys: set[str] = set()
    for directory in _dedupe(candidates):
        found = _scan_directory(directory)
        if not found:
            continue
        primary = _primary_executable(found)
        key = f"fs::{os.path.normcase(os.path.normpath(directory))}"
        installation_keys.add(key)
        installations.append(
            {
                "install_root": directory,
                "version": _extract_version_from_path(directory)
                or _extract_version_from_path(primary or ""),
                "tool_mode": detect_tool_mode(found),
                "selected": bool(
                    primary
                    and selected_path
                    and (os.path.normcase(primary) == os.path.normcase(selected_path))
                ),
                "discovery_sources": ["filesystem"],
                "registered_only": False,
                "registry_key": None,
                "display_name": None,
                "display_version": None,
                "install_source": None,
                "binaries": {
                    binary_key: found.get(binary_key)
                    for binary_key in ("ngfx", "ngfx_ui", "ngfx_capture", "ngfx_replay")
                },
            }
        )
    for record in _coupbase._COUP_GLOBALS["_read_registry_installations"](
        platform_system=platform_system
    ):
        install_location = record.get("install_location")
        normalized_location = None
        if install_location:
            normalized_location = _normalized_install_key(install_location)
        guessed_version = _extract_version_from_text(
            record.get("display_name") or ""
        ) or _extract_version_from_text(record.get("display_version") or "")
        matched_entry = None
        if normalized_location:
            for item in installations:
                item_root = item.get("install_root")
                if not item_root:
                    continue
                normalized_root = _normalized_install_key(item_root)
                if (
                    normalized_root == normalized_location
                    or normalized_root.startswith(normalized_location + "/")
                    or normalized_location.startswith(normalized_root + "/")
                ):
                    matched_entry = item
                    break
        elif guessed_version:
            same_version = [
                item
                for item in installations
                if not item.get("registered_only")
                and item.get("version") == guessed_version
            ]
            if len(same_version) == 1:
                matched_entry = same_version[0]
        if matched_entry is not None:
            matched_entry["discovery_sources"] = _dedupe(
                list(matched_entry.get("discovery_sources", [])) + ["registry"]
            )
            matched_entry["display_name"] = record.get("display_name")
            matched_entry["display_version"] = record.get("display_version")
            matched_entry["registry_key"] = record.get("registry_key")
            matched_entry["install_source"] = record.get("install_source")
            if not matched_entry.get("version"):
                matched_entry["version"] = guessed_version
            continue
        registry_key = f"reg::{record['registry_key']}"
        if registry_key in installation_keys:
            continue
        installation_keys.add(registry_key)
        installations.append(
            {
                "install_root": install_location or None,
                "version": guessed_version,
                "tool_mode": "registered-only",
                "selected": False,
                "discovery_sources": ["registry"],
                "registered_only": True,
                "registry_key": record.get("registry_key"),
                "display_name": record.get("display_name"),
                "display_version": record.get("display_version"),
                "install_source": record.get("install_source"),
                "binaries": {
                    "ngfx": None,
                    "ngfx_ui": None,
                    "ngfx_capture": None,
                    "ngfx_replay": None,
                },
            }
        )
    installations.sort(
        key=lambda item: (
            not item["selected"],
            item.get("registered_only", False),
            item.get("version") or "",
            item.get("install_root") or item.get("display_name") or "",
        ),
        reverse=False,
    )
    return {
        "ok": bool(installations),
        "selected_executable": selected_path,
        "count": len(installations),
        "installations": installations,
        "cli_override": discovered.get("cli_override"),
        "env_override": discovered.get("env_override"),
        "registry_count": sum(
            (
                1
                for item in installations
                if "registry" in item.get("discovery_sources", [])
            )
        ),
    }
