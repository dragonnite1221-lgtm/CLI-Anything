# ruff: noqa: F403, F405, E501
from .obs_studio_cli_base import *  # noqa: F403

# fmt: off
from .obs_studio_cli_p1 import _repl_help, cli, get_session, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.command()
@click.option("--project", "project_path", type=str, default=None)
@handle_error
def repl(project_path):
    """Start interactive REPL session."""
    from cli_anything.obs_studio.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("obs_studio", version="1.0.0")

    if project_path:
        sess = get_session()
        proj = proj_mod.open_project(project_path)
        sess.set_project(proj, project_path)

    skin.print_banner()

    pt_session = skin.create_prompt_session()

    def _get_project_name():
        """Get current project name for prompt display."""
        try:
            sess = get_session()
            if sess.has_project():
                info = proj_mod.get_project_info(sess.get_project())
                return info.get("name", "")
        except Exception:
            pass
        return ""

    while True:
        try:
            line = skin.get_input(
                pt_session,
                project_name=_get_project_name(),
                modified=False,
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
@click.option("--width", "-w", type=int, default=1920, help="Output width")
@click.option("--height", "-h", type=int, default=1080, help="Output height")
@click.option("--fps", type=int, default=30, help="Frames per second")
@click.option("--encoder", type=str, default="x264", help="Video encoder")
@click.option("--output", "-o", type=str, default=None, help="Save path")
@handle_error
def project_new(name, width, height, fps, encoder, output):
    """Create a new OBS scene collection."""
    proj = proj_mod.create_project(
        name=name,
        output_width=width,
        output_height=height,
        fps=fps,
        encoder=encoder,
    )
    sess = get_session()
    sess.set_project(proj, output)
    if output:
        proj_mod.save_project(proj, output)
    info = proj_mod.get_project_info(proj)
    globals()["output"](info, f"Created project: {name}")
