# ruff: noqa: F403, F405, E501
from .nsight_graphics_cli_base import *  # noqa: F403


@click.group(invoke_without_command=True)
@click.option("--json", "json_mode", is_flag=True, help="Output in JSON format.")
@click.option("--debug", is_flag=True, help="Show debug tracebacks on errors.")
@click.option(
    "--nsight-path",
    type=click.Path(exists=False),
    default=None,
    help="Explicit Nsight Graphics install dir or executable.",
)
@click.option(
    "--project",
    type=click.Path(exists=False),
    default=None,
    help="Nsight Graphics project file.",
)
@click.option(
    "--output-dir",
    type=click.Path(exists=False),
    default=None,
    help="Output directory for captures or exports.",
)
@click.option("--hostname", default=None, help="Remote host name.")
@click.option(
    "--platform", "platform_name", default=None, help="Target platform string."
)
@click.version_option(package_name="cli-anything-nsight-graphics")
@click.pass_context
def cli(
    ctx, json_mode, debug, nsight_path, project, output_dir, hostname, platform_name
):
    """Nsight Graphics CLI - orchestration wrapper for official tools."""
    ctx.ensure_object(dict)
    ctx.obj["json_mode"] = json_mode
    ctx.obj["debug"] = debug
    if nsight_path is not None:
        ctx.obj["nsight_path"] = nsight_path
    if project is not None:
        ctx.obj["project"] = project
    if output_dir is not None:
        ctx.obj["output_dir"] = output_dir
    if hostname is not None:
        ctx.obj["hostname"] = hostname
    if platform_name is not None:
        ctx.obj["platform_name"] = platform_name
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.command()
@click.pass_context
def repl(ctx):
    """Start the interactive REPL."""
    from cli_anything.nsight_graphics.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("nsight-graphics", version="0.1.0")
    skin.print_banner()
    session = skin.create_prompt_session()

    commands = {
        "doctor": "info|versions",
        "launch": "detached|attach",
        "frame": "capture",
        "gpu-trace": "capture|summarize",
        "replay": "analyze",
        "cpp": "capture",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    try:
        while True:
            try:
                context = (
                    os.path.basename(ctx.obj.get("project", ""))
                    if ctx.obj.get("project")
                    else ""
                )
                line = skin.get_input(session, project_name=context, modified=False)
                if not line:
                    continue
                if line.lower() in ("quit", "exit", "q"):
                    skin.print_goodbye()
                    break
                if line.lower() == "help":
                    skin.help(commands)
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
                        click.echo(json.dumps({"error": str(exc)}, indent=2))
                    else:
                        skin.error(str(exc))
            except (EOFError, KeyboardInterrupt):
                skin.print_goodbye()
                break
    finally:
        _repl_mode = False


@cli.group("doctor")
def doctor_group():
    """Installation and environment diagnostics."""
