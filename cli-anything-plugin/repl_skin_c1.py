# ruff: noqa: F403, F405, E501
from .repl_skin_base import *  # noqa: F403


class ReplSkinMixin1:
    def prompt(self, project_name: str = "", modified: bool = False,
               context: str = "") -> str:
        """Build a styled prompt string for prompt_toolkit or input().

        Args:
            project_name: Current project name (empty if none open).
            modified: Whether the project has unsaved changes.
            context: Optional extra context to show in prompt.

        Returns:
            Formatted prompt string.
        """
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
        """Build prompt_toolkit formatted text tokens for the prompt.

        Use with prompt_toolkit's FormattedText for proper ANSI handling.

        Returns:
            list of (style, text) tuples for prompt_toolkit.
        """
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
        """Get a prompt_toolkit Style object matching the skin.

        Returns:
            prompt_toolkit.styles.Style
        """
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
    def success(self, message: str):
        """Print a success message with green checkmark."""
        icon = self._c(_GREEN + _BOLD, "✓")
        print(f"  {icon} {self._c(_GREEN, message)}")
    def error(self, message: str):
        """Print an error message with red cross."""
        icon = self._c(_RED + _BOLD, "✗")
        print(f"  {icon} {self._c(_RED, message)}", file=sys.stderr)
    def warning(self, message: str):
        """Print a warning message with yellow triangle."""
        icon = self._c(_YELLOW + _BOLD, "⚠")
        print(f"  {icon} {self._c(_YELLOW, message)}")
    def info(self, message: str):
        """Print an info message with blue dot."""
        icon = self._c(_BLUE, "●")
        print(f"  {icon} {self._c(_LIGHT_GRAY, message)}")
    def hint(self, message: str):
        """Print a subtle hint message."""
        print(f"  {self._c(_DARK_GRAY, message)}")
    def section(self, title: str):
        """Print a section header."""
        print()
        print(f"  {self._c(self.accent + _BOLD, title)}")
        print(f"  {self._c(_DARK_GRAY, _H_LINE * len(title))}")
    def status(self, label: str, value: str):
        """Print a key-value status line."""
        lbl = self._c(_GRAY, f"  {label}:")
        val = self._c(_WHITE, f" {value}")
        print(f"{lbl}{val}")
    def status_block(self, items: dict[str, str], title: str = ""):
        """Print a block of status key-value pairs.

        Args:
            items: Dict of label -> value pairs.
            title: Optional title for the block.
        """
        if title:
            self.section(title)

        max_key = max(len(k) for k in items) if items else 0
        for label, value in items.items():
            lbl = self._c(_GRAY, f"  {label:<{max_key}}")
            val = self._c(_WHITE, f"  {value}")
            print(f"{lbl}{val}")
    def progress(self, current: int, total: int, label: str = ""):
        """Print a simple progress indicator.

        Args:
            current: Current step number.
            total: Total number of steps.
            label: Optional label for the progress.
        """
        pct = int(current / total * 100) if total > 0 else 0
        bar_width = 20
        filled = int(bar_width * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)
        text = f"  {self._c(_CYAN, bar)} {self._c(_GRAY, f'{pct:3d}%')}"
        if label:
            text += f" {self._c(_LIGHT_GRAY, label)}"
        print(text)
