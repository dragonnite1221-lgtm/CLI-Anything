# ruff: noqa: F403, F405, E501
from .nslogger_cli_base import *  # noqa: F403
# fmt: off
from .nslogger_cli_p2 import _run_repl  # noqa: E402,E501
# fmt: on


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}
def _level_option():
    return click.option(
        "--level", "-l",
        type=int, default=None,
        help="Maximum log level to show (0=error … 4=verbose)",
    )
def _json_option():
    return click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    """Parse ISO-like datetime string to aware UTC datetime."""
    if value is None:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%H:%M:%S"):
        try:
            dt = datetime.strptime(value, fmt)
            if dt.year == 1900:
                today = datetime.now(tz=timezone.utc).date()
                dt = dt.replace(year=today.year, month=today.month, day=today.day)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise click.BadParameter(f"Cannot parse datetime: {value!r}. Use HH:MM:SS or YYYY-MM-DDTHH:MM:SS")
def _time_range_options():
    def decorator(f):
        f = click.option("--after", default=None,
                         help="Show messages after this time (HH:MM:SS or YYYY-MM-DDTHH:MM:SS)")(f)
        f = click.option("--before", default=None,
                         help="Show messages before this time (HH:MM:SS or YYYY-MM-DDTHH:MM:SS)")(f)
        return f
    return decorator
def _listen_waiting_message(port: int, bonjour: bool) -> str:
    if bonjour:
        return f"[Bonjour] Waiting for an iOS client to connect on port {port}…"
    return f"Waiting for a client connection on port {port}…"
def _format_live_output_message(msg, fmt: str) -> str:
    if fmt == "jsonl":
        return json.dumps(msg.to_dict(), default=str)
    return msg.to_text_line()
def _open_live_output_file(path: str, append: bool):
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    mode = "a" if append else "w"
    return open(path, mode, encoding="utf-8", buffering=1)
_REPL_COMMANDS = {
    "read [FILE]": "Display parsed messages",
    "filter [FILE] [OPTIONS]": "Filter messages by level, tag, thread, text, regex, or range",
    "tail [FILE]": "Show the last messages from a file",
    "stats [FILE]": "Show summary statistics",
    "clients [FILE]": "List client_info records",
    "blocks [FILE]": "Show block start/end nesting",
    "export [FILE] --format json": "Export messages as text, JSON, or CSV",
    "merge FILE...": "Merge files by timestamp",
    "generate OUTPUT": "Generate a sample raw NSLogger file",
    "listen [OPTIONS]": "Listen for live NSLogger clients",
    "load FILE": "Set the default file for file-based commands",
    "current": "Show the current default file",
    "help": "Show this help",
    "quit / exit": "Exit the REPL",
}
_FILE_COMMANDS = {"read", "filter", "tail", "stats", "clients", "blocks", "export"}
@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.version_option(package_name="cli-anything-nslogger")
@click.pass_context
def cli(ctx):
    """NSLogger CLI — read, filter, export, and monitor NSLogger log files.

    \b
    Use COMMAND -h to see command-specific options, for example:
      cli-anything-nslogger listen -h

    \b
    Live logs can be mirrored to a file with:
      cli-anything-nslogger listen --bonjour --name bazinga --output app.log

    \b
    Live listen file output options:
      -o, --output FILE          Write live logs to FILE while printing stdout
      --output-format text|jsonl Write text lines or JSON Lines
      --append                   Append instead of replacing FILE on startup
    """
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        _run_repl(ctx)
