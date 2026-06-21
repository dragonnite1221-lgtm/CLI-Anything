# ruff: noqa: F403, F405, E501
from .kdenlive_cli_base import *  # noqa: F403

# fmt: off
from .kdenlive_cli_p1 import cli, get_session, handle_error  # noqa: E402,E501
# fmt: on


@cli.command()
@click.option("--project", "project_path", type=str, default=None)
@handle_error
def repl(project_path):
    """Start interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    if project_path:
        sess = get_session()
        proj = proj_mod.open_project(project_path)
        sess.set_project(proj, project_path)

    skin = ReplSkin("kdenlive", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    commands_dict = {
        "project new|open|save|info|profiles|json": "Project management",
        "bin import|remove|list|get": "Media bin management",
        "timeline add-track|remove-track|add-clip|remove-clip|trim|split|move|list": "Timeline management",
        "filter add|remove|set|list|available": "Filter/effect management",
        "transition add|remove|set|list": "Transition management",
        "guide add|remove|list": "Guide/marker management",
        "export xml|presets": "Export and render",
        "session status|undo|redo|history": "Session management",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    while True:
        try:
            sess = get_session()
            project_name = ""
            modified = False
            if sess.has_project():
                proj = sess.get_project()
                project_name = proj.get("name", "")
                modified = sess.is_modified() if hasattr(sess, "is_modified") else False

            line = skin.get_input(
                pt_session, project_name=project_name, modified=modified
            )
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(commands_dict)
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
                skin.error(str(e))

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
@click.option("--name", "-n", default="untitled", help="Project name")
@click.option("--profile", "-p", type=str, default=None, help="Video profile")
@click.option("--width", type=int, default=1920)
@click.option("--height", type=int, default=1080)
@click.option("--fps-num", type=int, default=30)
@click.option("--fps-den", type=int, default=1)
@click.option("--output", "-o", type=str, default=None, help="Save path")
@handle_error
def project_new(name, profile, width, height, fps_num, fps_den, output):
    """Create a new project."""
    proj = proj_mod.create_project(
        name=name,
        profile=profile,
        width=width,
        height=height,
        fps_num=fps_num,
        fps_den=fps_den,
    )
    sess = get_session()
    sess.set_project(proj, output)
    if output:
        proj_mod.save_project(proj, output)
    info = proj_mod.get_project_info(proj)
    globals()["output"](info, f"Created project: {name}")
