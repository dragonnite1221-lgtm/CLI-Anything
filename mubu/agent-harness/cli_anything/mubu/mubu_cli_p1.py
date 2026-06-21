# ruff: noqa: F403, F405, E501
from .mubu_cli_base import *  # noqa: F403
# fmt: off
# fmt: on


def normalize_program_name(program_name: str | None) -> str:
    candidate = Path(program_name or "").name.strip()
    if candidate == PUBLIC_PROGRAM_NAME:
        return PUBLIC_PROGRAM_NAME
    return COMPAT_PROGRAM_NAME


def repl_help_text(program_name: str | None = None) -> str:
    return REPL_HELP_TEMPLATE.format(program_name=normalize_program_name(program_name))


def session_state_dir() -> Path:
    override = os.environ.get("CLI_ANYTHING_MUBU_STATE_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    config_root = Path.home() / ".config"
    public_dir = config_root / PUBLIC_PROGRAM_NAME
    legacy_dir = config_root / COMPAT_PROGRAM_NAME
    if public_dir.exists():
        return public_dir
    if legacy_dir.exists():
        return legacy_dir
    return public_dir


def session_state_path() -> Path:
    return session_state_dir() / "session.json"


def default_session_state() -> dict[str, object]:
    return {
        "current_doc": None,
        "current_node": None,
        "command_history": [],
    }


def load_session_state() -> dict[str, object]:
    path = session_state_path()
    try:
        data = json.loads(path.read_text(errors="replace"))
    except FileNotFoundError:
        return default_session_state()
    except json.JSONDecodeError:
        return default_session_state()

    history = data.get("command_history")
    normalized_history = (
        [item for item in history if isinstance(item, str)]
        if isinstance(history, list)
        else []
    )
    return {
        "current_doc": data.get("current_doc")
        if isinstance(data.get("current_doc"), str)
        else None,
        "current_node": data.get("current_node")
        if isinstance(data.get("current_node"), str)
        else None,
        "command_history": normalized_history[-COMMAND_HISTORY_LIMIT:],
    }


def locked_save_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = open(path, "r+")
    except FileNotFoundError:
        handle = open(path, "w")
    with handle:
        locked = False
        try:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            locked = True
        except (ImportError, OSError):
            pass
        try:
            handle.seek(0)
            handle.truncate()
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.flush()
        finally:
            if locked:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def print_repl_banner(skin: ReplSkin, program_name: str | None = None) -> None:
    normalized_program_name = normalize_program_name(program_name)
    click.echo("Mubu REPL")
    if normalized_program_name == PUBLIC_PROGRAM_NAME:
        click.echo(f"Command: {PUBLIC_PROGRAM_NAME}")
        click.echo(f"Version: {__version__}")
        if skin.skill_path:
            click.echo(f"Skill: {skin.skill_path}")
        click.echo("Type help for commands, quit to exit")
        click.echo()
    else:
        skin.print_banner()
    click.echo(f"History: {skin.history_file}")


def root_json_output(ctx: click.Context | None) -> bool:
    if ctx is None:
        return False
    root = ctx.find_root()
    if root is None or root.obj is None:
        return False
    return bool(root.obj.get("json_output"))


def emit_json(payload: object) -> None:
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def print_repl_help(program_name: str | None = None) -> None:
    click.echo(repl_help_text(program_name).rstrip())


def parse_history_limit(argv: Sequence[str]) -> int:
    if len(argv) < 2:
        return 10
    try:
        return max(1, int(argv[1]))
    except ValueError as exc:
        raise RuntimeError(f"history limit must be an integer: {argv[1]}") from exc


def save_session_state(session: dict[str, object]) -> None:
    locked_save_json(
        session_state_path(),
        {
            "current_doc": session.get("current_doc"),
            "current_node": session.get("current_node"),
            "command_history": list(session.get("command_history", [])),
        },
    )


def append_command_history(command_line: str) -> None:
    command_line = command_line.strip()
    if not command_line:
        return
    session = load_session_state()
    history = list(session.get("command_history", []))
    history.append(command_line)
    session["command_history"] = history[-COMMAND_HISTORY_LIMIT:]
    save_session_state(session)


def resolve_current_daily_doc_ref(folder_ref: str | None = None) -> str:
    resolved_folder_ref = mubu_probe.resolve_daily_folder_ref(folder_ref)
    metas = mubu_probe.load_document_metas(mubu_probe.DEFAULT_STORAGE_ROOT)
    folders = mubu_probe.load_folders(mubu_probe.DEFAULT_STORAGE_ROOT)
    docs, folder, ambiguous = mubu_probe.folder_documents(
        metas, folders, resolved_folder_ref
    )
    if folder is None:
        if ambiguous:
            raise RuntimeError(
                mubu_probe.ambiguous_error_message(
                    "folder", resolved_folder_ref, ambiguous, "path"
                )
            )
        raise RuntimeError(f"folder not found: {resolved_folder_ref}")
    selected, _ = mubu_probe.choose_current_daily_document(docs)
    if selected is None or not selected.get("doc_path"):
        raise RuntimeError(f"no current daily document found in {folder['path']}")
    return str(selected["doc_path"])
