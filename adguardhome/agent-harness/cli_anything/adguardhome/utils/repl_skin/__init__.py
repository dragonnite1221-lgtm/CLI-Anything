"""cli-anything REPL Skin — Unified terminal interface for all CLI harnesses.

Copy this package into your CLI package at:
    cli_anything/<software>/utils/repl_skin/

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

The implementation is split across sibling modules for maintainability;
the public ``ReplSkin`` name is preserved here for backward compatibility.
"""

import os
import sys
from pathlib import Path

from ._banner import _BannerMixin
from ._const import (
    _ACCENT_COLORS, _DEFAULT_ACCENT, _RESET, _SKILL_SOURCE_REPO,
)
from ._io import _IOMixin
from ._session import _SessionMixin

__all__ = ["ReplSkin"]


class ReplSkin(_BannerMixin, _IOMixin, _SessionMixin):
    """Unified REPL skin for cli-anything CLIs.

    Provides consistent branding, prompts, and message formatting
    across all CLI harnesses built with the cli-anything methodology.
    """

    def __init__(self, software: str, version: str = "1.0.0",
                 history_file: str | None = None, skill_path: str | None = None):
        """Initialize the REPL skin.

        Args:
            software: Software name (e.g., "gimp", "shotcut", "blender").
            version: CLI version string.
            history_file: Path for persistent command history.
                         Defaults to ~/.cli-anything-<software>/history
            skill_path: Path to the SKILL.md file for agent discovery.
                        Auto-detected from the repo-root skills/ tree when present,
                        otherwise from the package's skills/ directory.
                        Displayed in banner for AI agents to know where to read skill info.
        """
        self.software = software.lower().replace("-", "_")
        self.display_name = software.replace("_", " ").title()
        self.version = version
        software_aliases = {"iterm2_ctl": "iterm2"}
        self.skill_slug = software_aliases.get(self.software, self.software).replace("_", "-")
        self.skill_id = f"cli-anything-{self.skill_slug}"
        self.skill_install_cmd = (
            f"npx skills add {_SKILL_SOURCE_REPO} --skill {self.skill_id} -g -y"
        )
        global_skill_root = Path(
            os.environ.get("CLI_ANYTHING_GLOBAL_SKILLS_DIR", str(Path.home() / ".agents" / "skills"))
        ).expanduser()
        self.global_skill_path = str(global_skill_root / self.skill_id / "SKILL.md")

        # Prefer repo-root canonical skills/<skill-id>/SKILL.md when running
        # inside the CLI-Anything monorepo. Fall back to the packaged
        # cli_anything/<software>/skills/SKILL.md for installed harnesses.
        if skill_path is None:
            package_skill = Path(__file__).resolve().parent.parent.parent / "skills" / "SKILL.md"
            repo_skill = None
            for parent in Path(__file__).resolve().parents:
                candidate = parent / "skills" / self.skill_id / "SKILL.md"
                if candidate.is_file():
                    repo_skill = candidate
                    break
            if repo_skill and repo_skill.is_file():
                skill_path = str(repo_skill)
            elif package_skill.is_file():
                skill_path = str(package_skill)
        self.skill_path = skill_path
        self.accent = _ACCENT_COLORS.get(self.software, _DEFAULT_ACCENT)

        # History file
        if history_file is None:
            hist_dir = Path.home() / f".cli-anything-{self.software}"
            hist_dir.mkdir(parents=True, exist_ok=True)
            self.history_file = str(hist_dir / "history")
        else:
            self.history_file = history_file

        # Detect terminal capabilities
        self._color = self._detect_color_support()

    def _detect_color_support(self) -> bool:
        """Check if terminal supports color."""
        if os.environ.get("NO_COLOR"):
            return False
        if os.environ.get("CLI_ANYTHING_NO_COLOR"):
            return False
        if not hasattr(sys.stdout, "isatty"):
            return False
        return sys.stdout.isatty()

    def _c(self, code: str, text: str) -> str:
        """Apply color code if colors are supported."""
        if not self._color:
            return text
        return f"{code}{text}{_RESET}"
