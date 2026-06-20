"""ReplSkin message/status mixin (behavior-preserving split)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from repl_skin_const import (  # noqa: E402
    _BOLD, _CYAN, _WHITE, _GRAY, _DARK_GRAY, _LIGHT_GRAY, _GREEN, _YELLOW, _RED, _BLUE,
    _H_LINE,
)


class _ReplSkinIO:
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

    # ── Status display ────────────────────────────────────────────────

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

    # ── Table display ─────────────────────────────────────────────────
