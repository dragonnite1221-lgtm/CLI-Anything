# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session, output  # noqa: E402,E501
from .freecad_cli_p2 import cli, handle_error, output_fn  # noqa: E402,E501
# fmt: on


@cli.command("repl")
@click.argument("project_path", required=False, type=click.Path())
@handle_error
def repl(project_path: Optional[str]) -> None:
    """Start interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.freecad.utils.repl_skin import ReplSkin

    skin = ReplSkin("freecad", version="1.0.0")
    skin.print_banner()

    sess = get_session()
    if project_path and sess.project is None:
        proj = doc_mod.open_document(project_path)
        sess.set_project(proj, path=project_path)

    _repl_commands = {
        "document": "new|open|save|info|profiles",
        "part": "add|remove|list|get|transform|boolean|copy|mirror|scale|offset|thickness|compound|explode|fillet-3d|chamfer-3d|loft|sweep|revolve|extrude|section|slice|line-3d|wire|polygon-3d|info|bounds|align",
        "sketch": "new|add-line|add-circle|add-rect|add-arc|constrain|close|list|get|add-point|add-ellipse|add-polygon|add-bspline|add-slot|edit-element|remove-element|remove-constraint|edit-constraint|mirror|offset|trim|extend|validate|solve-status|set-construction|project-external|intersection|add-external-face",
        "body": "new|pad|pocket|fillet|chamfer|revolution|list|get|groove|additive-loft|additive-pipe|additive-helix|subtractive-loft|subtractive-pipe|subtractive-helix|additive-box|additive-cylinder|additive-sphere|additive-cone|additive-torus|additive-wedge|subtractive-box|subtractive-cylinder|subtractive-sphere|subtractive-cone|subtractive-torus|subtractive-wedge|draft-feature|thickness-feature|hole|linear-pattern|polar-pattern|mirrored|multi-transform|datum-plane|datum-line|datum-point|shape-binder|local-coordinate-system|toggle-freeze",
        "material": "create|assign|list|get|set|presets|import-material|export-material",
        "export": "render|info|presets",
        "preview": "recipes|capture|latest|live",
        "motion": "new|list|get|delete|keyframe|sample|render-frames|render-video",
        "session": "undo|redo|status|history",
        "measure": "distance|length|angle|area|volume|radius|diameter|position|center-of-mass|bounding-box|inertia|check-geometry",
        "spreadsheet": "new|set-cell|get-cell|set-alias|import-csv|export-csv|list",
        "mesh": "import|from-shape|export|info|analyze|check|boolean|decimate|remesh|smooth|repair|fill-holes|flip-normals|merge|split|to-shape",
        "draft": "wire|rectangle|circle|ellipse|polygon|bspline|bezier|point|text|shapestring|dimension|label|hatch|move|rotate|scale|mirror|offset|array-linear|array-polar|array-path|copy|clone|upgrade|downgrade|trim|join|extrude|fillet-2d|to-sketch|list|get|remove",
        "surface": "filling|sections|extend|blend-curve|sew|cut",
        "import": "auto|step|iges|stl|obj|dxf|svg|brep|3mf|ply|off|gltf|info",
        "assembly": "new|add-part|remove-part|list|get|constrain|solve|dof|bom|explode|collapse|insert-part|create-simulation|add-sim-step",
        "techdraw": "new-page|set-template|add-view|add-projection-group|add-section-view|add-detail-view|add-dimension|add-annotation|add-leader|add-centerline|add-hatch|export-pdf|export-svg|list-views|get-view",
        "fem": "new-analysis|add-fixed|add-force|add-pressure|add-displacement|add-temperature|add-heatflux|set-material|mesh-generate|solve|results|export-results|add-beam-section|add-tie|purge-results|suppress",
        "cam": "new-job|set-stock|add-profile|add-pocket|add-drilling|add-facing|set-tool|generate-gcode|simulate|export-gcode|add-tapping|import-tool-library|export-tool-library",
    }

    pt_session = skin.create_prompt_session()

    while True:
        try:
            proj_name = ""
            modified = False
            if sess.project:
                proj_name = sess.project.get("name", "untitled")
                modified = sess._modified

            line = skin.get_input(pt_session, project_name=proj_name, modified=modified)

            if not line:
                continue

            if line.lower() in ("quit", "exit", "q"):
                if sess._modified:
                    skin.warning(
                        "Unsaved changes! Use 'document save' first, "
                        "or type 'quit' again."
                    )
                    sess._modified = False  # Allow second quit
                else:
                    skin.print_goodbye()
                    break

            if line.lower() == "help":
                skin.help(_repl_commands)
                continue

            args = line.split()
            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.error(str(e))

        except (KeyboardInterrupt, EOFError):
            skin.print_goodbye()
            break


@cli.group("document")
def document_group():
    """Document management commands."""
    pass


@document_group.command("new")
@click.option("--name", "-n", default="Untitled", help="Document name.")
@click.option("--units", "-u", default="mm", help="Units (mm, m, in).")
@click.option("--profile", help="Use a preset profile.")
@click.option("--output", "-o", type=click.Path(), help="Save to file.")
@handle_error
def document_new(
    name: str, units: str, profile: Optional[str], output: Optional[str]
) -> None:
    """Create a new FreeCAD document."""
    sess = get_session()
    proj = doc_mod.create_document(name=name, units=units, profile=profile)
    path = None
    if output:
        path = doc_mod.save_document(proj, output)
    sess.set_project(proj, path=path)
    result = doc_mod.get_document_info(proj)
    if path:
        result["saved_to"] = path
    output_fn(result, f"Created document: {name}")
