# ruff: noqa: F403, F405, E501
from .repl_skin_base import *  # noqa: F403


class ReplSkinMixin3:
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

    def get_input(
        self,
        pt_session,
        project_name: str = "",
        modified: bool = False,
        context: str = "",
    ) -> str:
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
