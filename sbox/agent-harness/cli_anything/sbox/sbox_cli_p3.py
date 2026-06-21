# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _format_status_block, _output, _output_error  # noqa: E402,E501
from .sbox_cli_p2 import _REPL_BANNER, _REPL_HELP, cli  # noqa: E402,E501
# fmt: on


@cli.command()
@click.pass_context
def repl(ctx):
    """Enter interactive REPL mode."""
    # Mark REPL mode so _output_error prints + returns instead of sys.exit(1).
    # Shared via obj=ctx.obj on the inner cli invocation below so child
    # commands see the same flag.
    ctx.obj["repl"] = True

    try:
        from cli_anything.sbox.utils.repl_skin import ReplSkin

        skin = ReplSkin("sbox", version="1.0.0")
    except (ImportError, TypeError):
        skin = None

    def echo(msg):
        if skin and hasattr(skin, "info"):
            skin.info(msg)
        else:
            click.echo(msg)

    def echo_error(msg):
        if skin and hasattr(skin, "error"):
            skin.error(msg)
        else:
            click.echo(f"Error: {msg}", err=True)

    echo(_REPL_BANNER)

    while True:
        try:
            line = click.prompt(
                "sbox", prompt_suffix="> ", default="", show_default=False
            )
        except (EOFError, KeyboardInterrupt):
            echo("\nBye!")
            break

        line = line.strip()
        if not line:
            continue

        if line in ("quit", "exit"):
            echo("Bye!")
            break

        if line == "help":
            echo(_REPL_HELP)
            continue

        # Parse the line and dispatch to Click
        try:
            args = shlex.split(line)
        except ValueError as exc:
            echo_error(f"Invalid input: {exc}")
            continue

        # Carry forward the global context options
        extra_args = []
        if ctx.obj.get("json"):
            extra_args.append("--json")
        project_path = ctx.obj.get("project_path")
        if project_path:
            extra_args.extend(["--project", project_path])

        try:
            cli(extra_args + args, standalone_mode=False, obj=ctx.obj)
        except SystemExit:
            # Click may raise SystemExit on --help or errors; absorb it in REPL mode
            pass
        except click.ClickException as exc:
            echo_error(exc.format_message())
        except click.Abort:
            echo_error("Command aborted.")
        except Exception as exc:
            echo_error(str(exc))


@cli.group()
@click.pass_context
def project(ctx):
    """Manage s&box projects."""
    pass


@project.command("new")
@click.option("--name", required=True, help="Project name")
@click.option(
    "--type",
    "project_type",
    type=click.Choice(["game", "addon", "library"]),
    default="game",
    help="Project type",
)
@click.option("-o", "--output-dir", default=None, help="Output directory")
@click.option("--max-players", type=int, default=64, help="Maximum player count")
@click.option("--tick-rate", type=int, default=50, help="Server tick rate")
@click.pass_context
def project_new(ctx, name, project_type, output_dir, max_players, tick_rate):
    """Create a new s&box project."""
    try:
        result = project_mod.create_project(
            name=name,
            project_type=project_type,
            output_dir=output_dir,
            max_players=max_players,
            tick_rate=tick_rate,
        )
        _output(
            ctx,
            result,
            lambda d: _format_status_block(d, f"Project '{d['name']}' created"),
        )
    except Exception as exc:
        _output_error(ctx, str(exc))
