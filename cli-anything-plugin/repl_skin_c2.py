# ruff: noqa: F403, F405, E501
from .repl_skin_base import *  # noqa: F403


class ReplSkinMixin2:
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
    def print_goodbye(self):
        """Print a styled goodbye message."""
        print(f"\n  {_ICON_SMALL} {self._c(_GRAY, 'Goodbye!')}\n")
    def create_prompt_session(self):
        """Create a prompt_toolkit PromptSession with skin styling.

        Returns:
            A configured PromptSession, or None if prompt_toolkit unavailable.
        """
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.history import FileHistory
            from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
            from prompt_toolkit.formatted_text import FormattedText

            style = self.get_prompt_style()

            session = PromptSession(
                history=FileHistory(self.history_file),
                auto_suggest=AutoSuggestFromHistory(),
                style=style,
                enable_history_search=True,
            )
            return session
        except ImportError:
            return None
    def get_input(self, pt_session, project_name: str = "",
                  modified: bool = False, context: str = "") -> str:
        """Get input from user using prompt_toolkit or fallback.

        Args:
            pt_session: A prompt_toolkit PromptSession (or None).
            project_name: Current project name.
            modified: Whether project has unsaved changes.
            context: Optional context string.

        Returns:
            User input string (stripped).
        """
        if pt_session is not None:
            from prompt_toolkit.formatted_text import FormattedText
            tokens = self.prompt_tokens(project_name, modified, context)
            return pt_session.prompt(FormattedText(tokens)).strip()
        else:
            raw_prompt = self.prompt(project_name, modified, context)
            return input(raw_prompt).strip()
    def bottom_toolbar(self, items: dict[str, str]):
        """Create a bottom toolbar callback for prompt_toolkit.

        Args:
            items: Dict of label -> value pairs to show in toolbar.

        Returns:
            A callable that returns FormattedText for the toolbar.
        """
        def toolbar():
            from prompt_toolkit.formatted_text import FormattedText
            parts = []
            for i, (k, v) in enumerate(items.items()):
                if i > 0:
                    parts.append(("class:bottom-toolbar.text", "  │  "))
                parts.append(("class:bottom-toolbar.text", f" {k}: "))
                parts.append(("class:bottom-toolbar", v))
            return FormattedText(parts)
        return toolbar
