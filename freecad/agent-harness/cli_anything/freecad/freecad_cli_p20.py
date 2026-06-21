# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p19 import material_group  # noqa: E402,E501
# fmt: on


@material_group.command("export-material")
@click.argument("index", type=int)
@click.argument("path", type=click.Path())
@handle_error
def material_export(index: int, path: str) -> None:
    """Export a material to a JSON file."""
    sess = get_session()
    proj = sess.get_project()
    result = mat_mod.export_material(proj, index, path)
    output_fn(result, f"Exported: {result.get('path', path)}")


@cli.group("export")
def export_group():
    """Export and rendering commands."""
    pass


@export_group.command("render")
@click.argument("output_path", type=click.Path())
@click.option("--preset", "-p", default="step", help="Export preset.")
@click.option("--overwrite", is_flag=True, help="Overwrite existing file.")
@handle_error
def export_render(output_path: str, preset: str, overwrite: bool) -> None:
    """Export/render the project to a file."""
    sess = get_session()
    proj = sess.get_project()
    result = export_mod.export_project(
        proj, output_path, preset=preset, overwrite=overwrite
    )
    output_fn(result, f"Exported: {result.get('output', output_path)}")


@export_group.command("info")
@handle_error
def export_info() -> None:
    """Show export information for the current project."""
    sess = get_session()
    proj = sess.get_project()
    result = export_mod.get_export_info(proj)
    output_fn(result, "Export info:")


@export_group.command("presets")
@handle_error
def export_presets() -> None:
    """List available export presets."""
    result = export_mod.list_presets()
    output_fn(result, "Export presets:")


@cli.group("preview")
def preview_group():
    """Preview bundle capture and inspection."""
    pass


@preview_group.group("live")
def preview_live_group():
    """Live preview session commands."""
    pass


@preview_group.command("recipes")
@handle_error
def preview_recipes() -> None:
    """List available preview recipes."""
    result = preview_mod.list_recipes()
    output_fn(result, "Preview recipes:")


@preview_group.command("capture")
@click.option("--recipe", default="quick", help="Preview recipe name.")
@click.option("--force", is_flag=True, help="Bypass preview cache.")
@click.option(
    "--root-dir", default=None, help="Override preview bundle root directory."
)
@handle_error
def preview_capture(recipe: str, force: bool, root_dir: Optional[str]) -> None:
    """Capture a preview bundle for the active project."""
    sess = get_session()
    result = preview_mod.capture(
        sess,
        recipe=recipe,
        force=force,
        root_dir=root_dir,
        command=f"cli-anything-freecad --project {sess.project_path or ''} preview capture --recipe {recipe}".strip(),
    )
    bundle_dir = result.get("_bundle_dir", result.get("bundle_dir", ""))
    status = (
        "Reused preview bundle" if result.get("cached") else "Created preview bundle"
    )
    output_fn(result, f"{status}: {bundle_dir}")


@preview_group.command("latest")
@click.option("--recipe", default=None, help="Filter by recipe name.")
@click.option(
    "--root-dir", default=None, help="Override preview bundle root directory."
)
@handle_error
def preview_latest(recipe: Optional[str], root_dir: Optional[str]) -> None:
    """Show the latest preview bundle manifest."""
    sess = get_session()
    result = preview_mod.latest(
        project_path=sess.project_path, recipe=recipe, root_dir=root_dir
    )
    output_fn(result, f"Latest preview bundle: {result.get('_bundle_dir', '')}")
