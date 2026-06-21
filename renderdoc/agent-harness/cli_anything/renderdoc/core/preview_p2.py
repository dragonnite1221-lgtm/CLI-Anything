# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403
# fmt: off
from .preview_p1 import HARNESS_VERSION, RECIPES, _attach_trajectory_ref, _default_event_id, _trajectory_dir  # noqa: E402,E501
# fmt: on


def capture(
    handle,
    capture_path: str,
    recipe: str = "quick",
    *,
    event_id: Optional[int] = None,
    root_dir: Optional[str] = None,
    force: bool = False,
    command: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a capture preview bundle for a RenderDoc capture."""
    if recipe not in RECIPES:
        raise ValueError(
            f"Unknown preview recipe: {recipe!r}. Available: {', '.join(sorted(RECIPES))}"
        )

    config = RECIPES[recipe]
    source_fingerprint = fingerprint_file(capture_path)
    prepared = prepare_bundle(
        software="renderdoc",
        recipe=recipe,
        bundle_kind="capture",
        source_fingerprint=source_fingerprint,
        options={"event_id": event_id or "auto", **config},
        harness_version=HARNESS_VERSION,
        project_path=capture_path,
        root_dir=root_dir,
        force=force,
    )
    if prepared["cached"]:
        manifest = dict(prepared["manifest"])
        manifest["cached"] = True
        return _attach_trajectory_ref(manifest)

    bundle_dir = prepared["bundle_dir"]
    artifacts_dir = prepared["artifacts_dir"]
    trajectory_dir = _trajectory_dir(capture_path, recipe, root_dir=root_dir)
    trajectory_rel = os.path.relpath(Path(trajectory_dir) / "trajectory.json", Path(bundle_dir))
    warnings: List[str] = []
    artifacts: List[Dict[str, Any]] = []
    metadata = handle.metadata()
    action_summary = actions_mod.action_summary(handle.controller)

    hero_path = os.path.join(artifacts_dir, "hero.png")
    thumb_result = handle.thumbnail(hero_path, config["max_thumb_dim"])
    if thumb_result.get("error"):
        warnings.append(str(thumb_result["error"]))
    elif os.path.isfile(hero_path):
        artifacts.append(
            artifact_record(
                bundle_dir,
                hero_path,
                artifact_id="hero",
                role="hero",
                kind="image",
                label="Capture thumbnail",
                renderdoc_format=thumb_result.get("format"),
            )
        )

    chosen_event = event_id or _default_event_id(handle)
    output_count = 0
    if chosen_event is not None:
        outputs_dir = os.path.join(artifacts_dir, "outputs")
        output_results = textures_mod.save_action_outputs(handle.controller, chosen_event, outputs_dir, file_format="png")
        for index, item in enumerate(output_results):
            if item.get("error") or not item.get("path") or not os.path.isfile(item["path"]):
                warnings.append(item.get("error", f"missing output target {index}"))
                continue
            output_count += 1
            artifacts.append(
                artifact_record(
                    bundle_dir,
                    item["path"],
                    artifact_id=f"output_{index:02d}",
                    role="gallery",
                    kind="image",
                    label=item.get("label", f"Output {index}"),
                )
            )

        pipeline_state = pipeline_mod.get_pipeline_state(handle.controller, chosen_event)
        pipeline_path = os.path.join(artifacts_dir, "pipeline_state.json")
        write_json(pipeline_path, pipeline_state)
        artifacts.append(
            artifact_record(
                bundle_dir,
                pipeline_path,
                artifact_id="pipeline_state",
                role="metadata",
                kind="json",
                label=f"Pipeline state at event {chosen_event}",
                media_type="application/json",
            )
        )
    else:
        warnings.append("No drawcall event found; skipped output-target and pipeline capture.")

    summary_path = os.path.join(artifacts_dir, "action_summary.json")
    write_json(summary_path, action_summary)
    artifacts.append(
        artifact_record(
            bundle_dir,
            summary_path,
            artifact_id="action_summary",
            role="metadata",
            kind="json",
            label="Action summary",
            media_type="application/json",
        )
    )

    summary = {
        "headline": f"RenderDoc preview captured from {os.path.basename(capture_path)}",
        "facts": {
            "recipe": recipe,
            "api": metadata.get("api"),
            "event_id": chosen_event,
            "drawcalls": action_summary.get("drawcalls", 0),
            "output_targets": output_count,
        },
        "warnings": warnings,
        "next_actions": [
            "Inspect the hero thumbnail for a quick capture-level sanity check.",
            "Inspect output targets and pipeline_state.json for the selected event.",
        ],
    }

    manifest = finalize_bundle(
        bundle_dir=bundle_dir,
        bundle_id=prepared["bundle_id"],
        bundle_kind="capture",
        software="renderdoc",
        recipe=recipe,
        source={
            "capture_path": os.path.abspath(capture_path),
            "capture_name": os.path.basename(capture_path),
            "capture_fingerprint": source_fingerprint,
        },
        artifacts=artifacts,
        summary=summary,
        cache_key=prepared["cache_key"],
        generator={
            "entry_point": "cli-anything-renderdoc",
            "harness_version": HARNESS_VERSION,
            "command": command or f"cli-anything-renderdoc -c {capture_path} preview capture --recipe {recipe}",
        },
        status="partial" if warnings else "ok",
        warnings=warnings or None,
        context={"event_id": chosen_event, "trajectory_path": trajectory_rel},
        metrics={
            "drawcalls": action_summary.get("drawcalls", 0),
            "output_targets": output_count,
        },
        labels=["gpu", "capture", "preview"],
    )
    trajectory = append_live_trajectory(
        trajectory_dir,
        software="renderdoc",
        recipe=recipe,
        bundle_manifest=manifest,
        publish_reason="capture",
        project_path=os.path.abspath(capture_path),
        project_name=os.path.basename(capture_path),
        session_name=f"{os.path.splitext(os.path.basename(capture_path))[0]}-{recipe}",
        command=command,
        stage_label=f"event-{chosen_event}" if chosen_event is not None else "capture",
        note=f"RenderDoc capture preview for event {chosen_event}" if chosen_event is not None else None,
    )
    manifest["_trajectory_path"] = trajectory["_trajectory_path"]
    manifest["cached"] = False
    return manifest
