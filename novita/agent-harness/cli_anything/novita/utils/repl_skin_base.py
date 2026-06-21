# ruff: noqa: F403, F405, E501
"""cli-anything REPL Skin — Unified terminal interface for all CLI harnesses.

Copy this file into your CLI package at:
    cli_anything/<software>/utils/repl_skin.py

Usage:
    from cli_anything.<software>.utils.repl_skin import ReplSkin

    skin = ReplSkin("shotcut", version="1.0.0")
    skin.print_banner()  # auto-detects repo-root or packaged SKILL.md
    prompt_text = skin.prompt(project_name="my_video.mlt", modified=True)
    skin.success("Project saved")
    skin.error("File not found")
    skin.warning("Unsaved changes")
    skin.info("Processing 24 clips...")
    skin.status("Track 1", "3 clips, 00:02:30")
    skin.table(headers, rows)
    skin.print_goodbye()
"""

import os
import sys
from pathlib import Path


_RESET = "\033[0m"


_BOLD = "\033[1m"


_DIM = "\033[2m"


_ITALIC = "\033[3m"


_UNDERLINE = "\033[4m"


_CYAN = "\033[38;5;80m"  # cli-anything brand cyan


_CYAN_BG = "\033[48;5;80m"


_WHITE = "\033[97m"


_GRAY = "\033[38;5;245m"


_DARK_GRAY = "\033[38;5;240m"


_LIGHT_GRAY = "\033[38;5;250m"


_ACCENT_COLORS = {
    "gimp": "\033[38;5;214m", # warm orange
    "blender": "\033[38;5;208m", # deep orange
    "inkscape": "\033[38;5;39m", # bright blue
    "audacity": "\033[38;5;33m", # navy blue
    "libreoffice": "\033[38;5;40m", # green
    "obs_studio": "\033[38;5;55m", # purple
    "kdenlive": "\033[38;5;69m", # slate blue
    "shotcut": "\033[38;5;35m", # teal green
}


_DEFAULT_ACCENT = "\033[38;5;75m"  # default sky blue


_GREEN = "\033[38;5;78m"


_YELLOW = "\033[38;5;220m"


_RED = "\033[38;5;196m"


_BLUE = "\033[38;5;75m"


_MAGENTA = "\033[38;5;176m"


_SKILL_SOURCE_REPO = os.environ.get("CLI_ANYTHING_SKILL_REPO", "HKUDS/CLI-Anything")


_ICON = f"{_CYAN}{_BOLD}◆{_RESET}"


_ICON_SMALL = f"{_CYAN}▸{_RESET}"


_H_LINE = "─"


_V_LINE = "│"


_TL = "╭"


_TR = "╮"


_BL = "╰"


_BR = "╯"


_T_DOWN = "┬"


_T_UP = "┴"


_T_RIGHT = "├"


_T_LEFT = "┤"


_CROSS = "┼"


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
    "\033[38;5;33m": "#0087ff", # audacity navy blue
    "\033[38;5;35m": "#00af5f", # shotcut teal
    "\033[38;5;39m": "#00afff", # inkscape bright blue
    "\033[38;5;40m": "#00d700", # libreoffice green
    "\033[38;5;55m": "#5f00af", # obs purple
    "\033[38;5;69m": "#5f87ff", # kdenlive slate blue
    "\033[38;5;75m": "#5fafff", # default sky blue
    "\033[38;5;80m": "#5fd7d7", # brand cyan
    "\033[38;5;208m": "#ff8700", # blender deep orange
    "\033[38;5;214m": "#ffaf00", # gimp warm orange
}


# fmt: off
__all__ = ['Path', '_ACCENT_COLORS', '_ANSI_256_TO_HEX', '_BL', '_BLUE', '_BOLD', '_BR', '_CROSS', '_CYAN', '_CYAN_BG', '_DARK_GRAY', '_DEFAULT_ACCENT', '_DIM', '_GRAY', '_GREEN', '_H_LINE', '_ICON', '_ICON_SMALL', '_ITALIC', '_LIGHT_GRAY', '_MAGENTA', '_RED', '_RESET', '_SKILL_SOURCE_REPO', '_TL', '_TR', '_T_DOWN', '_T_LEFT', '_T_RIGHT', '_T_UP', '_UNDERLINE', '_V_LINE', '_WHITE', '_YELLOW', '_display_home_path', '_strip_ansi', '_visible_len', 'os', 'sys']  # noqa: E501
# fmt: on
