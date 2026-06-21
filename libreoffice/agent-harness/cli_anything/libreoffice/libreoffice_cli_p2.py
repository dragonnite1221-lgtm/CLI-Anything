# ruff: noqa: F403, F405, E501
from .libreoffice_cli_base import *  # noqa: F403

# fmt: off
from .libreoffice_cli_p1 import _repl_help, cli, get_session, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.command()
@click.option("--project", "project_path", type=str, default=None)
@handle_error
def repl(project_path):
    """Start interactive REPL session."""
    from cli_anything.libreoffice.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("libreoffice", version="1.0.0")

    if project_path:
        sess = get_session()
        proj = doc_mod.open_document(project_path)
        sess.set_project(proj, project_path)

    skin.print_banner()

    pt_session = skin.create_prompt_session()

    def _get_project_name():
        try:
            s = get_session()
            proj = s.get_project()
            if proj and isinstance(proj, dict):
                return proj.get("name", "")
        except Exception:
            pass
        return ""

    def _is_modified():
        try:
            s = get_session()
            return s.is_modified() if hasattr(s, "is_modified") else False
        except Exception:
            return False

    while True:
        try:
            line = skin.get_input(
                pt_session,
                project_name=_get_project_name(),
                modified=_is_modified(),
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
def document():
    """Document management commands."""
    pass


@document.command("new")
@click.option(
    "--type",
    "doc_type",
    type=click.Choice(["writer", "calc", "impress"]),
    default="writer",
    help="Document type",
)
@click.option("--name", "-n", default="untitled", help="Document name")
@click.option("--profile", "-p", type=str, default=None, help="Page profile")
@click.option("--output", "-o", "output_path", type=str, default=None, help="Save path")
@handle_error
def document_new(doc_type, name, profile, output_path):
    """Create a new document."""
    proj = doc_mod.create_document(doc_type=doc_type, name=name, profile=profile)
    sess = get_session()
    sess.set_project(proj, output_path)
    if output_path:
        doc_mod.save_document(proj, output_path)
    info = doc_mod.get_document_info(proj)
    output(info, f"Created {doc_type} document: {name}")


@document.command("open")
@click.argument("path")
@click.option(
    "--output",
    "-o",
    "output_path",
    type=str,
    default=None,
    help="Save imported Office/ODF files to this project JSON path",
)
@click.option(
    "--name", "-n", type=str, default=None, help="Override imported project name"
)
@handle_error
def document_open(path, output_path, name):
    """Open a project JSON file, or import an existing Office/ODF file."""
    if import_mod.can_import(path):
        proj = import_mod.import_document(path, name=name)
        sess = get_session()
        sess.set_project(proj, output_path)
        if output_path:
            doc_mod.save_document(proj, output_path)
        info = doc_mod.get_document_info(proj)
        info["source_path"] = proj.get("metadata", {}).get("source_path")
        info["project_path"] = output_path
        output(info, f"Imported: {path}")
        return

    proj = doc_mod.open_document(path)
    sess = get_session()
    sess.set_project(proj, path)
    info = doc_mod.get_document_info(proj)
    output(info, f"Opened: {path}")


@document.command("import")
@click.argument("path")
@click.option(
    "--output", "-o", "output_path", required=True, help="Project JSON path to create"
)
@click.option(
    "--name", "-n", type=str, default=None, help="Override imported project name"
)
@handle_error
def document_import(path, output_path, name):
    """Import an existing Office/ODF file into a project JSON file."""
    proj = import_mod.import_document(path, name=name)
    doc_mod.save_document(proj, output_path)
    sess = get_session()
    sess.set_project(proj, output_path)
    info = doc_mod.get_document_info(proj)
    info["source_path"] = proj.get("metadata", {}).get("source_path")
    info["project_path"] = output_path
    output(info, f"Imported: {path}")
