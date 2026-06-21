# ruff: noqa: F403, F405, E501
from .qgis_cli_base import *  # noqa: F403

# fmt: off
from .qgis_cli_p1 import _current_project_modified, _requested_project_path, _sync_session_project_path, cli, get_session, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.command()
@handle_error
def repl():
    """Start the interactive REPL."""
    from cli_anything.qgis.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("qgis", version=__version__)
    skin.print_banner()
    prompt_session = skin.create_prompt_session()

    command_help = {
        "project": "new|open|save|info|set-crs",
        "layer": "create-vector|list|info|remove",
        "feature": "add|list",
        "layout": "create|list|info|remove|add-map|add-label",
        "export": "presets|pdf|image",
        "process": "list|help|run",
        "session": "status|history",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    try:
        while True:
            _sync_session_project_path()
            session_state = get_session()
            line = skin.get_input(
                prompt_session,
                project_name=session_state.active_project_name,
                modified=_current_project_modified(),
            )
            if not line:
                continue
            lowered = line.lower()
            if lowered in {"quit", "exit", "q"}:
                skin.print_goodbye()
                break
            if lowered == "help":
                skin.help(command_help)
                continue

            try:
                args = shlex.split(line)
            except ValueError as exc:
                skin.error(str(exc))
                continue

            try:
                cli.main(args=args, standalone_mode=False)
            except SystemExit:
                pass
            except click.ClickException as exc:
                skin.error(str(exc))
            except Exception as exc:  # pragma: no cover - last-resort REPL guard
                skin.error(str(exc))
    finally:
        _repl_mode = False


def _load_requested_project(required: bool = False) -> str | None:
    requested = _requested_project_path()
    if requested:
        normalized = project_mod.normalize_project_path(requested)
        if project_mod.current_project_path() != normalized:
            project_mod.open_project(normalized)
            _sync_session_project_path()
        return normalized

    if required and not project_mod.current_project_path():
        raise QgisBackendError(
            "No project is loaded. Open one with project open or pass --project."
        )

    return project_mod.current_project_path() or None


def _active_project_path(required: bool = False) -> str | None:
    requested = _requested_project_path()
    if requested:
        return project_mod.normalize_project_path(requested)

    current = project_mod.current_project_path()
    if current:
        return current

    if required:
        raise QgisBackendError(
            "No project is loaded. Open one with project open or pass --project."
        )
    return None


def _auto_save_if_one_shot() -> None:
    if _repl_mode:
        return
    if project_mod.current_project_path():
        project_mod.save_project()
        _sync_session_project_path()


def _record(command: str, args: dict, result=None) -> None:
    summary = None
    if isinstance(result, dict):
        summary_keys = {
            "path",
            "output",
            "format",
            "title",
            "layer_count",
            "layout_count",
            "feature_count",
            "count",
            "name",
        }
        summary = {key: value for key, value in result.items() if key in summary_keys}
        if not summary and "layer" in result and isinstance(result["layer"], dict):
            summary = {"layer": result["layer"].get("name")}
    get_session().record(command, args, summary)


@cli.group()
def project():
    """Project management commands."""


@project.command("new")
@click.option(
    "-o", "--output", "output_path", required=True, type=click.Path(path_type=Path)
)
@click.option("--title", default=None, help="Project title")
@click.option("--crs", default="EPSG:4326", help="Project CRS, e.g. EPSG:4326")
@handle_error
def project_new(output_path: Path, title: str | None, crs: str):
    """Create a new saved QGIS project."""
    data = project_mod.create_project(str(output_path), title=title, crs=crs)
    _sync_session_project_path()
    _record(
        "project new", {"output": str(output_path), "title": title, "crs": crs}, data
    )
    output(data, f"Created project: {data['path']}")
