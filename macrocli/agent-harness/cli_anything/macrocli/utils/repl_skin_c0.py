# ruff: noqa: F403, F405, E501
from .repl_skin_base import *  # noqa: F403


class ReplSkinMixin0:
    """Unified REPL skin for cli-anything CLIs.

    Provides consistent branding, prompts, and message formatting
    across all CLI harnesses built with the cli-anything methodology.
    """

    def __init__(
        self,
        software: str,
        version: str = "1.0.0",
        history_file: str | None = None,
        skill_path: str | None = None,
    ):
        """Initialize the REPL skin.

        Args:
            software: Software name (e.g., "gimp", "shotcut", "blender").
            version: CLI version string.
            history_file: Path for persistent command history.
                         Defaults to ~/.cli-anything-<software>/history
            skill_path: Path to the SKILL.md file for agent discovery.
                        Auto-detected from the package's skills/ directory if not provided.
                        Displayed in banner for AI agents to know where to read skill info.
        """
        self.software = software.lower().replace("-", "_")
        self.display_name = software.replace("_", " ").title()
        self.version = version

        # Auto-detect skill path from package layout:
        #   cli_anything/<software>/utils/repl_skin.py  (this file)
        #   cli_anything/<software>/skills/SKILL.md     (target)
        if skill_path is None:
            from pathlib import Path

            _auto = Path(__file__).resolve().parent.parent / "skills" / "SKILL.md"
            if _auto.is_file():
                skill_path = str(_auto)
        self.skill_path = skill_path
        self.accent = _ACCENT_COLORS.get(self.software, _DEFAULT_ACCENT)

        # History file
        if history_file is None:
            from pathlib import Path

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

    def print_banner(self):
        """Print the startup banner with branding."""
        inner = 54

        def _box_line(content: str) -> str:
            """Wrap content in box drawing, padding to inner width."""
            pad = inner - _visible_len(content)
            vl = self._c(_DARK_GRAY, _V_LINE)
            return f"{vl}{content}{' ' * max(0, pad)}{vl}"

        top = self._c(_DARK_GRAY, f"{_TL}{_H_LINE * inner}{_TR}")
        bot = self._c(_DARK_GRAY, f"{_BL}{_H_LINE * inner}{_BR}")

        # Title:  ◆  cli-anything · Shotcut
        icon = self._c(_CYAN + _BOLD, "◆")
        brand = self._c(_CYAN + _BOLD, "cli-anything")
        dot = self._c(_DARK_GRAY, "·")
        name = self._c(self.accent + _BOLD, self.display_name)
        title = f" {icon}  {brand} {dot} {name}"

        ver = f" {self._c(_DARK_GRAY, f'   v{self.version}')}"
        tip = f" {self._c(_DARK_GRAY, '   Type help for commands, quit to exit')}"
        empty = ""

        # Skill path for agent discovery
        skill_line = None
        if self.skill_path:
            skill_icon = self._c(_MAGENTA, "◇")
            skill_label = self._c(_DARK_GRAY, "   Skill:")
            skill_path_display = self._c(_LIGHT_GRAY, self.skill_path)
            skill_line = f" {skill_icon} {skill_label} {skill_path_display}"

        print(top)
        print(_box_line(title))
        print(_box_line(ver))
        if skill_line:
            print(_box_line(skill_line))
        print(_box_line(empty))
        print(_box_line(tip))
        print(bot)
        print()
