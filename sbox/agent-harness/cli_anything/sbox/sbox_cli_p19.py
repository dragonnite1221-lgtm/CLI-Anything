# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _format_status_block, _output, _output_error, _resolve_project_dir  # noqa: E402,E501
from .sbox_cli_p2 import cli  # noqa: E402,E501
from .sbox_cli_p17 import asset  # noqa: E402,E501
# fmt: on


@asset.command("rename")
@click.argument("old_path")
@click.argument("new_name")
@click.option(
    "--dry-run", is_flag=True, help="Report what would change without touching files"
)
@click.pass_context
def asset_rename(ctx, old_path, new_name, dry_run):
    """Rename an asset (in same directory) and update every reference in scenes/prefabs."""
    try:
        proj_dir = _resolve_project_dir(ctx)
        if not proj_dir:
            _output_error(ctx, "No project found")
            return
        result = export_mod.rename_asset(proj_dir, old_path, new_name, dry_run=dry_run)

        def human(d):
            if d.get("dry_run"):
                return f"[dry-run] Would rename {d['old_path']} -> {d['new_path']} and update {d['references_would_update']} reference(s)"
            n = sum(r["replacements"] for r in d["references_updated"])
            return f"Renamed {d['old_path']} -> {d['new_path']}, updated {n} reference(s) in {len(d['references_updated'])} file(s)"

        _output(ctx, result, human)
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@asset.command("move")
@click.argument("old_path")
@click.argument("new_path")
@click.option(
    "--dry-run", is_flag=True, help="Report what would change without touching files"
)
@click.pass_context
def asset_move(ctx, old_path, new_path, dry_run):
    """Move an asset to a new path (different directory) and update every reference."""
    try:
        proj_dir = _resolve_project_dir(ctx)
        if not proj_dir:
            _output_error(ctx, "No project found")
            return
        result = export_mod.move_asset(proj_dir, old_path, new_path, dry_run=dry_run)

        def human(d):
            if d.get("dry_run"):
                return f"[dry-run] Would move {d['old_path']} -> {d['new_path']} and update {d['references_would_update']} reference(s)"
            n = sum(r["replacements"] for r in d["references_updated"])
            return f"Moved {d['old_path']} -> {d['new_path']}, updated {n} reference(s) in {len(d['references_updated'])} file(s)"

        _output(ctx, result, human)
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@cli.group()
@click.pass_context
def material(ctx):
    """Manage s&box materials."""
    pass


@material.command("new")
@click.option("--name", required=True, help="Material name")
@click.option(
    "--shader", default="complex", help="Shader (complex, simple, unlit, glass)"
)
@click.option("--color-texture", default=None, help="Color/albedo texture path")
@click.option("--normal-texture", default=None, help="Normal map texture path")
@click.option("--roughness-texture", default=None, help="Roughness texture path")
@click.option("--metalness", type=float, default=0.0, help="Metalness (0-1)")
@click.option("--tint", default="1 1 1 0", help="Color tint (r g b a)")
@click.option(
    "-o", "--output", "output_path", default=None, help="Output .vmat file path"
)
@click.pass_context
def material_new(
    ctx,
    name,
    shader,
    color_texture,
    normal_texture,
    roughness_texture,
    metalness,
    tint,
    output_path,
):
    """Create a new material."""
    try:
        result = material_mod.create_material(
            name,
            shader=shader,
            color_texture=color_texture,
            normal_texture=normal_texture,
            roughness_texture=roughness_texture,
            metalness=metalness,
            tint=tint,
            output_path=output_path,
        )
        _output(
            ctx,
            result,
            lambda d: (
                f"Material '{d['name']}' created"
                + (f" at {d.get('path', 'stdout')}" if d.get("path") else "")
            ),
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@material.command("info")
@click.argument("material_path")
@click.pass_context
def material_info(ctx, material_path):
    """Show material properties."""
    try:
        result = material_mod.parse_material(material_path)
        _output(
            ctx, result, lambda d: _format_status_block(d, f"Material: {d['name']}")
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@material.command("list")
@click.pass_context
def material_list(ctx):
    """List materials in the project."""
    try:
        project_dir = _resolve_project_dir(ctx)
        if not project_dir:
            _output_error(ctx, "No project found")
            return
        result = material_mod.list_materials(project_dir)
        _output(ctx, result)
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))
