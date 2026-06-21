# ruff: noqa: F403, F405, E501
from .repl_skin_base_base import *  # noqa: F403


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes for length calculation."""
    import re

    return re.sub(r"\033\[[^m]*m", "", text)


def _visible_len(text: str) -> int:
    """Get visible length of text (excluding ANSI codes)."""
    return len(_strip_ansi(text))


def _display_home_path(path: str) -> str:
    """Display a path relative to the home directory when possible."""
    expanded = Path(path).expanduser().resolve()
    home = Path.home().resolve()
    try:
        relative = expanded.relative_to(home)
        return f"~/{relative.as_posix()}"
    except ValueError:
        return str(expanded)


_ANSI_256_TO_HEX = {
    "\033[38;5;33m": "#0087ff",  # audacity navy blue
    "\033[38;5;35m": "#00af5f",  # shotcut teal
    "\033[38;5;39m": "#00afff",  # inkscape bright blue
    "\033[38;5;40m": "#00d700",  # libreoffice green
    "\033[38;5;55m": "#5f00af",  # obs purple
    "\033[38;5;69m": "#5f87ff",  # kdenlive slate blue
    "\033[38;5;75m": "#5fafff",  # default sky blue
    "\033[38;5;80m": "#5fd7d7",  # brand cyan
    "\033[38;5;203m": "#ff5f5f",  # n8n coral
    "\033[38;5;208m": "#ff8700",  # blender deep orange
    "\033[38;5;214m": "#ffaf00",  # gimp warm orange
}
_skin: ReplSkin | None = None


def _get_skin() -> ReplSkin:
    global _skin
    if _skin is None:
        # Import VERSION lazily to avoid circular imports
        try:
            from cli_anything.n8n.n8n_cli import VERSION
        except ImportError:
            VERSION = "0.0.0"
        _skin = ReplSkin("n8n", version=VERSION)
    return _skin


def print_banner() -> None:
    """Print the cli-anything branded banner."""
    _get_skin().print_banner()


def success(msg: str) -> None:
    """Print a success message."""
    _get_skin().success(msg)


def error(msg: str) -> None:
    """Print an error message."""
    _get_skin().error(msg)


def warn(msg: str) -> None:
    """Print a warning message."""
    _get_skin().warning(msg)


def _print_table(rows: list[dict[str, Any]]) -> None:
    if not rows:
        click.secho("  (empty)", fg="bright_black")
        return

    term_width = shutil.get_terminal_size().columns
    keys = list(rows[0].keys())

    # Filter out overly complex nested fields for table view
    simple_keys = [k for k in keys if not isinstance(rows[0].get(k), (dict, list))]
    if not simple_keys:
        simple_keys = keys[:5]

    col_widths = {k: len(str(k)) for k in simple_keys}
    for row in rows:
        for k in simple_keys:
            val = str(row.get(k, ""))
            col_widths[k] = min(max(col_widths[k], len(val)), 40)

    # Truncate columns if they exceed terminal width
    total = sum(col_widths.values()) + (len(simple_keys) - 1) * 3
    if total > term_width:
        max_col = max(10, term_width // len(simple_keys) - 3)
        col_widths = {k: min(v, max_col) for k, v in col_widths.items()}

    header = " | ".join(
        click.style(k.ljust(col_widths[k])[: col_widths[k]], fg="cyan")
        for k in simple_keys
    )
    click.echo(header)
    click.echo("-+-".join("-" * col_widths[k] for k in simple_keys))

    # Color rules for specific columns
    color_rules = {
        "status": {
            "success": "green",
            "error": "red",
            "running": "bright_yellow",
            "waiting": "cyan",
        },
        "active": {"True": "green", "False": "bright_black"},
    }

    for row in rows:
        vals = []
        for k in simple_keys:
            v = str(row.get(k, ""))
            w = col_widths[k]
            if len(v) > w and w > 3:
                cell = v[: w - 1] + "\u2026"
            else:
                cell = v.ljust(w)[:w]
            # Apply color if column has a rule
            if k in color_rules and v in color_rules[k]:
                cell = click.style(cell, fg=color_rules[k][v])
            vals.append(cell)
        click.echo(" | ".join(vals))
