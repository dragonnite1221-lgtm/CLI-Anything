# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import cli  # noqa: E402,E501
# fmt: on


@cli.command()
@click.option("--project", "-p", default=None, help="Project file to open in REPL.")
@click.pass_context
def repl(ctx: click.Context, project: Optional[str]) -> None:
    """Start the interactive REPL session."""
    skin = ReplSkin("cloudcompare", version=VERSION)
    skin.print_banner()

    if not is_available():
        skin.warning("CloudCompare not found. Install it first.")
        skin.hint("  flatpak install flathub org.cloudcompare.CloudCompare")
        skin.print_goodbye()
        return

    # Override project from REPL flag
    project_path = project or (ctx.obj.get("project") if ctx.obj else None)
    session = Session(project_path) if project_path else None

    pt_session = skin.create_prompt_session()
    json_mode = ctx.obj.get("json", False) if ctx.obj else False

    # Build command reference
    commands = {
        "project new -o <file>": "Create a new project",
        "project info": "Show project status",
        "cloud add <file>": "Add a cloud to the project",
        "cloud list": "List loaded clouds",
        "cloud subsample <idx>": "Subsample a cloud",
        "cloud roughness <idx>": "Compute roughness SF",
        "cloud density <idx>": "Compute density SF",
        "cloud normals <idx>": "Compute normals",
        "cloud filter-sor <idx>": "Statistical Outlier Removal",
        "cloud crop <idx>": "Crop to bounding box",
        "cloud merge": "Merge all clouds",
        "distance c2c": "Cloud-to-cloud distance",
        "distance c2m": "Cloud-to-mesh distance",
        "transform icp": "ICP registration",
        "export cloud <idx>": "Export a cloud",
        "export mesh <idx>": "Export a mesh",
        "session save": "Save the project",
        "session history": "Show operation history",
        "help": "Show this help",
        "quit / exit": "Exit the REPL",
    }

    while True:
        proj_name = session.name if session else ""
        modified = session.is_modified if session else False
        try:
            line = skin.get_input(pt_session, project_name=proj_name, modified=modified)
        except (EOFError, KeyboardInterrupt):
            break

        if not line:
            continue

        if line.lower() in ("quit", "exit", "q"):
            if session and session.is_modified:
                skin.warning("Unsaved changes in project. Save with: session save")
            break

        if line.lower() in ("help", "h", "?"):
            skin.help(commands)
            continue

        # Parse and invoke as Click command via subprocess-style invocation
        try:
            args = line.split()
            # Inject project context if available
            if session and "--project" not in args and "-p" not in args:
                args = ["--project", session.project_path] + args
            if json_mode:
                args = ["--json"] + args
            standalone_mode_result = cli.main(
                args=args,
                standalone_mode=False,
                obj={
                    "project": session.project_path if session else None,
                    "json": json_mode,
                },
            )
            # Update session when project new or explicit -p/--project is used
            new_path: Optional[str] = None
            raw = line.split()
            if len(raw) >= 2 and raw[0] == "project" and raw[1] == "new":
                for i, tok in enumerate(raw):
                    if tok in ("-o", "--output") and i + 1 < len(raw):
                        new_path = raw[i + 1]
                        break
            elif "--project" in raw or "-p" in raw:
                for i, tok in enumerate(raw):
                    if tok in ("--project", "-p") and i + 1 < len(raw):
                        new_path = raw[i + 1]
                        break
            if new_path:
                session = Session(new_path)
        except SystemExit:
            pass
        except click.UsageError as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))

    skin.print_goodbye()


@cli.group()
def project() -> None:
    """Project management commands (create, open, inspect)."""
