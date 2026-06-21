# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _format_status_block, _output, _output_error, _resolve_project_path  # noqa: E402,E501
from .sbox_cli_p3 import project  # noqa: E402,E501
# fmt: on


@project.command("info")
@click.pass_context
def project_info(ctx):
    """Show project info."""
    try:
        sbproj = _resolve_project_path(ctx)
        if not sbproj:
            raise click.ClickException(
                "No .sbproj found. Use --project or run from a project directory."
            )
        result = project_mod.get_project_info(sbproj)
        _output(
            ctx,
            result,
            lambda d: _format_status_block(d, f"Project: {d.get('title', '')}"),
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@project.command("config")
@click.option("--title", default=None, help="Project title")
@click.option("--max-players", type=int, default=None, help="Maximum player count")
@click.option("--tick-rate", type=int, default=None, help="Server tick rate")
@click.option("--network-type", default=None, help="Network type (e.g. Multiplayer)")
@click.option("--startup-scene", default=None, help="Startup scene path")
@click.pass_context
def project_config(ctx, title, max_players, tick_rate, network_type, startup_scene):
    """Update project settings."""
    try:
        sbproj = _resolve_project_path(ctx)
        if not sbproj:
            raise click.ClickException(
                "No .sbproj found. Use --project or run from a project directory."
            )

        kwargs = {}
        if title is not None:
            kwargs["title"] = title
        if max_players is not None:
            kwargs["max_players"] = max_players
        if tick_rate is not None:
            kwargs["tick_rate"] = tick_rate
        if network_type is not None:
            kwargs["network_type"] = network_type
        if startup_scene is not None:
            kwargs["startup_scene"] = startup_scene

        if not kwargs:
            _output_error(
                ctx, "No settings specified. Use --title, --max-players, etc."
            )
            return

        result = project_mod.configure_project(sbproj, **kwargs)
        _output(ctx, result, lambda d: _format_status_block(d, "Project updated"))
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@project.command("add-package")
@click.argument("package_ref")
@click.pass_context
def project_add_package(ctx, package_ref):
    """Add a package reference to the project."""
    try:
        sbproj = _resolve_project_path(ctx)
        if not sbproj:
            _output_error(ctx, "No project found")
            return
        result = project_mod.add_package(sbproj, package_ref)
        _output(ctx, result, lambda d: f"Added package '{package_ref}'")
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@project.command("remove-package")
@click.argument("package_ref")
@click.pass_context
def project_remove_package(ctx, package_ref):
    """Remove a package reference from the project."""
    try:
        sbproj = _resolve_project_path(ctx)
        if not sbproj:
            _output_error(ctx, "No project found")
            return
        result = project_mod.remove_package(sbproj, package_ref)
        _output(ctx, result, lambda d: f"Removed package '{package_ref}'")
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))
