# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import _normalize_rsp_line, build_export_exec_command, build_rsp_exec_command, collect_materialized_outputs  # noqa: E402,E501
from .export_p2 import classify_export_result, default_log_path, expected_outputs_from_rsp  # noqa: E402,E501
# fmt: on


def _execute_insights(
    insights_exe: str,
    trace_path: str,
    exec_command: str,
    expected_outputs: list[str],
    log_path: str,
) -> dict[str, object]:
    backend.ensure_parent_dir(log_path)
    for output in expected_outputs:
        if "{" not in Path(output).name:
            backend.ensure_parent_dir(output)

    raw_command = backend.build_insights_command_line(
        insights_exe, trace_path, exec_command, log_path
    )
    run_result = backend.run_process(
        raw_command,
        wait=True,
    )
    log_info = backend.parse_unreal_log(log_path)

    actual_outputs: list[str] = []
    seen: set[str] = set()
    for output in expected_outputs:
        for match in collect_materialized_outputs(output):
            if match not in seen:
                actual_outputs.append(match)
                seen.add(match)

    output_status, status_message = classify_export_result(
        run_result, log_info, actual_outputs, expected_outputs
    )

    run_result.update(
        {
            "trace_path": str(Path(trace_path).expanduser().resolve()),
            "exec_command": exec_command,
            "expected_outputs": expected_outputs,
            "output_files": actual_outputs,
            "log_path": log_info["path"],
            "warnings": log_info["warnings"],
            "errors": log_info["errors"],
            "output_status": output_status,
            "status_message": status_message,
            "succeeded": output_status == "ok",
        }
    )
    return run_result


def execute_export(
    insights_exe: str,
    trace_path: str,
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
    log_path: str | None = None,
) -> dict[str, object]:
    """Execute a single TimingInsights exporter."""
    output_abs = str(Path(output_path).expanduser().resolve())
    resolved_log_path = log_path or default_log_path(output_abs)
    exec_command = build_export_exec_command(
        exporter,
        output_abs,
        insights_version=insights_version,
        columns=columns,
        threads=threads,
        timers=timers,
        start_time=start_time,
        end_time=end_time,
        region=region,
        counter=counter,
    )
    result = _execute_insights(
        insights_exe,
        trace_path,
        exec_command=exec_command,
        expected_outputs=[output_abs],
        log_path=resolved_log_path,
    )
    result["exporter"] = exporter
    return result


def execute_response_file(
    insights_exe: str,
    trace_path: str,
    rsp_path: str,
    *,
    insights_version: str | None = None,
    log_path: str | None = None,
) -> dict[str, object]:
    """Execute a response file batch export."""
    rsp_abs = str(Path(rsp_path).expanduser().resolve())
    resolved_log_path = log_path or default_log_path(rsp_abs)
    lines = Path(rsp_abs).read_text(encoding="utf-8", errors="replace").splitlines()

    normalized_lines: list[str] = []
    expected_outputs: list[str] = []
    for line in lines:
        normalized_line, normalized_output = _normalize_rsp_line(
            line, insights_version=insights_version
        )
        normalized_lines.append(normalized_line)
        if normalized_output:
            expected_outputs.append(normalized_output)

    if not expected_outputs:
        expected_outputs = expected_outputs_from_rsp(rsp_abs)

    temp_rsp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".rsp", delete=False, encoding="utf-8", newline="\n"
        ) as handle:
            temp_rsp_path = handle.name
            handle.write("\n".join(normalized_lines))
        result = _execute_insights(
            insights_exe,
            trace_path,
            exec_command=build_rsp_exec_command(temp_rsp_path),
            expected_outputs=expected_outputs,
            log_path=resolved_log_path,
        )
    finally:
        if temp_rsp_path:
            try:
                Path(temp_rsp_path).unlink()
            except OSError:
                pass
    result["response_file"] = rsp_abs
    result["executed_response_file"] = (
        str(Path(temp_rsp_path).resolve()) if temp_rsp_path else rsp_abs
    )
    result["exporter"] = "response-file"
    return result
