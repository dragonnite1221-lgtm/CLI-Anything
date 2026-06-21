# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403


def _quote(value: str) -> str:
    return f'"{value}"'


def _is_legacy_unrealinsights(version: str | None) -> bool:
    return bool(version and version.startswith("5.3"))


def _windows_short_path(path: Path) -> str | None:
    if os.name != "nt":
        return None
    buffer = ctypes.create_unicode_buffer(32768)
    result = ctypes.windll.kernel32.GetShortPathNameW(str(path), buffer, len(buffer))
    if result == 0:
        return None
    return buffer.value


def _legacy_filename_arg(output_path: str) -> str:
    path = Path(output_path).expanduser().resolve()
    path_str = str(path)
    if " " not in path_str:
        return path_str

    parent = path.parent
    short_parent = _windows_short_path(parent)
    if not short_parent:
        raise RuntimeError(
            f"Legacy UnrealInsights export requires a path without spaces or a resolvable short path: {path}"
        )
    if " " in path.name:
        raise RuntimeError(
            f"Legacy UnrealInsights export does not support spaces in the output filename: {path.name}"
        )
    return str(Path(short_parent) / path.name)


def _modern_filename_arg(output_path: str) -> str:
    """Build a filename token compatible with modern UnrealInsights builds."""
    path = Path(output_path).expanduser().resolve()
    path_str = str(path)
    if os.name != "nt":
        return _quote(path_str)
    if " " not in path_str:
        return path_str

    short_path = _windows_short_path(path)
    if short_path:
        return short_path

    raise RuntimeError(
        "UnrealInsights export requires a path without spaces or a resolvable short path on Windows: "
        f"{path}"
    )


def _filename_arg(output_path: str, insights_version: str | None = None) -> str:
    output_abs = str(Path(output_path).expanduser().resolve())
    if _is_legacy_unrealinsights(insights_version):
        return _legacy_filename_arg(output_abs)
    return _modern_filename_arg(output_abs)


def _option_value_arg(name: str, value: str) -> str:
    if not any(ch.isspace() for ch in value):
        return f"-{name}={value}"
    return f"-{name}={_quote(value)}"


def build_export_exec_command(
    exporter: str,
    output_path: str,
    *,
    insights_version: str | None = None,
    columns: str | None = None,
    threads: str | None = None,
    timers: str | None = None,
    start_time: float | None = None,
    end_time: float | None = None,
    region: str | None = None,
    counter: str | None = None,
) -> str:
    """Build a TimingInsights exporter command string."""
    if exporter not in EXPORTER_COMMANDS:
        raise RuntimeError(f"Unsupported exporter: {exporter}")

    output_abs = str(Path(output_path).expanduser().resolve())
    filename_token = _filename_arg(output_abs, insights_version=insights_version)

    parts = [EXPORTER_COMMANDS[exporter], filename_token]

    if counter:
        parts.append(_option_value_arg("counter", counter))
    if columns:
        parts.append(_option_value_arg("columns", columns))
    if threads:
        parts.append(_option_value_arg("threads", threads))
    if timers:
        parts.append(_option_value_arg("timers", timers))
    if start_time is not None:
        parts.append(f"-startTime={start_time}")
    if end_time is not None:
        parts.append(f"-endTime={end_time}")
    if region:
        parts.append(_option_value_arg("region", region))

    return " ".join(parts)


def build_rsp_exec_command(rsp_path: str) -> str:
    """Build the response-file execution token."""
    return f"@={Path(rsp_path).expanduser().resolve()}"


def _normalize_rsp_line(
    line: str, insights_version: str | None = None
) -> tuple[str, str | None]:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return line, None

    match = re.match(
        r'^(?P<indent>\s*)(?P<command>\S+)\s+(?P<output>"[^"]*"|\S+)(?P<rest>.*)$', line
    )
    if not match:
        return line, None

    command = match.group("command")
    if command not in EXPORTER_COMMANDS.values():
        return line, None

    output_path = match.group("output").strip('"')
    normalized_output = _filename_arg(output_path, insights_version=insights_version)
    normalized_line = (
        f"{match.group('indent')}{command} {normalized_output}{match.group('rest')}"
    )
    return normalized_line, str(Path(output_path).expanduser().resolve())


def _path_contains_placeholders(path: Path) -> bool:
    return "{counter}" in path.name or "{region}" in path.name


def collect_materialized_outputs(output_path: str) -> list[str]:
    """Collect actual output files for a requested exporter path."""
    path = Path(output_path).expanduser().resolve()
    if _path_contains_placeholders(path):
        pattern = path.name.replace("{counter}", "*").replace("{region}", "*")
        return sorted(
            str(match.resolve())
            for match in path.parent.glob(pattern)
            if match.is_file()
        )
    if path.is_file():
        return [str(path)]
    return []
