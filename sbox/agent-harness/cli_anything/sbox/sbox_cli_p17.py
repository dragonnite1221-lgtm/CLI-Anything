# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _format_status_block, _format_table, _output, _output_error, _resolve_project_dir  # noqa: E402,E501
from .sbox_cli_p2 import _resolve_collision_config, cli  # noqa: E402,E501
from .sbox_cli_p16 import collision_group  # noqa: E402,E501
# fmt: on


@collision_group.command("remove-rule")
@click.option("--layer-a", required=True, help="First collision layer")
@click.option("--layer-b", required=True, help="Second collision layer")
@click.pass_context
def collision_remove_rule(ctx, layer_a, layer_b):
    """Remove a collision pair rule."""
    try:
        config_path = _resolve_collision_config(ctx)
        removed = collision_config_mod.remove_rule(config_path, layer_a, layer_b)
        result = {"removed": removed, "layer_a": layer_a, "layer_b": layer_b}
        _output(
            ctx,
            result,
            lambda d: (
                f"Rule {d['layer_a']}-{d['layer_b']} {'removed' if d['removed'] else 'not found'}"
            ),
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@collision_group.command("remove-layer")
@click.option("--name", required=True, help="Layer name to remove")
@click.pass_context
def collision_remove_layer(ctx, name):
    """Remove a custom collision layer."""
    try:
        config_path = _resolve_collision_config(ctx)
        removed = collision_config_mod.remove_layer(config_path, name)
        result = {"removed": removed, "layer": name}
        _output(
            ctx,
            result,
            lambda d: (
                f"Layer '{d['layer']}' {'removed' if d['removed'] else 'not found'}"
            ),
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@cli.group()
@click.pass_context
def server(ctx):
    """Manage s&box dedicated server."""
    pass


@server.command("start")
@click.option("--game", required=True, help="Game identifier (e.g. org.gamename)")
@click.option("--map", "map_ident", default=None, help="Map identifier")
@click.pass_context
def server_start(ctx, game, map_ident):
    """Launch a dedicated server."""
    try:
        proc = sbox_backend.launch_server(game, map_ident=map_ident)
        result = {"pid": proc.pid, "game": game, "map": map_ident, "status": "launched"}
        _output(
            ctx,
            result,
            lambda d: f"Server launched (PID {d['pid']}) - game: {d['game']}",
        )
    except Exception as exc:
        _output_error(ctx, str(exc))


@server.command("info")
@click.pass_context
def server_info(ctx):
    """Show server executable path and version."""
    try:
        exe = sbox_backend.find_executable("sbox-server")
        version = sbox_backend.get_sbox_version()
        # get_sbox_version is documented to return {"error": ...} on failure
        # rather than raising, so check explicitly to propagate exit code.
        if isinstance(version, dict) and version.get("error"):
            _output_error(ctx, f"Failed to read s&box version: {version['error']}")
            return
        result = {"executable": exe, "version": version}
        _output(
            ctx,
            result,
            lambda d: _format_status_block(
                {
                    "executable": d["executable"],
                    "version": d["version"].get("version", "unknown"),
                    "sbox_path": d["version"].get("sbox_path", "unknown"),
                },
                "Server Info",
            ),
        )
    except Exception as exc:
        _output_error(ctx, str(exc))


@cli.group()
@click.pass_context
def asset(ctx):
    """Manage project assets."""
    pass


@asset.command("list")
@click.option(
    "--type",
    "asset_type",
    default=None,
    help="Filter by asset type (scene, prefab, material, model, etc.)",
)
@click.pass_context
def asset_list(ctx, asset_type):
    """List project assets."""
    try:
        proj_dir = _resolve_project_dir(ctx)
        if not proj_dir:
            raise click.ClickException(
                "No project found. Use --project or run from a project directory."
            )

        assets = export_mod.list_assets(proj_dir, asset_type=asset_type)
        if ctx.obj.get("json"):
            _output(ctx, assets)
        else:
            if not assets:
                click.echo("No assets found.")
                return
            rows = []
            for a in assets:
                size_kb = a["size_bytes"] / 1024
                rows.append(
                    {
                        "name": a["name"],
                        "type": a["type"],
                        "path": a["path"],
                        "size": f"{size_kb:.1f} KB",
                    }
                )
            click.echo(_format_table(rows, ["name", "type", "path", "size"]))
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))
