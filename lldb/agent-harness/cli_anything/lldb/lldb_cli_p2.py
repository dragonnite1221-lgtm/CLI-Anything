# ruff: noqa: F403, F405, E501
from .lldb_cli_base import *  # noqa: F403

# fmt: off
from .lldb_cli_p1 import _get_session, _handle_exc, _output, _require_target, _session_status, _shutdown_session, cli  # noqa: E402,E501
# fmt: on


@cli.command()
@click.pass_context
def repl(ctx):
    """Start interactive REPL session."""
    from cli_anything.lldb.utils.repl_skin import ReplSkin

    skin = ReplSkin("lldb", version="1.0.0")
    skin.print_banner()
    pt_session = skin.create_prompt_session()

    repl_commands = {
        "target": "create|info",
        "process": "launch|attach|continue|interrupt|detach|info",
        "breakpoint": "set|list|delete|enable|disable",
        "thread": "list|select|backtrace|info",
        "frame": "select|info|locals",
        "step": "over|into|out",
        "expr": "<expression>",
        "memory": "read|find",
        "core": "load",
        "dap": "Run Debug Adapter Protocol server",
        "session": "info|close",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    try:
        while True:
            try:
                context = ""
                if _session is not None:
                    status = _session_status(_session)
                    if status.get("has_process"):
                        context = status.get("process_origin") or "active"
                    elif status.get("has_target"):
                        context = "target"
                line = skin.get_input(pt_session, project_name=context, modified=False)
                if not line:
                    continue
                if line.lower() in ("quit", "exit", "q"):
                    skin.print_goodbye()
                    break
                if line.lower() == "help":
                    skin.help(repl_commands)
                    continue
                args = shlex.split(line, posix=os.name != "nt")
                if ctx.obj.get("session_file"):
                    args = ["--session-file", ctx.obj["session_file"], *args]
                if ctx.obj.get("json_mode"):
                    args = ["--json", *args]
                if ctx.obj.get("debug"):
                    args = ["--debug", *args]
                try:
                    command_obj = dict(ctx.obj)
                    command_obj["close_session_on_exit"] = False
                    cli.main(args, standalone_mode=False, obj=command_obj)
                except SystemExit:
                    pass
                except click.exceptions.UsageError as exc:
                    skin.warning(f"Usage error: {exc}")
                except Exception as exc:
                    if ctx.obj.get("json_mode"):
                        click.echo(json.dumps({"error": str(exc)}, indent=2))
                    else:
                        skin.error(str(exc))
            except (EOFError, KeyboardInterrupt):
                skin.print_goodbye()
                break
    finally:
        _shutdown_session()


@cli.result_callback()
@click.pass_context
def _cleanup(ctx, _result, **_kwargs):
    if ctx.obj.get("close_session_on_exit"):
        _shutdown_session()


@cli.group("target")
def target_group():
    """Target management."""


@target_group.command("create")
@click.option("--exe", "exe_path", required=True, type=click.Path(exists=False))
@click.option("--arch", type=str, default=None, help="Target architecture (optional).")
@click.pass_context
def target_create(ctx, exe_path: str, arch: Optional[str]):
    """Create debug target."""
    try:
        data = _get_session().target_create(exe_path, arch=arch)
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@target_group.command("info")
@click.pass_context
def target_info(ctx):
    """Show target info."""
    try:
        data = _require_target().target_info()
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@cli.group("process")
def process_group():
    """Process management."""


@process_group.command("launch")
@click.option(
    "--arg", "args", multiple=True, help="Launch argument. Repeat for multiple."
)
@click.option("--env", "envs", multiple=True, help="Environment entry KEY=VALUE.")
@click.option("--cwd", "working_dir", type=click.Path(exists=True), default=None)
@click.option(
    "--stop-at-entry",
    is_flag=True,
    help="Stop at the process entry point before user code.",
)
@click.pass_context
def process_launch(ctx, args, envs, working_dir, stop_at_entry):
    """Launch process for current target."""
    try:
        data = _require_target().launch(
            args=list(args) or None,
            env=list(envs) or None,
            working_dir=working_dir,
            stop_at_entry=stop_at_entry,
        )
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)
