# ruff: noqa: F403, F405, E501
from .audacity_cli_base import *  # noqa: F403

# fmt: off
from .audacity_cli_p1 import _repl_help, cli, get_session, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.command()
@click.option("--project", "project_path", type=str, default=None)
@handle_error
def repl(project_path):
    """Start interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.audacity.utils.repl_skin import ReplSkin

    skin = ReplSkin("audacity", version="1.0.0")

    if project_path:
        sess = get_session()
        proj = proj_mod.open_project(project_path)
        sess.set_project(proj, project_path)

    skin.print_banner()

    pt_session = skin.create_prompt_session()

    while True:
        try:
            sess = get_session()
            proj_name = ""
            modified = False
            if sess.has_project():
                proj = sess.get_project()
                proj_name = proj.get("name", "")
                modified = sess.is_modified() if hasattr(sess, "is_modified") else False

            line = skin.get_input(pt_session, project_name=proj_name, modified=modified)
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
@click.option("--sample-rate", "-sr", type=int, default=44100, help="Sample rate")
@click.option("--bit-depth", "-bd", type=int, default=16, help="Bit depth")
@click.option(
    "--channels", "-ch", type=int, default=2, help="Channels (1=mono, 2=stereo)"
)
@click.option("--output", "-o", type=str, default=None, help="Save path")
@handle_error
def project_new(name, sample_rate, bit_depth, channels, output):
    """Create a new project."""
    proj = proj_mod.create_project(
        name=name,
        sample_rate=sample_rate,
        bit_depth=bit_depth,
        channels=channels,
    )
    sess = get_session()
    sess.set_project(proj, output)
    if output:
        proj_mod.save_project(proj, output)
    info = proj_mod.get_project_info(proj)
    globals()["output"](info, f"Created project: {name}")


@project.command("open")
@click.argument("path")
@handle_error
def project_open(path):
    """Open an existing project."""
    proj = proj_mod.open_project(path)
    sess = get_session()
    sess.set_project(proj, path)
    info = proj_mod.get_project_info(proj)
    globals()["output"](info, f"Opened: {path}")
