# ruff: noqa: F403, F405, E501
from .repl_skin_base_base import *  # noqa: F403

# fmt: off
from .repl_skin_base_p1 import _print_table  # noqa: E402,E501
# fmt: on


def _print_dict(d: dict[str, Any], indent: int = 0) -> None:
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.secho(f"{prefix}{k}:", fg="cyan")
            _print_dict(v, indent + 1)
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            click.secho(f"{prefix}{k}:", fg="cyan")
            _print_table(v)
        else:
            click.echo(f"{prefix}{click.style(str(k), fg='cyan')}: {v}")


def output(data: Any, as_json: bool) -> None:
    """Print data as JSON or human-readable."""
    if as_json:
        click.echo(json.dumps(data, indent=2, default=str))
        return

    if isinstance(data, dict):
        if "data" in data and isinstance(data["data"], list):
            _print_table(data["data"])
            if "nextCursor" in data:
                click.secho(f"\n  Next cursor: {data['nextCursor']}", fg="bright_black")
        else:
            _print_dict(data)
    elif isinstance(data, list):
        if data and isinstance(data[0], dict):
            _print_table(data)
        else:
            click.echo(json.dumps(data, indent=2, default=str))
    else:
        click.echo(str(data))


__all__ = [
    "Any",
    "Path",
    "ReplSkin",
    "_ACCENT_COLORS",
    "_ANSI_256_TO_HEX",
    "_BL",
    "_BLUE",
    "_BOLD",
    "_BR",
    "_CROSS",
    "_CYAN",
    "_CYAN_BG",
    "_DARK_GRAY",
    "_DEFAULT_ACCENT",
    "_DIM",
    "_GRAY",
    "_GREEN",
    "_H_LINE",
    "_ICON",
    "_ICON_SMALL",
    "_ITALIC",
    "_LIGHT_GRAY",
    "_MAGENTA",
    "_RED",
    "_RESET",
    "_SKILL_SOURCE_REPO",
    "_TL",
    "_TR",
    "_T_DOWN",
    "_T_LEFT",
    "_T_RIGHT",
    "_T_UP",
    "_UNDERLINE",
    "_V_LINE",
    "_WHITE",
    "_YELLOW",
    "_display_home_path",
    "_get_skin",
    "_print_dict",
    "_print_table",
    "_skin",
    "_strip_ansi",
    "_visible_len",
    "click",
    "error",
    "json",
    "os",
    "output",
    "print_banner",
    "shutil",
    "success",
    "sys",
    "warn",
]
