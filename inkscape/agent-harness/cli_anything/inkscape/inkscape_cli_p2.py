# ruff: noqa: F403, F405, E501
from .inkscape_cli_base import *  # noqa: F403

# fmt: off
from .inkscape_cli_p1 import _auto_save_callback, _load_or_seed_project, _repl_help, get_session, handle_error, output  # noqa: E402,E501
# fmt: on


@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.option(
    "--project",
    "project_path",
    type=str,
    default=None,
    help="Path to .inkscape-cli.json project file",
)
@click.option(
    "-s",
    "--save",
    "auto_save",
    is_flag=True,
    help="Auto-save project after each mutation command (one-shot mode)",
)
@click.option(
    "--dry-run",
    "dry_run",
    is_flag=True,
    default=False,
    help="Run command without saving changes to disk",
)
@click.pass_context
def cli(ctx, use_json, project_path, auto_save, dry_run):
    """Inkscape CLI — Stateful vector graphics editing from the command line.

    Run without a subcommand to enter interactive REPL mode.

    Use -s/--save to automatically save changes after each mutation command.
    This is useful in one-shot mode where each command runs in a new process.
    """
    global _json_output, _auto_save, _dry_run
    _json_output = use_json
    _auto_save = auto_save
    _dry_run = dry_run

    if project_path:
        _load_or_seed_project(project_path)

    # Register auto-save callback to run after each command
    ctx.call_on_close(_auto_save_callback)

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl, project_path=None)


@cli.command()
@click.option("--project", "project_path", type=str, default=None)
@handle_error
def repl(project_path):
    """Start interactive REPL session."""
    from cli_anything.inkscape.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("inkscape", version="1.0.0")

    if project_path:
        _load_or_seed_project(project_path)

    skin.print_banner()

    pt_session = skin.create_prompt_session()

    # Determine the current project name for the prompt
    def _current_project_name():
        try:
            s = get_session()
            if s.has_project():
                return s.project_path or "untitled"
        except Exception:
            pass
        return ""

    while True:
        try:
            project_name = _current_project_name()
            line = skin.get_input(
                pt_session, project_name=project_name, modified=False
            ).strip()
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                _repl_help(skin)
                continue

            try:
                args = shlex.split(line)
            except ValueError:
                args = line.split()
            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.error(f"Usage error: {e}")
            except Exception as e:
                skin.error(f"{e}")

        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


@cli.group()
def document():
    """Document management commands."""
    pass


@document.command("new")
@click.option("--width", "-w", type=float, default=1920, help="Canvas width")
@click.option("--height", "-h", type=float, default=1080, help="Canvas height")
@click.option(
    "--units",
    "-u",
    type=click.Choice(["px", "mm", "cm", "in", "pt", "pc"]),
    default="px",
)
@click.option("--background", "-bg", default="#ffffff", help="Background color")
@click.option("--name", "-n", default="untitled", help="Document name")
@click.option("--profile", "-p", type=str, default=None, help="Document profile")
@click.option("--output", "-o", type=str, default=None, help="Save path")
@handle_error
def document_new(width, height, units, background, name, profile, output):
    """Create a new document."""
    proj = doc_mod.create_document(
        width=width,
        height=height,
        units=units,
        background=background,
        name=name,
        profile=profile,
    )
    sess = get_session()
    sess.set_project(proj, output)
    if output:
        doc_mod.save_document(proj, output)
    output_data = doc_mod.get_document_info(proj)
    globals()["output"](output_data, f"Created document: {name}")


@document.command("open")
@click.argument("path")
@handle_error
def document_open(path):
    """Open an existing project."""
    proj = doc_mod.open_document(path)
    sess = get_session()
    sess.set_project(proj, path)
    info = doc_mod.get_document_info(proj)
    output(info, f"Opened: {path}")
