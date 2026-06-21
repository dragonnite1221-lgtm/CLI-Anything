# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
# fmt: off
from .freecad_live_preview_demo_p1 import DEFAULT_WAIT_TIMEOUT_S, FREECAD_WORKDIR, REPO_ROOT  # noqa: E402,E501
from .freecad_live_preview_demo_p29 import _is_noop_alignment, ensure_clean_dir, get_scenario, now_iso, run_cli, write_json  # noqa: E402,E501
from .freecad_live_preview_demo_p30 import extract_bundle_artifacts, generate_live_html, wait_for_bundle_update  # noqa: E402,E501
# fmt: on


def collect_demo(output_dir: Path, scenario_name: str) -> Path:
    scenario = get_scenario(scenario_name)
    run_dir = ensure_clean_dir(output_dir)
    snapshots_dir = run_dir / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    project_path = run_dir / scenario["project_file"]
    live_root = run_dir / "live-root"

    trajectory: Dict[str, Any] = {
        "protocol": "freecad-live-demo/v1",
        "created_at": now_iso(),
        "scenario": scenario_name,
        "scenario_title": scenario["title"],
        "scenario_subtitle": scenario["subtitle"],
        "repo_root": str(REPO_ROOT),
        "freecad_workdir": str(FREECAD_WORKDIR),
        "project_path": str(project_path),
        "live_root": str(live_root),
        "commands": [],
        "preview_events": [],
        "notes": [
            "All commands were executed against the real cli-anything-freecad entry point.",
            "All preview images came from the real FreeCAD live-preview poll session.",
            "The final video is a programmatic composition of these real artifacts.",
        ],
    }

    started_at = time.time()
    session_path: Optional[Path] = None
    session_dir: Optional[Path] = None
    live_recipe = "quick"
    expected_bundle_count = 0
    failure: Optional[BaseException] = None
    partial_timeline_path = run_dir / "trajectory.partial.json"

    try:
        for idx, step in enumerate(scenario["steps"]):
            argv = [arg.format(project_path=project_path, live_root=live_root) for arg in step["argv"]]
            result = run_cli(argv)
            result["index"] = idx
            result["id"] = step["id"]
            result["label"] = step["label"]
            result["timeline_start_s"] = round(result["started_at"] - started_at, 3)
            result["timeline_end_s"] = round(result["finished_at"] - started_at, 3)
            trajectory["commands"].append(result)
            write_json(partial_timeline_path, trajectory)

            if step.get("manual_session_payload"):
                payload = result.get("json") or {}
                session_path = Path(payload["_session_path"]).resolve()
                session_dir = Path(payload["_session_dir"]).resolve()
                expected_bundle_count = int(payload.get("bundle_count", 0))
                preview_sequence = len(trajectory["preview_events"]) + 1
                snapshot_dir = snapshots_dir / f"{preview_sequence:02d}_{step['id']}"
                snapshot_dir.mkdir(parents=True, exist_ok=True)
                copied = extract_bundle_artifacts(payload, snapshot_dir)
                preview_event = {
                    "sequence_index": preview_sequence,
                    "step_index": idx,
                    "step_id": step["id"],
                    "step_label": step["label"],
                    "ready_at": time.time(),
                    "timeline_ready_s": round(time.time() - started_at, 3),
                    "latency_s": round(time.time() - result["finished_at"], 3),
                    "bundle_count": expected_bundle_count,
                    "publish_reason": (payload.get("source_state") or {}).get("last_publish_reason"),
                    "session_path": str(session_path),
                    "session_dir": str(session_dir),
                    "snapshot_dir": str(snapshot_dir),
                    "copied_bundle": copied,
                }
                trajectory["preview_events"].append(preview_event)
                write_json(partial_timeline_path, trajectory)
                continue

            if step.get("wait_preview"):
                if session_path is None or session_dir is None:
                    raise RuntimeError(f"Step {step['id']} expected an active live session")
                if _is_noop_alignment(result):
                    continue
                expected_bundle_count += 1
                previous_bundle_id = trajectory["preview_events"][-1]["copied_bundle"]["bundle_id"] if trajectory["preview_events"] else None
                payload = wait_for_bundle_update(
                    session_path,
                    expected_bundle_count,
                    DEFAULT_WAIT_TIMEOUT_S,
                    previous_bundle_id=previous_bundle_id,
                )
                observed_bundle_count = int(payload.get("bundle_count", expected_bundle_count))
                expected_bundle_count = observed_bundle_count
                preview_sequence = len(trajectory["preview_events"]) + 1
                snapshot_dir = snapshots_dir / f"{preview_sequence:02d}_{step['id']}"
                snapshot_dir.mkdir(parents=True, exist_ok=True)
                copied = extract_bundle_artifacts(payload, snapshot_dir)
                ready_at = time.time()
                preview_event = {
                    "sequence_index": preview_sequence,
                    "step_index": idx,
                    "step_id": step["id"],
                    "step_label": step["label"],
                    "ready_at": ready_at,
                    "timeline_ready_s": round(ready_at - started_at, 3),
                    "latency_s": round(ready_at - result["finished_at"], 3),
                    "bundle_count": int(payload.get("bundle_count", 0)),
                    "publish_reason": (payload.get("source_state") or {}).get("last_publish_reason"),
                    "session_path": str(session_path),
                    "session_dir": str(session_dir),
                    "snapshot_dir": str(snapshot_dir),
                    "copied_bundle": copied,
                }
                trajectory["preview_events"].append(preview_event)
                write_json(partial_timeline_path, trajectory)

        if session_dir is not None:
            generate_live_html(session_dir, run_dir / "live.html")
            trajectory["final_session_dir"] = str(session_dir)
            trajectory["final_session_path"] = str(session_dir / "session.json")
            trajectory["final_live_html"] = str(run_dir / "live.html")
    except Exception as exc:
        failure = exc
        trajectory["error"] = {
            "type": type(exc).__name__,
            "message": str(exc),
        }
    finally:
        if project_path.is_file():
            try:
                stop_result = run_cli(
                    [
                        "-p",
                        str(project_path),
                        "preview",
                        "live",
                        "stop",
                        "--recipe",
                        live_recipe,
                        "--root-dir",
                        str(live_root),
                    ],
                    timeout=120,
                )
                trajectory["stop_command"] = {
                    "display_cmd": stop_result["display_cmd"],
                    "returncode": stop_result["returncode"],
                    "stdout": stop_result["stdout"],
                    "stderr": stop_result["stderr"],
                }
            except Exception as exc:  # pragma: no cover - cleanup best effort
                trajectory["stop_error"] = str(exc)

    trajectory["completed_at"] = now_iso()
    timeline_path = write_json(run_dir / "trajectory.json", trajectory)
    if failure is not None:
        raise RuntimeError(
            f"collect_demo failed for scenario {scenario_name!r}; partial trajectory written to {timeline_path}"
        ) from failure
    return timeline_path
