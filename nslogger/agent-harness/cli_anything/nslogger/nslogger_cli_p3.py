# ruff: noqa: F403, F405, E501
from .nslogger_cli_base import *  # noqa: F403
# fmt: off
from .nslogger_cli_p1 import _json_option, _level_option, _parse_dt, cli  # noqa: E402,E501
# fmt: on


@cli.command(name="filter")
@click.argument("file", type=click.Path(exists=True))
@_level_option()
@click.option("--min-level", type=int, default=None, help="Minimum log level")
@click.option("--tag", "-t", multiple=True, help="Filter by tag")
@click.option("--thread", help="Filter by thread ID")
@click.option("--search", "-s", help="Substring search in message text")
@click.option("--regex", "-r", help="Regex search in message text")
@click.option("--type", "msg_type", multiple=True,
              type=click.Choice(["text", "image", "data", "client_info", "block_start", "block_end"]),
              help="Filter by message type")
@click.option("--limit", "-n", type=int, default=None, help="Max messages")
@click.option("--after", default=None, help="Show messages after this time (HH:MM:SS or YYYY-MM-DDTHH:MM:SS)")
@click.option("--before", default=None, help="Show messages before this time")
@click.option("--from-seq", type=int, default=None, help="Start from sequence number (inclusive)")
@click.option("--to-seq", type=int, default=None, help="End at sequence number (inclusive)")
@_json_option()
def filter_cmd(file, level, min_level, tag, thread, search, regex, msg_type, limit,
               after, before, from_seq, to_seq, as_json):
    """Filter messages from a file with advanced criteria."""
    msgs = parse_file(file)
    msgs = filter_messages(
        msgs,
        max_level=level,
        min_level=min_level,
        tags=list(tag) if tag else None,
        thread_id=thread,
        text_search=search,
        text_regex=regex,
        msg_types=list(msg_type) if msg_type else None,
        limit=limit,
        after=_parse_dt(after),
        before=_parse_dt(before),
        from_seq=from_seq,
        to_seq=to_seq,
    )
    result = list(msgs)
    if as_json:
        click.echo(json.dumps([m.to_dict() for m in result], indent=2, default=str))
    else:
        for m in result:
            click.echo(m.to_text_line())
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--format", "-f", "fmt",
              type=click.Choice(["text", "json", "csv"]), default="text",
              show_default=True, help="Output format")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Output file (default: stdout)")
@_level_option()
@click.option("--tag", "-t", multiple=True, help="Filter by tag before export")
@click.option("--search", "-s", help="Filter by text before export")
@click.option("--limit", "-n", type=int, default=None, help="Max messages")
def export(file, fmt, output, level, tag, search, limit):
    """Export messages to text, JSON, or CSV."""
    msgs = parse_file(file)
    msgs = filter_messages(
        msgs,
        max_level=level,
        tags=list(tag) if tag else None,
        text_search=search,
        limit=limit,
    )
    result_str = export_messages(msgs, fmt=fmt)
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result_str)
        click.echo(f"Exported to {output}", err=True)
    else:
        click.echo(result_str, nl=False)
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@_json_option()
def stats(file, as_json):
    """Show statistics for a NSLogger file."""
    msgs = parse_file(file)
    s = compute_stats(msgs)
    if as_json:
        click.echo(json.dumps(s, indent=2, default=str))
        return

    click.echo(f"Total messages : {s['total']}")
    if s.get("first_timestamp"):
        click.echo(f"First message  : {s['first_timestamp']}")
        click.echo(f"Last message   : {s['last_timestamp']}")
    if s.get("duration_seconds") is not None:
        click.echo(f"Duration       : {s['duration_seconds']:.1f}s")
    if s.get("clients"):
        click.echo(f"Clients        : {', '.join(s['clients'])}")
    click.echo("")
    click.echo("By level:")
    for name, count in s.get("by_level", {}).items():
        click.echo(f"  {name:<10} {count}")
    click.echo("")
    click.echo("By type:")
    for name, count in s.get("by_type", {}).items():
        click.echo(f"  {name:<15} {count}")
    if s.get("by_tag"):
        click.echo("")
        click.echo("Top tags:")
        for tag, count in list(s["by_tag"].items())[:10]:
            click.echo(f"  {tag:<20} {count}")
    if s.get("by_thread"):
        click.echo("")
        click.echo("Top threads:")
        for thread, count in list(s["by_thread"].items())[:5]:
            click.echo(f"  {thread:<25} {count}")
