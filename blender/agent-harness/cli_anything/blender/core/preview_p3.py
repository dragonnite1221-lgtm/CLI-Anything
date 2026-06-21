# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403

# fmt: off
from .preview_p1 import _project_fingerprint  # noqa: E402,E501
from .preview_p2 import _ensure_preview_rig, _render_image  # noqa: E402,E501
# fmt: on


def capture(
    session: Session,
    recipe: str = "quick",
    *,
    root_dir: Optional[str] = None,
    force: bool = False,
    command: Optional[str] = None,
) -> Dict[str, Any]:
    """Render a preview bundle for the active Blender project."""
    if not session.has_project():
        raise RuntimeError("No scene loaded. Use 'scene new' or 'scene open' first.")
    if recipe not in RECIPES:
        raise ValueError(
            f"Unknown preview recipe: {recipe!r}. Available: {', '.join(sorted(RECIPES))}"
        )

    config = RECIPES[recipe]
    source_fingerprint = _project_fingerprint(session)
    prepared = prepare_bundle(
        software="blender",
        recipe=recipe,
        bundle_kind="capture",
        source_fingerprint=source_fingerprint,
        options=config,
        harness_version=HARNESS_VERSION,
        project_path=session.project_path,
        root_dir=root_dir,
        force=force,
    )
    if prepared["cached"]:
        manifest = dict(prepared["manifest"])
        manifest["cached"] = True
        return manifest

    project = copy.deepcopy(session.get_project())
    warnings = _ensure_preview_rig(project)
    bundle_dir = prepared["bundle_dir"]
    artifacts_dir = prepared["artifacts_dir"]
    frame = int(project.get("scene", {}).get("frame_current", 1) or 1)

    hero_path = os.path.join(artifacts_dir, "hero.png")
    hero_result, hero_settings = _render_image(
        project,
        hero_path,
        preset=config["primary_preset"],
        frame=frame,
        timeout=config["timeout"],
    )

    alt_path = os.path.join(artifacts_dir, "workbench.png")
    alt_result, alt_settings = _render_image(
        project,
        alt_path,
        preset=config["secondary_preset"],
        frame=frame,
        timeout=config["timeout"],
        resolution_percentage=config["secondary_resolution_percentage"],
    )

    def _size(settings: Dict[str, Any]) -> Tuple[int, int]:
        effective = settings.get("effective_resolution", "0x0").split("x", 1)
        try:
            return int(effective[0]), int(effective[1])
        except (ValueError, IndexError):
            return 0, 0

    hero_w, hero_h = _size(hero_settings)
    alt_w, alt_h = _size(alt_settings)

    artifacts = [
        artifact_record(
            bundle_dir,
            hero_result["output"],
            artifact_id="hero",
            role="hero",
            kind="image",
            label="Eevee preview",
            width=hero_w or None,
            height=hero_h or None,
            preset=config["primary_preset"],
            blender_method=hero_result.get("method"),
        ),
        artifact_record(
            bundle_dir,
            alt_result["output"],
            artifact_id="workbench",
            role="gallery",
            kind="image",
            label="Workbench structure view",
            width=alt_w or None,
            height=alt_h or None,
            preset=config["secondary_preset"],
            blender_method=alt_result.get("method"),
        ),
    ]

    scene = project.get("scene", {})
    metrics = {
        "object_count": len(project.get("objects", [])),
        "material_count": len(project.get("materials", [])),
        "camera_count": len(project.get("cameras", [])),
        "light_count": len(project.get("lights", [])),
        "frame_current": frame,
    }
    summary = {
        "headline": f"Blender {recipe} preview rendered for frame {frame}",
        "facts": {
            "recipe": recipe,
            "scene_name": project.get("name", "untitled"),
            "frame": frame,
            "hero_resolution": hero_settings.get("effective_resolution"),
            "workbench_resolution": alt_settings.get("effective_resolution"),
            **metrics,
        },
        "warnings": warnings,
        "next_actions": [
            "Inspect hero.png for shading, materials, and framing.",
            "Inspect workbench.png for silhouette and structural problems.",
        ],
    }

    manifest = finalize_bundle(
        bundle_dir=bundle_dir,
        bundle_id=prepared["bundle_id"],
        bundle_kind="capture",
        software="blender",
        recipe=recipe,
        source={
            "project_path": session.project_path,
            "project_name": os.path.basename(session.project_path)
            if session.project_path
            else project.get("name"),
            "project_fingerprint": source_fingerprint,
        },
        artifacts=artifacts,
        summary=summary,
        cache_key=prepared["cache_key"],
        generator={
            "entry_point": "cli-anything-blender",
            "harness_version": HARNESS_VERSION,
            "command": command
            or f"cli-anything-blender preview capture --recipe {recipe}",
        },
        status="partial" if warnings else "ok",
        warnings=warnings or None,
        context={
            "frame_range": f"{scene.get('frame_start', 1)}-{scene.get('frame_end', 250)}",
            "fps": scene.get("fps", 24),
            "primary_preset": config["primary_preset"],
            "secondary_preset": config["secondary_preset"],
        },
        metrics=metrics,
        labels=["3d", "scene", "preview"],
    )
    manifest["cached"] = False
    return manifest
