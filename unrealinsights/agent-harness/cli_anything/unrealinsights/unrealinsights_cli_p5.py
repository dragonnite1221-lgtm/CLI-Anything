# ruff: noqa: F403, F405, E501
from .unrealinsights_cli_base import *  # noqa: F403
# fmt: off
from .unrealinsights_cli_p1 import _get_session, _handle_exc, _human_capture_result, _output  # noqa: E402,E501
from .unrealinsights_cli_p2 import _human_capture_status  # noqa: E402,E501
from .unrealinsights_cli_p4 import capture_group  # noqa: E402,E501
# fmt: on


@capture_group.command("run")
@click.argument("target_exe", required=False, type=click.Path(exists=False))
@click.option("--project", type=click.Path(exists=False), default=None, help="Path to a .uproject file.")
@click.option(
    "--engine-root",
    type=click.Path(exists=False),
    default=None,
    help="UE install root such as D:\\Program Files\\Epic Games\\UE_5.5 or its Engine subdir.",
)
@click.option("--target-arg", "target_args", multiple=True, help="Argument to pass to the target executable.")
@click.option("--output-trace", type=click.Path(exists=False), default=None, help="Output .utrace path.")
@click.option("--channels", default=DEFAULT_CHANNELS, show_default=True, help="Comma-separated UE trace channels.")
@click.option("--exec-cmd", "exec_cmds", multiple=True, help="Startup UE console command for -ExecCmds.")
@click.option("--wait", is_flag=True, help="Wait for the target to exit.")
@click.option("--timeout", type=float, default=None, help="Optional timeout in seconds when waiting.")
@click.pass_context
def capture_run(ctx, target_exe, project, engine_root, target_args, output_trace, channels, exec_cmds, wait, timeout):
    """Launch a target executable with UE trace flags in file mode."""
    try:
        session = _get_session(ctx)
        resolved_target_exe, resolved_target_args, launch_info = resolve_capture_target(
            target_exe,
            project=project,
            engine_root=engine_root,
            target_args=target_args,
        )
        resolved_output = normalize_trace_output_path(
            resolved_target_exe,
            output_trace=output_trace,
            current_trace=session.trace_path,
        )
        data = run_capture(
            resolved_target_exe,
            output_trace=resolved_output,
            channels=channels,
            exec_cmds=exec_cmds,
            target_args=resolved_target_args,
            wait=wait,
            timeout=timeout,
        )
        data.update(launch_info)
        session.set_trace(resolved_output)
        if wait:
            session.clear_capture()
        else:
            session.set_capture(
                pid=data.get("pid"),
                target_exe=resolved_target_exe,
                target_args=resolved_target_args,
                trace_path=resolved_output,
                channels=channels,
                project_path=launch_info.get("project_path"),
                engine_root=launch_info.get("engine_root"),
            )
        _output(ctx, data, _human_capture_result)
    except Exception as exc:
        _handle_exc(ctx, exc)
def _prepare_capture_start(ctx: click.Context, replace: bool):
    session = _get_session(ctx)
    status = capture_status(session)
    if status.get("active") and status.get("running"):
        if not replace:
            raise RuntimeError(
                "A capture session is already running. Use `capture status` to inspect it, "
                "`capture stop` to end it, or rerun `capture start` with `--replace`."
            )

        stop_result = stop_capture(session)
        if not stop_result.get("termination", {}).get("stopped"):
            raise RuntimeError("Failed to stop the existing capture session before starting a replacement.")
    elif status.get("active"):
        session.clear_capture()
@capture_group.command("start")
@click.argument("target_exe", required=False, type=click.Path(exists=False))
@click.option("--project", type=click.Path(exists=False), default=None, help="Path to a .uproject file.")
@click.option(
    "--engine-root",
    type=click.Path(exists=False),
    default=None,
    help="UE install root such as D:\\Program Files\\Epic Games\\UE_5.5 or its Engine subdir.",
)
@click.option("--target-arg", "target_args", multiple=True, help="Argument to pass to the target executable.")
@click.option("--output-trace", type=click.Path(exists=False), default=None, help="Output .utrace path.")
@click.option("--channels", default=DEFAULT_CHANNELS, show_default=True, help="Comma-separated UE trace channels.")
@click.option("--exec-cmd", "exec_cmds", multiple=True, help="Startup UE console command for -ExecCmds.")
@click.option("--replace", is_flag=True, help="Stop the currently tracked capture session before starting a new one.")
@click.pass_context
def capture_start(ctx, target_exe, project, engine_root, target_args, output_trace, channels, exec_cmds, replace):
    """Launch a traced target in the background and track the session."""
    try:
        _prepare_capture_start(ctx, replace=replace)
        ctx.invoke(
            capture_run,
            target_exe=target_exe,
            project=project,
            engine_root=engine_root,
            target_args=target_args,
            output_trace=output_trace,
            channels=channels,
            exec_cmds=exec_cmds,
            wait=False,
            timeout=None,
        )
    except Exception as exc:
        _handle_exc(ctx, exc)
@capture_group.command("status")
@click.pass_context
def capture_status_cmd(ctx):
    """Show the tracked background capture status."""
    try:
        data = capture_status(_get_session(ctx))
        _output(ctx, data, _human_capture_status)
    except Exception as exc:
        _handle_exc(ctx, exc)
