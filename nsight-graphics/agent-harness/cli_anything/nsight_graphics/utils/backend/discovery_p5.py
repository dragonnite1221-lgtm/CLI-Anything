# ruff: noqa: F403, F405, E402, F401, E501
from .discovery_base import *
from .discovery_p2 import detect_tool_mode
from .discovery_p3 import _primary_executable, discover_binaries

from . import discovery_base as _coupbase  # noqa: E402


def get_version(binaries: dict[str, Optional[str]]) -> Optional[str]:
    """Best-effort version detection from CLI output or path."""
    preferred = (
        binaries.get("ngfx")
        or binaries.get("ngfx_capture")
        or binaries.get("ngfx_replay")
    )
    if not preferred:
        return None
    result = _coupbase._COUP_GLOBALS["run_command"](
        [preferred, "--version"], timeout=10
    )
    text = _combined_output(result)
    return _extract_version_from_text(text) or _extract_version_from_path(preferred)


def probe_installation(nsight_path: Optional[str] = None) -> dict[str, Any]:
    """Return an installation and capability report."""
    discovered = discover_binaries(nsight_path=nsight_path)
    binaries = discovered["binaries"]
    mode = detect_tool_mode(binaries)
    version = get_version(binaries)
    help_metadata = {
        "activities": [],
        "platforms": [],
        "general_options": [],
        "activity_options": {},
    }
    if binaries.get("ngfx"):
        help_result = _coupbase._COUP_GLOBALS["run_command"](
            [binaries["ngfx"], "--help-all"], timeout=15
        )
        help_metadata.update(parse_unified_help(_combined_output(help_result)))
    capture_options: list[str] = []
    if binaries.get("ngfx_capture"):
        capture_help = _coupbase._COUP_GLOBALS["run_command"](
            [binaries["ngfx_capture"], "--help"], timeout=15
        )
        capture_options = parse_option_help(_combined_output(capture_help))
    replay_options: list[str] = []
    if binaries.get("ngfx_replay"):
        replay_help = _coupbase._COUP_GLOBALS["run_command"](
            [binaries["ngfx_replay"], "--help"], timeout=15
        )
        replay_options = parse_option_help(_combined_output(replay_help))
    warnings: list[str] = []
    host_platform = platform.system()
    if host_platform != "Windows":
        warnings.append(
            "V1 is only verified on Windows-hosted Nsight Graphics installations."
        )
    if mode == "missing":
        warnings.append(INSTALL_INSTRUCTIONS)
    if mode == "split":
        warnings.append(
            "Split capture/replay tools were found without ngfx.exe; launch, attach, GPU Trace, and C++ Capture helpers may be unavailable."
        )
    return {
        "ok": _primary_executable(binaries) is not None,
        "tool_mode": mode,
        "compatibility_mode": mode,
        "resolved_executable": _primary_executable(binaries),
        "version": version,
        "host_platform": host_platform,
        "verified_host": host_platform == "Windows",
        "supported_activities": help_metadata["activities"],
        "supported_platforms": help_metadata["platforms"],
        "general_options": help_metadata["general_options"],
        "activity_options": help_metadata["activity_options"],
        "split_binaries_present": {
            "ngfx_capture": bool(binaries.get("ngfx_capture")),
            "ngfx_replay": bool(binaries.get("ngfx_replay")),
        },
        "capture_options": capture_options,
        "replay_options": replay_options,
        "binaries": binaries,
        "search_roots": discovered["search_roots"],
        "env_override": discovered["env_override"],
        "cli_override": discovered.get("cli_override"),
        "effective_override": discovered.get("effective_override"),
        "warnings": warnings,
    }
