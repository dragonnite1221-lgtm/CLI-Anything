# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import _filename_arg  # noqa: E402,E501
# fmt: on


def _token_output_path(command_line: str) -> str | None:
    try:
        tokens = shlex.split(command_line, posix=False)
    except ValueError:
        return None
    if len(tokens) < 2:
        return None
    return tokens[1].strip('"')


def expected_outputs_from_rsp(rsp_path: str) -> list[str]:
    """Read a response file and infer output files from each command line."""
    path = Path(rsp_path).expanduser().resolve()
    outputs: list[str] = []
    if not path.is_file():
        return outputs

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        output = _token_output_path(stripped)
        if output:
            outputs.append(str(Path(output).expanduser().resolve()))
    return outputs


def normalize_response_file_lines(
    lines: list[str], *, insights_version: str | None = None
) -> list[str]:
    """Normalize response-file output filename tokens for UnrealInsights parsing."""
    normalized_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            normalized_lines.append(line)
            continue
        try:
            tokens = shlex.split(stripped, posix=False)
        except ValueError:
            normalized_lines.append(line)
            continue
        if len(tokens) < 2:
            normalized_lines.append(line)
            continue
        output_path = tokens[1].strip('"')
        filename_token = _filename_arg(output_path, insights_version=insights_version)
        normalized_lines.append(" ".join([tokens[0], filename_token, *tokens[2:]]))
    return normalized_lines


def normalized_response_file_path(
    rsp_path: str, *, insights_version: str | None = None
) -> str:
    """Return a normalized temporary response file path when normalization changes content."""
    path = Path(rsp_path).expanduser().resolve()
    if not path.is_file():
        return str(path)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    normalized_lines = normalize_response_file_lines(
        lines, insights_version=insights_version
    )
    if normalized_lines == lines:
        return str(path)

    handle = tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        errors="replace",
        suffix=".rsp",
        prefix=f"{path.stem}-normalized-",
        delete=False,
    )
    with handle:
        handle.write("\n".join(normalized_lines))
        handle.write("\n")
    return str(Path(handle.name).resolve())


def default_log_path(reference_path: str, suffix: str = ".insights.log") -> str:
    path = Path(reference_path).expanduser().resolve()
    return str(path.with_name(f"{path.stem}{suffix}"))


def classify_export_result(
    run_result: dict[str, object],
    log_info: dict[str, object],
    actual_outputs: list[str],
    expected_outputs: list[str],
) -> tuple[str, str]:
    """Classify an Unreal Insights exporter result for agent diagnostics."""
    if run_result.get("timed_out"):
        return "timed_out", "UnrealInsights.exe timed out before export completion."
    if run_result.get("exit_code") != 0:
        return (
            "process_failed",
            f"UnrealInsights.exe exited with code {run_result.get('exit_code')}.",
        )
    if actual_outputs:
        return "ok", f"Materialized {len(actual_outputs)} output file(s)."

    errors = list(log_info.get("errors") or [])
    if errors:
        return "exporter_error", errors[-1]
    if expected_outputs:
        return (
            "no_output",
            "Exporter completed without materializing expected outputs; the trace may not contain matching data.",
        )
    return (
        "no_expected_outputs",
        "No output paths were inferred for this export command.",
    )
