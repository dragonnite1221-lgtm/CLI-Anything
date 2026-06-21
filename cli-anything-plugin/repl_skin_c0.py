# ruff: noqa: F403, F405, E501
from .repl_skin_base import *  # noqa: F403


class ReplSkinMixin0:
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
    def print_banner(self):
        """Print the startup banner with branding."""
        import textwrap

        inner = 72

        def _box_line(content: str) -> str:
            """Wrap content in box drawing, padding to inner width."""
            pad = inner - _visible_len(content)
            vl = self._c(_DARK_GRAY, _V_LINE)
            return f"{vl}{content}{' ' * max(0, pad)}{vl}"

        def _meta_lines(label: str, value: str) -> list[str]:
            """Wrap a metadata line for the banner box."""
            icon = self._c(_MAGENTA, "◇")
            label_text = self._c(_DARK_GRAY, label)
            prefix = f" {icon} {label_text} "
            available = max(12, inner - _visible_len(prefix))
            wrapped = textwrap.wrap(
                value,
                width=available,
                break_long_words=True,
                break_on_hyphens=False,
            ) or [""]
            lines = [f"{prefix}{self._c(_LIGHT_GRAY, wrapped[0])}"]
            continuation_prefix = " " * _visible_len(prefix)
            for chunk in wrapped[1:]:
                lines.append(f"{continuation_prefix}{self._c(_LIGHT_GRAY, chunk)}")
            return lines

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

        meta_lines: list[str] = []
        meta_lines.extend(_meta_lines("Install:", self.skill_install_cmd))
        meta_lines.extend(_meta_lines("Global skill:", _display_home_path(self.global_skill_path)))
        print(top)
        print(_box_line(title))
        print(_box_line(ver))
        for line in meta_lines:
            print(_box_line(line))
        print(_box_line(empty))
        print(_box_line(tip))
        print(bot)
        print()
