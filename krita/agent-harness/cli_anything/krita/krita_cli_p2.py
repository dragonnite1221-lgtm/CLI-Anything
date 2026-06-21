# ruff: noqa: F403, F405, E501
from .krita_cli_base import *  # noqa: F403

# fmt: off
from .krita_cli_p1 import cli  # noqa: E402,E501
# fmt: on


@cli.command("repl", hidden=True)
@click.option("--project-path", type=click.Path(), default=None)
@click.pass_context
def repl(ctx, project_path):
    """Interactive REPL mode."""
    global _current_project, _current_project_path

    try:
        from cli_anything.krita.utils.repl_skin import ReplSkin
    except ImportError:
        click.echo(
            "REPL requires prompt-toolkit. Install with: pip install prompt-toolkit"
        )
        return

    skin = ReplSkin("krita", version="1.0.0")
    skin.print_banner()

    if project_path:
        try:
            _current_project = open_project(project_path)
            _current_project_path = project_path
            _session.snapshot(_current_project, f"Opened '{project_path}'")
            skin.success(f"Loaded project: {project_path}")
        except Exception as exc:
            skin.error(f"Failed to load project: {exc}")

    try:
        pt_session = skin.create_prompt_session()
    except Exception:
        pt_session = None

    commands_dict = {
        "project new": "Create a new project",
        "project open <path>": "Open a project file",
        "project save [-o path]": "Save current project",
        "project info": "Show project info",
        "layer add <name> [-t type]": "Add a layer",
        "layer remove <name>": "Remove a layer",
        "layer list": "List all layers",
        "layer set <name> <prop> <val>": "Set layer property",
        "filter apply <name> [-l layer]": "Apply a filter",
        "filter list": "List available filters",
        "canvas resize [-w W] [-h H]": "Resize canvas",
        "canvas info": "Show canvas info",
        "export render <path> [-p preset]": "Export to file",
        "export presets": "List export presets",
        "export formats": "List export formats",
        "session undo": "Undo last operation",
        "session redo": "Redo last operation",
        "session history": "Show history",
        "status": "Show current status",
        "help": "Show this help",
        "quit / exit": "Exit REPL",
    }

    while True:
        try:
            proj_name = _current_project.get("name", "") if _current_project else ""
            modified = _session.can_undo()
            line = skin.get_input(pt_session, project_name=proj_name, modified=modified)
        except (EOFError, KeyboardInterrupt):
            break

        if line is None:
            break

        line = line.strip()
        if not line:
            continue
        if line.lower() in ("quit", "exit", "q"):
            break
        if line.lower() == "help":
            skin.help(commands_dict)
            continue

        # Parse and dispatch to Click commands
        args = line.split()
        try:
            cli.main(
                args=args, standalone_mode=False, **{"parent": ctx, "obj": ctx.obj}
            )
        except SystemExit:
            pass
        except click.exceptions.UsageError as exc:
            skin.error(str(exc))
        except Exception as exc:
            skin.error(str(exc))

    skin.print_goodbye()
