# ruff: noqa: F403, F405, E501
from .replay_base import *  # noqa: F403
# fmt: off
from .replay_p1 import _capture_type, _summarize_metadata  # noqa: E402,E501
from .replay_p2 import _compact_result, _summarize_functions, _summarize_objects  # noqa: E402,E501
from .replay_p3 import _has_files, _run_stdout_export  # noqa: E402,E501
from .replay_p4 import _analyze_logs, _build_analysis  # noqa: E402,E501
# fmt: on


def analyze_capture(
    *,
    nsight_path: str | None,
    capture_file: str,
    output_dir: str,
    metadata: bool,
    logs: bool,
    screenshot: bool,
    perf_report: bool,
) -> dict[str, Any]:
    """Analyze an existing capture through ngfx-replay metadata and replay outputs."""
    capture_path = Path(capture_file).resolve()
    if not capture_path.is_file():
        raise FileNotFoundError(f"Capture file does not exist: {capture_file}")
    capture_kind = _capture_type(capture_path)

    if not any((metadata, logs, screenshot, perf_report)):
        metadata = True
        logs = True
        perf_report = True

    report = backend.probe_installation(nsight_path=nsight_path)
    binaries = report["binaries"]
    if not binaries.get("ngfx_replay"):
        raise RuntimeError(
            "ngfx-replay.exe is required for replay analyze. Install Nsight Graphics "
            "with replay tools or set NSIGHT_GRAPHICS_PATH to an install containing ngfx-replay.exe."
        )

    output_root = Path(output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    before = backend.snapshot_files([str(output_root)])

    command_results: list[dict[str, Any]] = []
    metadata_files: dict[str, str | None] = {
        "summary": None,
        "functions": None,
        "objects": None,
    }
    logs_payload: dict[str, Any] = {
        "log_file": None,
        "errors_file": None,
        "log_line_count": 0,
        "error_line_count": 0,
        "error_summary": [],
        "raw_error_summary": [],
        "status": "not_requested",
    }
    screenshot_payload: dict[str, Any] = {"path": None, "present": False}
    perf_payload: dict[str, Any] = {"dir": None, "present": False}

    if metadata:
        for kind, flag, filename in [
            ("metadata", "--metadata", "metadata.txt"),
            ("metadata_functions", "--metadata-functions", "metadata_functions.txt"),
            ("metadata_objects", "--metadata-objects", "metadata_objects.json"),
        ]:
            output_file = output_root / filename
            command_results.append(
                _run_stdout_export(
                    binaries,
                    capture_file=str(capture_path),
                    output_file=output_file,
                    kind=kind,
                    replay_flag=flag,
                )
            )
            metadata_key = kind.replace("metadata_", "") if kind != "metadata" else "summary"
            metadata_files[metadata_key] = str(output_file) if output_file.is_file() else None

    _analyze_logs(binaries, capture_path, command_results, logs, logs_payload, output_root)

    if screenshot:
        screenshot_file = output_root / "metadata_screenshot.png"
        command = backend.build_replay_command(
            binaries,
            capture_file=str(capture_path),
            extra_args=["--metadata-screenshot", str(screenshot_file)],
        )
        result = backend.run_command(command, timeout=300)
        command_results.append(_compact_result("metadata_screenshot", result, output_file=screenshot_file))
        screenshot_payload = {
            "path": str(screenshot_file),
            "present": screenshot_file.is_file() and screenshot_file.stat().st_size > 0,
        }

    if perf_report:
        perf_dir = output_root / "perf_report"
        perf_dir.mkdir(parents=True, exist_ok=True)
        command = backend.build_replay_command(
            binaries,
            capture_file=str(capture_path),
            extra_args=[
                "--loop-count",
                "1",
                "--present-hidden",
                "--no-block-on-incompatibility",
                "--perf-report-dir",
                str(perf_dir),
            ],
        )
        result = backend.run_command(command, timeout=600)
        command_results.append(_compact_result("perf_report", result, output_file=perf_dir))
        perf_payload = {
            "dir": str(perf_dir),
            "present": _has_files(perf_dir),
        }

    after = backend.snapshot_files([str(output_root)])
    artifacts = backend.diff_snapshots(before, after)
    metadata_present = {
        "summary": bool(metadata_files["summary"] and Path(metadata_files["summary"]).is_file()),
        "functions": bool(metadata_files["functions"] and Path(metadata_files["functions"]).is_file()),
        "objects": bool(metadata_files["objects"] and Path(metadata_files["objects"]).is_file()),
    }
    metadata_summary = _summarize_metadata(Path(metadata_files["summary"]) if metadata_files["summary"] else None)
    function_summary = _summarize_functions(Path(metadata_files["functions"]) if metadata_files["functions"] else None)
    object_summary = _summarize_objects(Path(metadata_files["objects"]) if metadata_files["objects"] else None)
    all_commands_ok = all(item["ok"] for item in command_results)
    ok = all_commands_ok
    if screenshot:
        ok = ok and screenshot_payload["present"]
    if perf_report:
        ok = ok and perf_payload["present"]
    analysis = _build_analysis(
        capture_kind=capture_kind,
        metadata_requested=metadata,
        logs_requested=logs,
        screenshot_requested=screenshot,
        perf_requested=perf_report,
        metadata_present=metadata_present,
        metadata_summary=metadata_summary,
        object_summary=object_summary,
        function_summary=function_summary,
        logs_summary=logs_payload,
        screenshot_payload=screenshot_payload,
        perf_payload=perf_payload,
        command_results=command_results,
    )

    return {
        "ok": ok,
        "capture_file": str(capture_path),
        "capture_type": capture_kind,
        "version": report.get("version"),
        "tool_mode": report.get("tool_mode"),
        "compatibility_mode": report.get("compatibility_mode"),
        "replay_executable": binaries.get("ngfx_replay"),
        "output_dir": str(output_root),
        "requested_outputs": {
            "metadata": metadata,
            "logs": logs,
            "screenshot": screenshot,
            "perf_report": perf_report,
        },
        "command_results": command_results,
        "artifacts": artifacts,
        "artifact_count": len(artifacts),
        "metadata": {
            "files": metadata_files,
            "present": metadata_present,
            "summary": metadata_summary,
            "functions": function_summary,
            "objects": object_summary,
        },
        "logs": logs_payload,
        "screenshot": screenshot_payload,
        "perf_report": perf_payload,
        "analysis": analysis,
    }
