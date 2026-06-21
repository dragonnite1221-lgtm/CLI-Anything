# ruff: noqa: F403, F405, E501
from .nsight_graphics_cli_base import *  # noqa: F403

# fmt: off
from .nsight_graphics_cli_p1 import _common_kwargs, _handle_exc, _output  # noqa: E402,E501
from .nsight_graphics_cli_p2 import cli, doctor_group  # noqa: E402,E501
# fmt: on


@doctor_group.command("info")
@click.pass_context
def doctor_info(ctx):
    """Show installation details and detected capabilities."""
    try:
        data = doctor.get_installation_report(nsight_path=ctx.obj.get("nsight_path"))

        def _human(report):
            click.echo(f"Mode:     {report['compatibility_mode']}")
            click.echo(f"Version:  {report.get('version') or 'unknown'}")
            click.echo(f"Primary:  {report.get('resolved_executable') or 'not found'}")
            click.echo(
                f"Windows:  {'yes' if report.get('verified_host') else 'unverified'}"
            )
            if report.get("supported_activities"):
                click.echo("Activities:")
                for activity in report["supported_activities"]:
                    click.echo(f"  - {activity}")
            if report.get("warnings"):
                click.echo("Warnings:")
                for warning in report["warnings"]:
                    click.echo(f"  - {warning}")

        _output(ctx, data, _human)
    except Exception as exc:
        _handle_exc(ctx, exc)


@doctor_group.command("versions")
@click.pass_context
def doctor_versions(ctx):
    """List detected Nsight Graphics installations and versions."""
    try:
        data = doctor.list_installations(nsight_path=ctx.obj.get("nsight_path"))

        def _human(report):
            click.echo(f"Found: {report['count']}")
            if report.get("selected_executable"):
                click.echo(f"Selected: {report['selected_executable']}")
            for item in report.get("installations", []):
                marker = "*" if item.get("selected") else " "
                version = item.get("version") or "unknown"
                sources = "+".join(item.get("discovery_sources", []))
                click.echo(f"{marker} {version} [{item['tool_mode']}] ({sources})")
                if item.get("display_name"):
                    click.echo(f"    {item['display_name']}")
                if item.get("install_root"):
                    click.echo(f"    {item['install_root']}")
                elif item.get("registry_key"):
                    click.echo(f"    {item['registry_key']}")
                if item.get("install_source") and item.get("registered_only"):
                    click.echo(f"    source: {item['install_source']}")

        _output(ctx, data, _human)
    except Exception as exc:
        _handle_exc(ctx, exc)


@cli.group("launch")
def launch_group():
    """Launch or attach targets under Nsight Graphics."""


@launch_group.command("detached")
@click.option(
    "--activity",
    default="Graphics Capture",
    show_default=True,
    help="Nsight activity name.",
)
@click.option(
    "--exe",
    "exe_path",
    type=click.Path(exists=False),
    default=None,
    help="Target executable path.",
)
@click.option(
    "--dir",
    "working_dir",
    type=click.Path(exists=False),
    default=None,
    help="Target working directory.",
)
@click.option(
    "--arg", "program_args", multiple=True, help="Target argument. Repeat for multiple."
)
@click.option("--env", "envs", multiple=True, help="Environment entry KEY=VALUE.")
@click.pass_context
def launch_detached_cmd(ctx, activity, exe_path, working_dir, program_args, envs):
    """Launch a target under Nsight and return immediately."""
    try:
        data = launch.launch_detached(
            activity=activity,
            exe=exe_path,
            working_dir=working_dir,
            args=program_args,
            envs=envs,
            **_common_kwargs(ctx),
        )
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@launch_group.command("attach")
@click.option(
    "--activity",
    default="Graphics Capture",
    show_default=True,
    help="Nsight activity name.",
)
@click.option("--pid", type=int, required=True, help="PID to attach.")
@click.pass_context
def launch_attach_cmd(ctx, activity, pid):
    """Attach an Nsight activity to a running PID."""
    try:
        data = launch.attach(
            activity=activity,
            pid=pid,
            **_common_kwargs(ctx),
        )
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@cli.group("frame")
def frame_group():
    """Graphics capture commands."""
