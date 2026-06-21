# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403

# fmt: off
from .preview_p1 import _project_fingerprint  # noqa: E402,E501
from .preview_p2 import _generate_preview_macro  # noqa: E402,E501
# fmt: on


def capture(
    session: Session,
    recipe: str = "quick",
    *,
    root_dir: Optional[str] = None,
    force: bool = False,
    command: Optional[str] = None,
) -> Dict[str, Any]:
    """Render a preview bundle for the active FreeCAD project."""
    if session.project is None:
        raise RuntimeError("No project is currently loaded.")
    if recipe not in RECIPES:
        raise ValueError(
            f"Unknown preview recipe: {recipe!r}. Available: {', '.join(sorted(RECIPES))}"
        )

    project = session.get_project()
    config = RECIPES[recipe]
    source_fingerprint = _project_fingerprint(session)
    prepared = prepare_bundle(
        software="freecad",
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

    bundle_dir = prepared["bundle_dir"]
    artifacts_dir = prepared["artifacts_dir"]
    outputs: List[Dict[str, str]] = []
    for artifact_id, method_name, label in config["views"]:
        filename = f"{artifact_id}.png"
        outputs.append(
            {
                "artifact_id": artifact_id,
                "method": method_name,
                "label": label,
                "path": os.path.join(artifacts_dir, filename),
            }
        )

    warnings: List[str] = []
    if not project.get("parts") and not project.get("bodies"):
        warnings.append("Project has no parts or bodies; preview may be empty.")

    macro_content = _generate_preview_macro(
        project,
        outputs,
        width=config["width"],
        height=config["height"],
        background=config["background"],
    )
    result = freecad_backend.run_macro_content(
        macro_content,
        timeout=240,
        gui_required=True,
        env={"QT_QPA_PLATFORM": "offscreen"},
    )
    if result["returncode"] != 0:
        raise RuntimeError(
            f"FreeCAD preview failed (exit code {result['returncode']}): {result['stderr']}"
        )

    artifacts = []
    for output in outputs:
        if not os.path.isfile(output["path"]):
            warnings.append(
                f"missing preview image: {os.path.basename(output['path'])}"
            )
            continue
        artifacts.append(
            artifact_record(
                bundle_dir,
                output["path"],
                artifact_id=output["artifact_id"],
                role="hero" if output["artifact_id"] == "hero" else "gallery",
                kind="image",
                label=output["label"],
                width=config["width"],
                height=config["height"],
                view_method=output["method"],
            )
        )

    metrics = {
        "parts_count": len(project.get("parts", [])),
        "bodies_count": len(project.get("bodies", [])),
        "sketches_count": len(project.get("sketches", [])),
        "materials_count": len(project.get("materials", [])),
        "assemblies_count": len(project.get("assemblies", [])),
    }
    summary = {
        "headline": f"FreeCAD {recipe} preview rendered with {len(artifacts)} views",
        "facts": {
            "recipe": recipe,
            "units": project.get("units", "mm"),
            "resolution": f"{config['width']}x{config['height']}",
            **metrics,
        },
        "warnings": warnings,
        "next_actions": [
            "Inspect the isometric hero image for overall form and placement.",
            "Inspect front/top/right views for dimensional and alignment issues.",
        ],
    }

    manifest = finalize_bundle(
        bundle_dir=bundle_dir,
        bundle_id=prepared["bundle_id"],
        bundle_kind="capture",
        software="freecad",
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
            "entry_point": "cli-anything-freecad",
            "harness_version": HARNESS_VERSION,
            "command": command
            or f"cli-anything-freecad preview capture --recipe {recipe}",
        },
        status="partial" if warnings else "ok",
        warnings=warnings or None,
        context={"views": [item[0] for item in config["views"]]},
        metrics=metrics,
        labels=["cad", "3d", "preview"],
    )
    manifest["cached"] = False
    return manifest
