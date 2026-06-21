# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403

# fmt: off
from .preview_p1 import _metrics, _project_fingerprint, _seconds_to_timecode  # noqa: E402,E501
# fmt: on


def capture(
    session: Session,
    recipe: str = "quick",
    *,
    root_dir: Optional[str] = None,
    force: bool = False,
    command: Optional[str] = None,
) -> Dict[str, Any]:
    """Render a preview bundle for the active Shotcut project."""
    if not session.is_open:
        raise RuntimeError("No project is open")
    if recipe not in RECIPES:
        raise ValueError(
            f"Unknown preview recipe: {recipe!r}. Available: {', '.join(sorted(RECIPES))}"
        )

    config = RECIPES[recipe]
    source_fingerprint = _project_fingerprint(session)
    prepared = prepare_bundle(
        software="shotcut",
        recipe=recipe,
        bundle_kind="capture",
        source_fingerprint=source_fingerprint,
        options={k: config[k] for k in ("preset", "width", "height", "sample_ratios")},
        harness_version=HARNESS_VERSION,
        project_path=session.project_path,
        root_dir=root_dir,
        force=force,
    )
    if prepared["cached"]:
        manifest = dict(prepared["manifest"])
        manifest["cached"] = True
        return manifest

    bundle_dir = prepared["bundle_dir"]
    artifacts_dir = prepared["artifacts_dir"]
    preview_clip = os.path.join(artifacts_dir, "preview.mp4")

    render_result = export_mod.render(
        session,
        preview_clip,
        preset=config["preset"],
        width=config["width"],
        height=config["height"],
        overwrite=True,
        prefer_ffmpeg=True,
    )
    clip_meta = media_mod.probe_media(preview_clip)
    duration_s = float(clip_meta.get("duration_seconds", 0.0) or 0.0)
    video_stream = (clip_meta.get("video_streams") or [{}])[0]
    width = int(video_stream.get("width") or config["width"])
    height = int(video_stream.get("height") or config["height"])

    warnings: List[str] = []
    artifacts = [
        artifact_record(
            bundle_dir,
            preview_clip,
            artifact_id="clip",
            role="preview-clip",
            kind="clip",
            label="Quick preview render",
            width=width,
            height=height,
            duration_s=round(duration_s, 3),
            render_method=render_result.get("method"),
        )
    ]

    for index, ratio in enumerate(config["sample_ratios"]):
        capture_time = duration_s * ratio if duration_s > 0 else 0.0
        image_path = os.path.join(artifacts_dir, f"frame_{index + 1:02d}.png")
        try:
            media_mod.generate_thumbnail(
                preview_clip,
                image_path,
                _seconds_to_timecode(capture_time),
                config["thumbnail_width"],
                config["thumbnail_height"],
            )
        except Exception as exc:
            warnings.append(f"frame sample {index + 1} failed: {exc}")
            continue

        role = "hero" if abs(ratio - 0.5) < 1e-9 else "gallery"
        label = "Midpoint frame" if role == "hero" else f"Sample frame {index + 1}"
        artifacts.append(
            artifact_record(
                bundle_dir,
                image_path,
                artifact_id=f"frame_{index + 1:02d}",
                role=role,
                kind="image",
                label=label,
                width=config["thumbnail_width"],
                height=config["thumbnail_height"],
                time_s=round(capture_time, 3),
            )
        )

    metrics = _metrics(session)
    summary = {
        "headline": (
            f"Shotcut {recipe} preview rendered at {width}x{height}"
            + (f" for {duration_s:.2f}s" if duration_s > 0 else "")
        ),
        "facts": {
            "recipe": recipe,
            "resolution": f"{width}x{height}",
            "duration_s": round(duration_s, 3),
            "track_count": metrics["track_count"],
            "producer_count": metrics["producer_count"],
            "filter_count": metrics["filter_count"],
        },
        "warnings": warnings,
        "next_actions": [
            "Inspect the preview clip for pacing, timing, and cut order.",
            "Use cli-hub previews html on the bundle for a richer inspection page.",
        ],
    }

    manifest = finalize_bundle(
        bundle_dir=bundle_dir,
        bundle_id=prepared["bundle_id"],
        bundle_kind="capture",
        software="shotcut",
        recipe=recipe,
        source={
            "project_path": session.project_path,
            "project_name": os.path.basename(session.project_path)
            if session.project_path
            else None,
            "project_fingerprint": source_fingerprint,
            "session_id": session.session_id,
        },
        artifacts=artifacts,
        summary=summary,
        cache_key=prepared["cache_key"],
        generator={
            "entry_point": "cli-anything-shotcut",
            "harness_version": HARNESS_VERSION,
            "command": command
            or f"cli-anything-shotcut preview capture --recipe {recipe}",
        },
        status="partial" if warnings else "ok",
        warnings=warnings or None,
        context={"profile": metrics["profile"]},
        metrics={k: v for k, v in metrics.items() if k != "profile"},
        labels=["video", "timeline", "preview"],
    )
    manifest["cached"] = False
    return manifest
