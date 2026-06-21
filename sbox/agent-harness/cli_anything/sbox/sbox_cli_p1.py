# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403


def _output(ctx: click.Context, data: Any, human_fn=None) -> None:
    """Output data as JSON or human-readable text.

    Args:
        ctx: Click context with obj["json"] flag.
        data: Data to output (must be JSON-serializable for --json mode).
        human_fn: Optional callable that returns a human-readable string.
                  If None, falls back to a pretty-printed representation.
    """
    if ctx.obj.get("json"):
        click.echo(json.dumps(data, indent=2, default=str))
    elif human_fn:
        click.echo(human_fn(data))
    else:
        click.echo(json.dumps(data, indent=2, default=str))


def _output_error(ctx: click.Context, message: str) -> None:
    """Output an error message and signal failure to scripts and agents.

    In one-shot mode, exits the process with code 1 after printing so callers
    observe a non-zero exit on failure. In REPL mode (``ctx.obj["repl"]`` is
    truthy), prints and returns so the REPL loop continues. Centralising the
    exit-on-error here keeps per-command try/except blocks simple while still
    propagating failures correctly.
    """
    if ctx.obj.get("json"):
        click.echo(json.dumps({"error": message}))
    else:
        click.echo(f"Error: {message}", err=True)
    if not ctx.obj.get("repl"):
        sys.exit(1)


def _format_table(rows: list, headers: list) -> str:
    """Format a list of dicts/tuples as a simple aligned table."""
    if not rows:
        return "(empty)"

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    str_rows = []
    for row in rows:
        if isinstance(row, dict):
            cells = [str(row.get(h, "")) for h in headers]
        else:
            cells = [str(c) for c in row]
        str_rows.append(cells)
        for i, cell in enumerate(cells):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(cell))

    lines = []
    # Header
    header_line = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    lines.append(header_line)
    lines.append("  ".join("-" * w for w in col_widths))
    # Rows
    for cells in str_rows:
        line = "  ".join(
            cells[i].ljust(col_widths[i]) if i < len(col_widths) else cells[i]
            for i in range(len(cells))
        )
        lines.append(line)

    return "\n".join(lines)


def _format_status_block(data: dict, title: str = "") -> str:
    """Format a dict as a key-value status block."""
    lines = []
    if title:
        lines.append(title)
        lines.append("=" * len(title))
    max_key = max((len(str(k)) for k in data), default=0)
    for key, value in data.items():
        lines.append(f"  {str(key).ljust(max_key)}  {value}")
    return "\n".join(lines)


def _resolve_project_path(ctx: click.Context) -> Optional[str]:
    """Resolve the project directory from --project or cwd.

    Returns the .sbproj file path, or None if not found.
    """
    project_path = ctx.obj.get("project_path")
    if project_path:
        # If it is a directory, find the .sbproj inside
        if os.path.isdir(project_path):
            return project_mod.find_sbproj(project_path)
        # If it is a file, assume it is the .sbproj
        if os.path.isfile(project_path):
            return project_path
        return None
    # Auto-detect from cwd
    proj_dir = export_mod.find_project_dir(os.getcwd())
    if proj_dir:
        return project_mod.find_sbproj(proj_dir)
    return None


def _resolve_project_dir(ctx: click.Context) -> Optional[str]:
    """Resolve the project directory from --project or cwd."""
    project_path = ctx.obj.get("project_path")
    if project_path:
        if os.path.isdir(project_path):
            return project_path
        if os.path.isfile(project_path):
            return os.path.dirname(project_path)
        return None
    return export_mod.find_project_dir(os.getcwd())


def _resolve_input_config(ctx: click.Context, config_path: Optional[str] = None) -> str:
    """Resolve the Input.config path from explicit arg, --project, or cwd."""
    if config_path:
        return config_path
    proj_dir = _resolve_project_dir(ctx)
    if proj_dir:
        return os.path.join(proj_dir, "ProjectSettings", "Input.config")
    raise click.ClickException(
        "No project found. Use --project or run from a project directory."
    )
