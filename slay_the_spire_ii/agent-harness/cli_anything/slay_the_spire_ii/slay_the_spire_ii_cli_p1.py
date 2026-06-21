# ruff: noqa: F403, F405, E501
from .slay_the_spire_ii_cli_base import *  # noqa: F403


class CliRuntime:
    def __init__(self, base_url: str, timeout: float):
        self.base_url = base_url
        self.timeout = timeout
        self.client = Sts2RawClient(base_url=base_url, timeout=timeout)


def _get_runtime(ctx: click.Context) -> CliRuntime:
    runtime = ctx.obj
    if not isinstance(runtime, CliRuntime):
        raise RuntimeError("CLI runtime not initialized")
    return runtime


@click.group(invoke_without_command=True)
@click.option(
    "--base-url",
    default="http://localhost:15526",
    show_default=True,
    help="Local bridge API base URL",
)
@click.option(
    "--timeout",
    type=float,
    default=10.0,
    show_default=True,
    help="HTTP timeout in seconds",
)
@click.pass_context
def cli(ctx: click.Context, base_url: str, timeout: float) -> None:
    """CLI adapter for controlling the real STS2 game via the local bridge plugin.

    Run without a subcommand to enter interactive REPL mode.
    """
    ctx.obj = CliRuntime(base_url=base_url, timeout=timeout)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.command()
@click.pass_context
def repl(ctx: click.Context) -> None:
    """Start an interactive sts2 shell."""
    runtime = _get_runtime(ctx)
    skin = ReplSkin("slay_the_spire_ii", version=__version__)
    skin.print_banner()
    skin.hint("Type a command such as `state` or `play-card 0 --target NIBBIT_0`.")
    skin.hint("Type `help` to show shortcuts. Type `quit` or `exit` to leave.")
    print()

    pt_session = skin.create_prompt_session()

    while True:
        try:
            line = skin.get_input(pt_session, context=runtime.base_url)
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            return

        if not line:
            continue

        lowered = line.lower()
        if lowered in {"quit", "exit"}:
            skin.print_goodbye()
            return
        if lowered == "help":
            skin.help(_repl_commands())
            continue

        try:
            argv = shlex.split(line)
        except ValueError as exc:
            skin.warning(str(exc))
            continue

        if argv and argv[0] == "repl":
            skin.warning("Already in REPL. Run a command directly instead.")
            continue

        try:
            cli.main(
                args=[
                    "--base-url",
                    runtime.base_url,
                    "--timeout",
                    str(runtime.timeout),
                    *argv,
                ],
                prog_name="cli-anything-sts2",
                standalone_mode=False,
            )
        except click.ClickException as exc:
            skin.error(exc.format_message())
        except click.exceptions.Exit as exc:
            if exc.exit_code not in (None, 0):
                skin.error(f"Command exited with status {exc.exit_code}")
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
            if code not in (None, 0):
                skin.error(f"Command exited with status {code}")
        except Exception as exc:
            skin.error(str(exc))


def _repl_commands() -> dict[str, str]:
    commands = {
        name: cmd.short_help or ""
        for name, cmd in cli.commands.items()
        if name != "repl"
    }
    commands["help"] = "Show this help"
    commands["quit"] = "Exit REPL"
    return commands


def _print_json(value: object) -> None:
    json.dump(value, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def _run_json(command: Callable[[], object]) -> None:
    try:
        _print_json(command())
    except (ApiError, RuntimeError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


def _coerce_value(raw: str) -> object:
    if raw.isdigit() or (raw.startswith("-") and raw[1:].isdigit()):
        return int(raw)
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    return raw


def _parse_kv_pairs(entries: list[str]) -> dict[str, object]:
    result: dict[str, object] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError(f"Expected key=value, got: {entry}")
        key, raw_value = entry.split("=", 1)
        result[key] = _coerce_value(raw_value)
    return result
