# ruff: noqa: F403, F405, E501
from .zotero_cli_base import *  # noqa: F403


@dataclass(frozen=True)
class RootCliConfig:
    backend: str = "auto"
    data_dir: str | None = None
    profile_dir: str | None = None
    executable: str | None = None
    json_output: bool = False


def _stdout_encoding() -> str:
    return getattr(sys.stdout, "encoding", None) or "utf-8"


def _can_encode_for_stdout(text: str) -> bool:
    try:
        text.encode(_stdout_encoding())
    except UnicodeEncodeError:
        return False
    return True


def _safe_text_for_stdout(text: str) -> str:
    if _can_encode_for_stdout(text):
        return text
    return text.encode(_stdout_encoding(), errors="backslashreplace").decode(
        _stdout_encoding()
    )


def _json_text(data: Any) -> str:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if _can_encode_for_stdout(text):
        return text
    return json.dumps(data, ensure_ascii=True, indent=2)


def root_json_output(ctx: click.Context | None) -> bool:
    if ctx is None:
        return False
    root = ctx.find_root()
    if root is None or root.obj is None:
        return False
    cli_config = root.obj.get("cli_config")
    if isinstance(cli_config, RootCliConfig):
        return cli_config.json_output
    return bool(root.obj.get("json_output"))


def _build_runtime_from_config(config: RootCliConfig) -> discovery.RuntimeContext:
    return discovery.build_runtime_context(
        backend=config.backend,
        data_dir=config.data_dir,
        profile_dir=config.profile_dir,
        executable=config.executable,
    )


def _current_cli_config(ctx: click.Context | None) -> RootCliConfig:
    if ctx is None:
        return RootCliConfig()
    root = ctx.find_root()
    assert root is not None
    root.ensure_object(dict)
    cli_config = root.obj.get("cli_config")
    if isinstance(cli_config, RootCliConfig):
        return cli_config
    legacy = root.obj.get("config", {})
    cli_config = RootCliConfig(
        backend=legacy.get("backend", "auto"),
        data_dir=legacy.get("data_dir"),
        profile_dir=legacy.get("profile_dir"),
        executable=legacy.get("executable"),
        json_output=bool(root.obj.get("json_output")),
    )
    root.obj["cli_config"] = cli_config
    return cli_config


def _repl_root_args(config: RootCliConfig) -> list[str]:
    args = ["--backend", config.backend]
    if config.json_output:
        args.append("--json")
    if config.data_dir:
        args.extend(["--data-dir", config.data_dir])
    if config.profile_dir:
        args.extend(["--profile-dir", config.profile_dir])
    if config.executable:
        args.extend(["--executable", config.executable])
    return args


def current_runtime(ctx: click.Context) -> discovery.RuntimeContext:
    root = ctx.find_root()
    assert root is not None
    root.ensure_object(dict)
    cached = root.obj.get("runtime")
    config = _current_cli_config(ctx)
    if cached is None:
        cached = _build_runtime_from_config(config)
        root.obj["runtime"] = cached
    return cached


def current_session() -> dict[str, Any]:
    return session_mod.load_session_state()
