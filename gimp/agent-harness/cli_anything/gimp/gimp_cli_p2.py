# ruff: noqa: F403, F405, E501
from .gimp_cli_base import *  # noqa: F403

# fmt: off
from .gimp_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.command()
@click.option("--project", "project_path", type=str, default=None)
@handle_error
def repl(project_path):
    """Start interactive REPL session."""
    from cli_anything.gimp.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("gimp", version="1.0.0")

    if project_path:
        sess = get_session()
        proj = proj_mod.open_project(project_path)
        sess.set_project(proj, project_path)

    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "project": "new|open|save|info|profiles|json",
        "layer": "new|add-from-file|list|remove|duplicate|move|set|flatten|merge-down",
        "canvas": "info|resize|scale|crop|mode|dpi",
        "filter": "list-available|info|add|remove|set|list",
        "media": "probe|list|check|histogram",
        "export": "presets|preset-info|render",
        "draw": "text|rect",
        "session": "status|undo|redo|history",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    while True:
        try:
            # Determine project name for prompt
            try:
                sess = get_session()
                proj_name = ""
                if sess.has_project():
                    p = sess.get_project()
                    proj_name = p.get("name", "") if isinstance(p, dict) else ""
            except Exception:
                proj_name = ""

            line = skin.get_input(pt_session, project_name=proj_name, modified=False)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(_repl_commands)
                continue

            # Parse and execute command (shlex handles quoted strings with spaces)
            try:
                args = shlex.split(line)
            except ValueError:
                args = line.split()
            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.warning(f"Usage error: {e}")
            except Exception as e:
                skin.error(f"{e}")

        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


@cli.result_callback()
def auto_save_on_exit(result, use_json, project_path, dry_run, **kwargs):
    """Auto-save project after one-shot commands if state was modified."""
    if _repl_mode:
        return
    if dry_run:
        return
    sess = get_session()
    if sess.has_project() and sess._modified and sess.project_path:
        try:
            sess.save_session()
        except Exception as e:
            click.echo(f"Warning: Auto-save failed: {e}", err=True)


@cli.group()
def project():
    """Project management commands."""
    pass


@project.command("new")
@click.option("--width", "-w", type=int, default=1920, help="Canvas width")
@click.option("--height", "-h", type=int, default=1080, help="Canvas height")
@click.option("--mode", type=click.Choice(["RGB", "RGBA", "L", "LA"]), default="RGB")
@click.option("--background", "-bg", default="#ffffff", help="Background color")
@click.option("--dpi", type=int, default=72, help="Resolution in DPI")
@click.option("--name", "-n", default="untitled", help="Project name")
@click.option("--profile", "-p", type=str, default=None, help="Canvas profile")
@click.option("--output", "-o", type=str, default=None, help="Save path")
@handle_error
def project_new(width, height, mode, background, dpi, name, profile, output):
    """Create a new project."""
    proj = proj_mod.create_project(
        width=width,
        height=height,
        color_mode=mode,
        background=background,
        dpi=dpi,
        name=name,
        profile=profile,
    )
    sess = get_session()
    sess.set_project(proj, output)
    if output:
        proj_mod.save_project(proj, output)
    output_data = proj_mod.get_project_info(proj)
    globals()["output"](output_data, f"Created project: {name}")


@project.command("open")
@click.argument("path")
@handle_error
def project_open(path):
    """Open an existing project."""
    proj = proj_mod.open_project(path)
    sess = get_session()
    sess.set_project(proj, path)
    info = proj_mod.get_project_info(proj)
    output(info, f"Opened: {path}")
