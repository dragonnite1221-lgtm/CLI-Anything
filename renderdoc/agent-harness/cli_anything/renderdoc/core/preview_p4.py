# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403
# fmt: off
from .preview_p1 import HARNESS_VERSION, _attach_trajectory_ref, _compact_diff, _count_differences, _trajectory_dir  # noqa: E402,E501
from .preview_p3 import _diff_part0, _diff_part1, _diff_part2  # noqa: E402,E501
# fmt: on


def diff(
    handle_a,
    capture_path_a: str,
    event_a: int,
    handle_b,
    capture_path_b: str,
    event_b: int,
    *,
    compact: bool = True,
    root_dir: Optional[str] = None,
    force: bool = False,
    command: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a diff preview bundle for two RenderDoc events."""
    source_fingerprint = fingerprint_data(
        {
            "capture_a": fingerprint_file(capture_path_a),
            "event_a": event_a,
            "capture_b": fingerprint_file(capture_path_b),
            "event_b": event_b,
        }
    )
    prepared = prepare_bundle(
        software="renderdoc",
        recipe="diff",
        bundle_kind="diff",
        source_fingerprint=source_fingerprint,
        options={"compact": compact, "event_a": event_a, "event_b": event_b},
        harness_version=HARNESS_VERSION,
        project_path=capture_path_a,
        root_dir=root_dir,
        force=force,
    )
    if prepared["cached"]:
        manifest = dict(prepared["manifest"])
        manifest["cached"] = True
        return _attach_trajectory_ref(manifest)

    bundle_dir = prepared["bundle_dir"]
    artifacts_dir = prepared["artifacts_dir"]
    trajectory_dir = _trajectory_dir(capture_path_a, "diff", root_dir=root_dir)
    trajectory_rel = os.path.relpath(Path(trajectory_dir) / "trajectory.json", Path(bundle_dir))
    warnings: List[str] = []
    artifacts: List[Dict[str, Any]] = []

    thumb_a = os.path.join(artifacts_dir, "capture_a_thumb.png")
    thumb_a_result = handle_a.thumbnail(thumb_a, 512)
    _diff_part1(artifacts, bundle_dir, capture_path_a, thumb_a, thumb_a_result)

    thumb_b = os.path.join(artifacts_dir, "capture_b_thumb.png")
    thumb_b_result = handle_b.thumbnail(thumb_b, 512)
    _diff_part2(artifacts, bundle_dir, capture_path_b, thumb_b, thumb_b_result)

    outputs_a = textures_mod.save_action_outputs(
        handle_a.controller,
        event_a,
        os.path.join(artifacts_dir, "outputs_a"),
        file_format="png",
    )
    outputs_b = textures_mod.save_action_outputs(
        handle_b.controller,
        event_b,
        os.path.join(artifacts_dir, "outputs_b"),
        file_format="png",
    )
    _diff_part0(artifacts, bundle_dir, outputs_a, outputs_b, warnings)

    diff_data = diff_mod.diff_pipeline(handle_a.controller, event_a, handle_b.controller, event_b)
    if compact:
        diff_data = _compact_diff(diff_data) or {}

    diff_path = os.path.join(artifacts_dir, "pipeline_diff.json")
    write_json(diff_path, diff_data)
    artifacts.append(
        artifact_record(
            bundle_dir,
            diff_path,
            artifact_id="pipeline_diff",
            role="diff",
            kind="json",
            label="Pipeline diff",
            media_type="application/json",
        )
    )

    pipeline_a = pipeline_mod.get_pipeline_state(handle_a.controller, event_a)
    pipeline_a_path = os.path.join(artifacts_dir, "pipeline_a.json")
    write_json(pipeline_a_path, pipeline_a)
    artifacts.append(
        artifact_record(
            bundle_dir,
            pipeline_a_path,
            artifact_id="pipeline_a",
            role="metadata",
            kind="json",
            label=f"Pipeline state A at event {event_a}",
            media_type="application/json",
        )
    )

    pipeline_b = pipeline_mod.get_pipeline_state(handle_b.controller, event_b)
    pipeline_b_path = os.path.join(artifacts_dir, "pipeline_b.json")
    write_json(pipeline_b_path, pipeline_b)
    artifacts.append(
        artifact_record(
            bundle_dir,
            pipeline_b_path,
            artifact_id="pipeline_b",
            role="metadata",
            kind="json",
            label=f"Pipeline state B at event {event_b}",
            media_type="application/json",
        )
    )

    diff_count = _count_differences(diff_data)
    summary = {
        "headline": f"RenderDoc diff bundle created for events {event_a} vs {event_b}",
        "facts": {
            "event_a": event_a,
            "event_b": event_b,
            "capture_a": os.path.basename(capture_path_a),
            "capture_b": os.path.basename(capture_path_b),
            "difference_count": diff_count,
        },
        "warnings": warnings,
        "next_actions": [
            "Inspect pipeline_diff.json for resource, shader, and state changes.",
            "Compare A/B output-target images for visible regressions.",
        ],
    }

    manifest = finalize_bundle(
        bundle_dir=bundle_dir,
        bundle_id=prepared["bundle_id"],
        bundle_kind="diff",
        software="renderdoc",
        recipe="diff",
        source={
            "capture_path": os.path.abspath(capture_path_a),
            "capture_name": os.path.basename(capture_path_a),
            "capture_fingerprint": fingerprint_file(capture_path_a),
        },
        artifacts=artifacts,
        summary=summary,
        cache_key=prepared["cache_key"],
        generator={
            "entry_point": "cli-anything-renderdoc",
            "harness_version": HARNESS_VERSION,
            "command": command
            or f"cli-anything-renderdoc -c {capture_path_a} preview diff {event_a} {event_b} --capture-b {capture_path_b}",
        },
        status="partial" if warnings else "ok",
        warnings=warnings or None,
        context={"event_a": event_a, "event_b": event_b, "trajectory_path": trajectory_rel},
        metrics={"difference_count": diff_count},
        labels=["gpu", "capture", "diff", "preview"],
        source_bundles=[
            {"capture_path": os.path.abspath(capture_path_a), "event_id": event_a},
            {"capture_path": os.path.abspath(capture_path_b), "event_id": event_b},
        ],
    )
    trajectory = append_live_trajectory(
        trajectory_dir,
        software="renderdoc",
        recipe="diff",
        bundle_manifest=manifest,
        publish_reason="diff",
        project_path=os.path.abspath(capture_path_a),
        project_name=os.path.basename(capture_path_a),
        session_name=f"{os.path.splitext(os.path.basename(capture_path_a))[0]}-diff",
        command=command,
        stage_label=f"diff-{event_a}-vs-{event_b}",
        note=f"Pipeline diff for events {event_a} vs {event_b}",
    )
    manifest["_trajectory_path"] = trajectory["_trajectory_path"]
    manifest["cached"] = False
    return manifest
