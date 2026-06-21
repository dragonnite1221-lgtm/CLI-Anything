# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestREPLSessionState:
    def test_trace_set_then_info_in_repl(self):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        with patch(
            "cli_anything.unrealinsights.utils.repl_skin.ReplSkin.create_prompt_session",
            return_value=None,
        ):
            runner = CliRunner()
            result = runner.invoke(
                cli,
                input="trace set sample.utrace\ntrace info\nquit\n",
            )
        assert result.exit_code == 0
        assert "sample.utrace" in result.output
