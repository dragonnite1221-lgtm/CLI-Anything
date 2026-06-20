"""Banner and prompt methods for the cli-anything REPL skin.

Provides ``_ReplSkinMethods``, one of the mixins consumed by ``ReplSkin`` in
``repl_skin.py``. Split out to keep modules within the 200-line gate.
"""

from .repl_skin_lib import (
    _ANSI_256_TO_HEX,
    _BOLD,
    _CYAN,
    _DARK_GRAY,
    _GRAY,
    _H_LINE,
    _LIGHT_GRAY,
    _MAGENTA,
    _RESET,
    _TL,
    _TR,
    _BL,
    _BR,
    _V_LINE,
    _display_home_path,
    _visible_len,
)


class _ReplSkinMethods:
    """Banner/prompt rendering mixin for ``ReplSkin``."""

    # ── Banner ────────────────────────────────────────────────────────

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

    # ── Prompt ────────────────────────────────────────────────────────

    def prompt(self, project_name: str = "", modified: bool = False,
               context: str = "") -> str:
        """Build a styled prompt string for prompt_toolkit or input()."""
        parts = []

        # Icon
        if self._color:
            parts.append(f"{_CYAN}◆{_RESET} ")
        else:
            parts.append("> ")

        # Software name
        parts.append(self._c(self.accent + _BOLD, self.software))

        # Project context
        if project_name or context:
            ctx = context or project_name
            mod = "*" if modified else ""
            parts.append(f" {self._c(_DARK_GRAY, '[')}")
            parts.append(self._c(_LIGHT_GRAY, f"{ctx}{mod}"))
            parts.append(self._c(_DARK_GRAY, ']'))

        parts.append(self._c(_GRAY, " ❯ "))

        return "".join(parts)

    def prompt_tokens(self, project_name: str = "", modified: bool = False,
                      context: str = ""):
        """Build prompt_toolkit formatted text tokens for the prompt."""
        accent_hex = _ANSI_256_TO_HEX.get(self.accent, "#5fafff")
        tokens = []

        tokens.append(("class:icon", "◆ "))
        tokens.append(("class:software", self.software))

        if project_name or context:
            ctx = context or project_name
            mod = "*" if modified else ""
            tokens.append(("class:bracket", " ["))
            tokens.append(("class:context", f"{ctx}{mod}"))
            tokens.append(("class:bracket", "]"))

        tokens.append(("class:arrow", " ❯ "))

        return tokens

    def get_prompt_style(self):
        """Get a prompt_toolkit Style object matching the skin."""
        try:
            from prompt_toolkit.styles import Style
        except ImportError:
            return None

        accent_hex = _ANSI_256_TO_HEX.get(self.accent, "#5fafff")

        return Style.from_dict({
            "icon": "#5fdfdf bold",     # cyan brand color
            "software": f"{accent_hex} bold",
            "bracket": "#585858",
            "context": "#bcbcbc",
            "arrow": "#808080",
            # Completion menu
            "completion-menu.completion": "bg:#303030 #bcbcbc",
            "completion-menu.completion.current": f"bg:{accent_hex} #000000",
            "completion-menu.meta.completion": "bg:#303030 #808080",
            "completion-menu.meta.completion.current": f"bg:{accent_hex} #000000",
            # Auto-suggest
            "auto-suggest": "#585858",
            # Bottom toolbar
            "bottom-toolbar": "bg:#1c1c1c #808080",
            "bottom-toolbar.text": "#808080",
        })
