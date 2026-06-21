# ruff: noqa: F403, F405, E501
from .nslogger_cli_base import *  # noqa: F403
# fmt: off
from .nslogger_cli_p1 import _FILE_COMMANDS, _REPL_COMMANDS, _json_option, _level_option, _parse_dt, cli  # noqa: E402,E501
# fmt: on


def _run_repl(ctx, file: Optional[str] = None):
    """Launch the shared cli-anything REPL and dispatch commands through Click."""
    skin = ReplSkin("nslogger", version="0.1.0")
    skin.print_banner()

    current_file = file
    if current_file:
        try:
            message_count = sum(1 for _ in parse_file(current_file))
            skin.success(f"Loaded {message_count} messages from {current_file}")
        except Exception as exc:
            skin.error(f"Could not load {current_file}: {exc}")
            current_file = None

    session = skin.create_prompt_session()

    while True:
        context = os.path.basename(current_file) if current_file else ""
        try:
            user_input = skin.get_input(session, context=context)
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not user_input:
            continue

        raw = user_input.strip()
        command = raw.lower()

        if command in ("quit", "exit", "q"):
            skin.print_goodbye()
            break

        if command in ("help", "h", "?"):
            skin.help(_REPL_COMMANDS)
            continue

        try:
            args = shlex.split(raw)
        except ValueError as exc:
            skin.error(f"Parse error: {exc}")
            continue

        if not args:
            continue

        if args[0] == "load":
            if len(args) != 2:
                skin.error("Usage: load FILE")
                continue
            if not os.path.exists(args[1]):
                skin.error(f"File not found: {args[1]}")
                continue
            current_file = args[1]
            try:
                message_count = sum(1 for _ in parse_file(current_file))
                skin.success(f"Loaded {message_count} messages from {current_file}")
            except Exception as exc:
                skin.error(f"Could not load {current_file}: {exc}")
                current_file = None
            continue

        if args[0] == "current":
            if current_file:
                skin.status("File", current_file)
            else:
                skin.info("No default file loaded.")
            continue

        if args[0] in _FILE_COMMANDS and current_file and (len(args) == 1 or args[1].startswith("-")):
            args.insert(1, current_file)

        try:
            cli.main(args=args, obj=ctx.obj, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.ClickException as exc:
            skin.error(exc.format_message())
        except Exception as exc:
            skin.error(str(exc))
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@_level_option()
@click.option("--tag", "-t", multiple=True, help="Filter by tag (repeatable)")
@click.option("--thread", help="Filter by thread ID")
@click.option("--search", "-s", help="Text search (case-insensitive)")
@click.option("--limit", "-n", type=int, default=None, help="Max messages to show")
@click.option("--after", default=None, help="Show messages after this time (HH:MM:SS or YYYY-MM-DDTHH:MM:SS)")
@click.option("--before", default=None, help="Show messages before this time (HH:MM:SS or YYYY-MM-DDTHH:MM:SS)")
@_json_option()
def read(file, level, tag, thread, search, limit, after, before, as_json):
    """Parse and display messages from a .rawnsloggerdata or .nsloggerdata file."""
    msgs = parse_file(file)
    msgs = filter_messages(
        msgs,
        max_level=level,
        tags=list(tag) if tag else None,
        thread_id=thread,
        text_search=search,
        limit=limit,
        after=_parse_dt(after),
        before=_parse_dt(before),
    )
    result = list(msgs)
    if as_json:
        click.echo(json.dumps([m.to_dict() for m in result], indent=2, default=str))
    else:
        for m in result:
            click.echo(m.to_text_line())
