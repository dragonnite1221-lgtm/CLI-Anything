# ruff: noqa: F403, F405, E501
from .musescore_cli_base import *  # noqa: F403

# fmt: off
from .musescore_cli_p1 import _repl_help, cli, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.command(hidden=True)
@handle_error
def repl():
    """Start interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.musescore.utils.repl_skin import ReplSkin

    skin = ReplSkin("musescore", version="1.0.0")
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
                modified = sess.is_modified()

            line = skin.get_input(pt_session, project_name=proj_name, modified=modified)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                _repl_help(skin)
                continue

            import shlex

            args = shlex.split(line)
            # Preserve --json flag across REPL commands
            if _json_output and "--json" not in args:
                args = ["--json"] + args
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


@project.command("open")
@click.option("-i", "--input", "path", required=True, help="Score file path")
@handle_error
def project_open(path):
    """Open a score file."""
    proj = proj_mod.open_project(path)
    sess = get_session()
    sess.set_project(proj, path)
    output(proj, f"Opened: {path}")


@project.command("info")
@click.option("-i", "--input", "path", required=True, help="Score file path")
@handle_error
def project_info(path):
    """Show score information."""
    info = proj_mod.project_info(path)
    output(info)


@project.command("save")
@click.option("-i", "--input", "input_path", required=True, help="Input score file")
@click.option("-o", "--output", "output_path", required=True, help="Output score file")
@handle_error
def project_save(input_path, output_path):
    """Save/convert a score to .mscz format via mscore export."""
    from cli_anything.musescore.core import export as export_mod_local

    result = export_mod_local.export_score(input_path, output_path, fmt="mscz")
    output(result, f"Saved to: {output_path}")


@cli.group()
def transpose():
    """Transposition commands."""
    pass
