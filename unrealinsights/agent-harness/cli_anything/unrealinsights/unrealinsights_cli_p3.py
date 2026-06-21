# ruff: noqa: F403, F405, E501
from .unrealinsights_cli_base import *  # noqa: F403
# fmt: off
from .unrealinsights_cli_p1 import _get_session, _handle_exc, _human_backend, _output, _repl_mode, _resolve_insights, _resolve_trace_server  # noqa: E402,E501
# fmt: on


@click.group(invoke_without_command=True)
@click.option("--json", "json_mode", is_flag=True, help="Output in JSON format.")
@click.option("--debug", is_flag=True, help="Show debug tracebacks on errors.")
@click.option(
    "--trace",
    "-t",
    type=click.Path(exists=False),
    envvar="UNREALINSIGHTS_TRACE",
    help="Path to the active .utrace file.",
)
@click.option(
    "--insights-exe",
    type=click.Path(exists=False),
    envvar="UNREALINSIGHTS_EXE",
    help="Explicit path to UnrealInsights.exe.",
)
@click.option(
    "--trace-server-exe",
    type=click.Path(exists=False),
    envvar="UNREAL_TRACE_SERVER_EXE",
    help="Explicit path to UnrealTraceServer.exe.",
)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, json_mode, debug, trace, insights_exe, trace_server_exe):
    """Windows-first Unreal Insights harness with REPL and exporter wrappers."""
    ctx.ensure_object(dict)
    session = _get_session(ctx)
    ctx.obj["json_mode"] = json_mode
    ctx.obj["debug"] = debug

    if trace is not None:
        session.set_trace(trace)
    if insights_exe is not None:
        session.set_insights_exe(insights_exe)
    if trace_server_exe is not None:
        session.set_trace_server_exe(trace_server_exe)

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)
@cli.command()
@click.pass_context
def repl(ctx):
    """Start the interactive REPL."""
    from cli_anything.unrealinsights.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    session = _get_session(ctx)
    skin = ReplSkin("unrealinsights", version=__version__, history_file=str(state_dir() / "history"))
    skin.print_banner()
    pt_session = skin.create_prompt_session()

    repl_commands = {
        "backend": "info|ensure-insights",
        "trace": "set|info",
        "store": "info|list|latest",
        "capture": "run|start|status|stop|snapshot",
        "live": "processes|exec|trace-status|bookmark|screenshot|snapshot|stop-trace",
        "gui": "status|open|open-latest",
        "export": "threads|timers|timing-events|timer-stats|timer-callees|counters|counter-values",
        "batch": "run-rsp",
        "analyze": "summary",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    try:
        while True:
            try:
                trace_name = Path(session.trace_path).name if session.trace_path else ""
                line = skin.get_input(pt_session, project_name=trace_name, modified=False)
                if not line:
                    continue
                if line.lower() in ("quit", "exit", "q"):
                    skin.print_goodbye()
                    break
                if line.lower() == "help":
                    skin.help(repl_commands)
                    continue

                args = shlex.split(line, posix=os.name != "nt")
                if ctx.obj.get("json_mode"):
                    args = ["--json", *args]
                if ctx.obj.get("debug"):
                    args = ["--debug", *args]
                try:
                    cli.main(args, standalone_mode=False, obj=ctx.obj)
                except SystemExit:
                    pass
                except click.exceptions.UsageError as exc:
                    skin.warning(f"Usage error: {exc}")
                except Exception as exc:
                    if ctx.obj.get("json_mode"):
                        output_json({"error": str(exc)})
                    else:
                        skin.error(str(exc))
            except (EOFError, KeyboardInterrupt):
                skin.print_goodbye()
                break
    finally:
        _repl_mode = False
@cli.group("backend")
def backend_group():
    """Backend executable discovery and inspection."""
@backend_group.command("info")
@click.pass_context
def backend_info(ctx):
    """Resolve Unreal Insights backend executables."""
    try:
        data = {
            "insights": _resolve_insights(ctx),
            "trace_server": _resolve_trace_server(ctx),
        }
        _output(ctx, data, _human_backend)
    except Exception as exc:
        _handle_exc(ctx, exc)
