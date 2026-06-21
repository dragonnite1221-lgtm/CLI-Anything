# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _format_status_block, _output, _output_error, _resolve_project_dir  # noqa: E402,E501
from .sbox_cli_p2 import cli  # noqa: E402,E501
from .sbox_cli_p19 import material  # noqa: E402,E501
# fmt: on


@material.command("set")
@click.argument("material_path")
@click.option("--shader", default=None, help="New shader")
@click.option("--color-texture", default=None, help="New color texture path")
@click.option("--normal-texture", default=None, help="New normal texture path")
@click.option("--metalness", type=float, default=None, help="New metalness (0-1)")
@click.option("--tint", default=None, help="New tint (r g b a)")
@click.pass_context
def material_set(
    ctx, material_path, shader, color_texture, normal_texture, metalness, tint
):
    """Update properties of an existing material."""
    try:
        result = material_mod.update_material(
            material_path,
            shader=shader,
            color_texture=color_texture,
            normal_texture=normal_texture,
            metalness=metalness,
            tint=tint,
        )
        _output(ctx, result, lambda d: f"Material '{d['name']}' updated")
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@cli.group()
@click.pass_context
def sound(ctx):
    """Manage s&box sound events."""
    pass


@sound.command("list")
@click.pass_context
def sound_list(ctx):
    """List sound events in the project."""
    try:
        project_dir = _resolve_project_dir(ctx)
        if not project_dir:
            _output_error(ctx, "No project found")
            return
        from cli_anything.sbox.core import export as export_mod_local

        assets = export_mod_local.list_assets(project_dir, asset_type="sound")
        _output(ctx, assets)
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@sound.command("new")
@click.option("--name", required=True, help="Sound event name")
@click.option("--sounds", default=None, help="Comma-separated .vsnd paths")
@click.option("--volume", default="1", help="Volume (0-1)")
@click.option("--pitch", default="1", help="Pitch multiplier")
@click.option("--decibels", type=int, default=70, help="Loudness in dB")
@click.option("--ui/--no-ui", default=False, help="UI sound (no spatialization)")
@click.option(
    "-o", "--output", "output_path", default=None, help="Output .sound file path"
)
@click.pass_context
def sound_new(ctx, name, sounds, volume, pitch, decibels, ui, output_path):
    """Create a new sound event."""
    try:
        sound_list = [s.strip() for s in sounds.split(",")] if sounds else []
        result = sound_mod.create_sound_event(
            name,
            sounds=sound_list,
            volume=volume,
            pitch=pitch,
            decibels=decibels,
            is_ui=ui,
            output_path=output_path,
        )
        _output(
            ctx,
            result,
            lambda d: (
                f"Sound '{d['name']}' created"
                + (f" at {d.get('path', '')}" if d.get("path") else "")
            ),
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@sound.command("info")
@click.argument("sound_path")
@click.pass_context
def sound_info(ctx, sound_path):
    """Show sound event details."""
    try:
        result = sound_mod.parse_sound_event(sound_path)
        _output(ctx, result, lambda d: _format_status_block(d, f"Sound: {d['name']}"))
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@sound.command("set")
@click.argument("sound_path")
@click.option(
    "--sounds", default=None, help="Comma-separated .vsnd paths (replaces all)"
)
@click.option("--volume", default=None, help="Volume (0-1)")
@click.option("--pitch", default=None, help="Pitch multiplier")
@click.option("--decibels", type=int, default=None, help="Loudness in dB")
@click.option(
    "--is-ui/--no-is-ui",
    "is_ui",
    default=None,
    help="Mark sound as UI (skips occlusion/positional audio)",
)
@click.option(
    "--occlusion/--no-occlusion",
    "occlusion",
    default=None,
    help="Enable occlusion calculations",
)
@click.pass_context
def sound_set(ctx, sound_path, sounds, volume, pitch, decibels, is_ui, occlusion):
    """Update properties of an existing sound event."""
    try:
        sound_list_parsed = (
            [s.strip() for s in sounds.split(",")] if sounds is not None else None
        )
        result = sound_mod.update_sound_event(
            sound_path,
            sounds=sound_list_parsed,
            volume=volume,
            pitch=pitch,
            decibels=decibels,
            is_ui=is_ui,
            occlusion=occlusion,
        )
        _output(ctx, result, lambda d: f"Sound '{d['name']}' updated")
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@cli.group()
@click.pass_context
def localization(ctx):
    """Manage translation files."""
    pass
