"""Message, status, table, help, and I/O helpers for the REPL skin.

Mixin split out of the original ``repl_skin`` module without behavior
changes.
"""

import sys

from ._const import (
    _BOLD, _BLUE, _CYAN, _DARK_GRAY, _GRAY, _GREEN, _H_LINE, _ICON_SMALL,
    _LIGHT_GRAY, _RED, _V_LINE, _WHITE, _YELLOW,
)


class _IOMixin:
    """Message / status / table / help methods for :class:`ReplSkin`."""

    # ── Messages ──────────────────────────────────────────────────────

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

    def table(self, headers: list[str], rows: list[list[str]],
              max_col_width: int = 40):
        """Print a formatted table with box-drawing characters.

        Args:
            headers: Column header strings.
            rows: List of rows, each a list of cell strings.
            max_col_width: Maximum column width before truncation.
        """
        if not headers:
            return

        # Calculate column widths
        col_widths = [min(len(h), max_col_width) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = min(
                        max(col_widths[i], len(str(cell))), max_col_width
                    )

        def pad(text: str, width: int) -> str:
            t = str(text)[:width]
            return t + " " * (width - len(t))

        # Header
        header_cells = [
            self._c(_CYAN + _BOLD, pad(h, col_widths[i]))
            for i, h in enumerate(headers)
        ]
        sep = self._c(_DARK_GRAY, f" {_V_LINE} ")
        header_line = f"  {sep.join(header_cells)}"
        print(header_line)

        # Separator
        sep_parts = [self._c(_DARK_GRAY, _H_LINE * w) for w in col_widths]
        sep_line = self._c(_DARK_GRAY, f"  {'───'.join([_H_LINE * w for w in col_widths])}")
        print(sep_line)

        # Rows
        for row in rows:
            cells = []
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    cells.append(self._c(_LIGHT_GRAY, pad(str(cell), col_widths[i])))
            row_sep = self._c(_DARK_GRAY, f" {_V_LINE} ")
            print(f"  {row_sep.join(cells)}")

    # ── Help display ──────────────────────────────────────────────────

    def help(self, commands: dict[str, str]):
        """Print a formatted help listing.

        Args:
            commands: Dict of command -> description pairs.
        """
        self.section("Commands")
        max_cmd = max(len(c) for c in commands) if commands else 0
        for cmd, desc in commands.items():
            cmd_styled = self._c(self.accent, f"  {cmd:<{max_cmd}}")
            desc_styled = self._c(_GRAY, f"  {desc}")
            print(f"{cmd_styled}{desc_styled}")
        print()

    # ── Goodbye ───────────────────────────────────────────────────────

    def print_goodbye(self):
        """Print a styled goodbye message."""
        print(f"\n  {_ICON_SMALL} {self._c(_GRAY, 'Goodbye!')}\n")
