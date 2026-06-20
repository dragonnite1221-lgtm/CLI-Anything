"""cli-anything REPL Skin facade (public ReplSkin entrypoint).

Constants live in repl_skin_const; method bodies in repl_skin_banner,
repl_skin_io, and repl_skin_table. Public import path is unchanged:
    from ...utils.repl_skin import ReplSkin
"""

import os  # noqa: F401
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from repl_skin_const import (  # noqa: E402
    _RESET, _BOLD, _DIM, _ITALIC, _UNDERLINE, _CYAN, _CYAN_BG, _WHITE, _GRAY, _DARK_GRAY,
    _LIGHT_GRAY, _ACCENT_COLORS, _DEFAULT_ACCENT, _GREEN, _YELLOW, _RED, _BLUE, _MAGENTA,
    _SKILL_SOURCE_REPO, _ICON, _ICON_SMALL, _H_LINE, _V_LINE, _TL, _TR, _BL, _BR, _T_DOWN,
    _T_UP, _T_RIGHT, _T_LEFT, _CROSS, _strip_ansi, _visible_len, _display_home_path,
    _ANSI_256_TO_HEX,
)
from repl_skin_banner import _ReplSkinBanner  # noqa: E402
from repl_skin_io import _ReplSkinIO  # noqa: E402
from repl_skin_table import _ReplSkinTable  # noqa: E402


class ReplSkin(_ReplSkinBanner, _ReplSkinIO, _ReplSkinTable):
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
            package_skill = Path(__file__).resolve().parent.parent / "skills" / "SKILL.md"
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

    # ── Banner ────────────────────────────────────────────────────────
