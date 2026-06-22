# ruff: noqa: F403, F405, E501
from .zotero_cli_base import *  # noqa: F403

# fmt: off
from .zotero_cli_p1 import RootCliConfig, _repl_root_args, current_session  # noqa: E402,E501
from .zotero_cli_p3 import _handle_repl_builtin  # noqa: E402,E501
# fmt: on


def _supports_fancy_repl_output() -> bool:
    is_tty = getattr(sys.stdout, "isatty", lambda: False)()
    if not is_tty:
        return False
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        "▸↑⊙﹞".encode(encoding)
    except UnicodeEncodeError:
        return False
    return True


def _safe_print_banner(skin: ReplSkin) -> None:
    if not _supports_fancy_repl_output():
        click.echo("cli-anything-zotero REPL")
        click.echo(f"Skill: {skin.skill_path}")
        click.echo("Type help for commands, quit to exit")
        return
    try:
        skin.print_banner()
    except UnicodeEncodeError:
        click.echo("cli-anything-zotero REPL")
        click.echo(f"Skill: {skin.skill_path}")
        click.echo("Type help for commands, quit to exit")


def _safe_print_goodbye(skin: ReplSkin) -> None:
    if not _supports_fancy_repl_output():
        click.echo("Goodbye!")
        return
    try:
        skin.print_goodbye()
    except UnicodeEncodeError:
        click.echo("Goodbye!")


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.option(
    "--backend",
    type=click.Choice(["auto", "sqlite", "api"]),
    default="auto",
    show_default=True,
)
@click.option("--data-dir", default=None, help="Explicit Zotero data directory.")
@click.option("--profile-dir", default=None, help="Explicit Zotero profile directory.")
@click.option("--executable", default=None, help="Explicit Zotero executable path.")
@click.pass_context
def cli(
    ctx: click.Context,
    json_output: bool,
    backend: str,
    data_dir: str | None,
    profile_dir: str | None,
    executable: str | None,
) -> int:
    """Agent-native Zotero CLI using SQLite, connector, and Local API backends."""
    ctx.ensure_object(dict)
    cli_config = RootCliConfig(
        backend=backend,
        data_dir=data_dir,
        profile_dir=profile_dir,
        executable=executable,
        json_output=json_output,
    )
    ctx.obj["json_output"] = json_output
    ctx.obj["cli_config"] = cli_config
    ctx.obj["config"] = {
        "backend": backend,
        "data_dir": data_dir,
        "profile_dir": profile_dir,
        "executable": executable,
    }
    if ctx.invoked_subcommand is None:
        return run_repl(cli_config)
    return 0


def run_repl(config: RootCliConfig | None = None) -> int:
    config = config or RootCliConfig()
    skin = ReplSkin("zotero", version=__version__)
    prompt_session = None
    try:
        prompt_session = skin.create_prompt_session()
    except NoConsoleScreenBufferError:
        prompt_session = None
    _safe_print_banner(skin)
    while True:
        try:
            if prompt_session is None:
                line = input("zotero> ").strip()
            else:
                line = skin.get_input(prompt_session).strip()
        except EOFError:
            click.echo()
            _safe_print_goodbye(skin)
            return 0
        except KeyboardInterrupt:
            click.echo()
            continue
        if not line:
            continue
        try:
            argv = shlex.split(line)
        except ValueError as exc:
            skin.error(f"parse error: {exc}")
            continue
        handled, control = _handle_repl_builtin(argv, skin, config)
        if handled:
            if control == 1:
                _safe_print_goodbye(skin)
                return 0
            continue
        expanded = session_mod.expand_repl_aliases_with_state(argv, current_session())
        result = dispatch(_repl_root_args(config) + expanded)
        if result not in (0, None):
            skin.warning(f"command exited with status {result}")
        else:
            session_mod.append_command_history(line)


# fmt: off — deferred to break import cycle
from .zotero_cli_p5 import dispatch  # noqa: E402,E501
