# ruff: noqa: F403, F405, E501
from .godot_cli_base import *  # noqa: F403

# fmt: off
from .godot_cli_p1 import cli  # noqa: E402,E501
# fmt: on


@cli.command()
@click.pass_context
def session(ctx):
    """Start an interactive REPL session."""
    ctx.obj["repl"] = True

    try:
        from cli_anything.godot.utils.repl_skin import ReplSkin

        skin = ReplSkin("godot", version="1.0.0")
        skin.print_banner()
    except ImportError:
        skin = None
        click.secho("cli-anything-godot REPL", fg="green", bold=True)
        click.echo("Type 'help' for commands, 'exit' to quit.\n")

    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory

    prompt_session = PromptSession(history=InMemoryHistory())
    project_path = ctx.obj.get("project")
    project_name = os.path.basename(project_path) if project_path else "no-project"

    while True:
        try:
            if skin:
                prompt_text = skin.prompt(project_name=project_name, modified=False)
            else:
                prompt_text = f"godot ({project_name})> "

            line = prompt_session.prompt(prompt_text)
            line = line.strip()
            if not line:
                continue
            if line in ("exit", "quit", "q"):
                break
            if line == "help":
                click.echo(cli.get_help(click.Context(cli)))
                continue

            try:
                args = shlex.split(line)
            except ValueError as e:
                click.secho(f"Parse error: {e}", fg="red")
                continue

            try:
                cli.main(args=args, standalone_mode=False, obj=ctx.obj)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                click.secho(str(e), fg="red")

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

    if skin:
        skin.print_goodbye()
    else:
        click.echo("Goodbye.")


def main():
    cli()
