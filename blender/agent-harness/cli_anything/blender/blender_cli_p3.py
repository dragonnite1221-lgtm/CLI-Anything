# ruff: noqa: F403, F405, E501
from .blender_cli_base import *  # noqa: F403

# fmt: off
from .blender_cli_p1 import get_session  # noqa: E402,E501
from .blender_cli_p2 import cli, handle_error  # noqa: E402,E501
# fmt: on


@cli.command()
@click.option("--project", "project_path", type=str, default=None)
@handle_error
def repl(project_path):
    """Start interactive REPL session."""
    from cli_anything.blender.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("blender", version="1.0.0")

    if project_path:
        sess = get_session()
        proj = scene_mod.open_scene(project_path)
        sess.set_project(proj, project_path)

    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "scene": "new|open|save|info|profiles|json",
        "object": "add|remove|duplicate|transform|set|list|get",
        "material": "create|assign|set|list|get",
        "modifier": "list-available|info|add|remove|set|list",
        "camera": "add|set|set-active|list",
        "light": "add|set|list",
        "animation": "keyframe|remove-keyframe|frame-range|fps|list-keyframes",
        "render": "settings|info|presets|execute|script",
        "preview": "recipes|capture|latest|live start|push|status|stop",
        "session": "status|undo|redo|history",
        "help": "show this help",
        "quit": "exit REPL",
    }

    while True:
        try:
            sess = get_session()
            project_name = ""
            modified = False
            if sess.has_project():
                if sess.project_path:
                    project_name = os.path.basename(sess.project_path)
                else:
                    info = sess.get_project()
                    project_name = info.get("scene", {}).get(
                        "name", info.get("name", "")
                    )
                modified = sess._modified

            line = skin.get_input(
                pt_session, project_name=project_name, modified=modified
            ).strip()
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
def scene():
    """Scene management commands."""
    pass
