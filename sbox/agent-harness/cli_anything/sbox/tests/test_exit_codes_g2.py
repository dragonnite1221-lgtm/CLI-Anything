# ruff: noqa: F403, F405, E501
from .test_exit_codes_helpers import *  # noqa: F403


class TestReplModeAbsorbsExit:
    """Direct unit tests on _output_error to prove REPL mode doesn't exit.

    These tests don't go through the interactive REPL loop because the
    upstream-shared repl_skin uses unicode glyphs (e.g. ●) that fail to
    encode on Windows cp1252 console when stdin is piped, which is unrelated
    to the exit-code contract under test.
    """

    def test_output_error_does_not_exit_in_repl_mode(self):
        from click import Context
        from cli_anything.sbox import sbox_cli

        ctx = Context(sbox_cli.cli)
        ctx.obj = {"json": False, "repl": True}
        # Must NOT raise SystemExit when repl flag is set.
        sbox_cli._output_error(ctx, "test error")

    def test_output_error_exits_in_oneshot_mode(self):
        from click import Context
        from cli_anything.sbox import sbox_cli

        ctx = Context(sbox_cli.cli)
        ctx.obj = {"json": False, "repl": False}
        with pytest.raises(SystemExit) as exc_info:
            sbox_cli._output_error(ctx, "test error")
        assert exc_info.value.code == 1

    def test_output_error_exits_when_repl_key_missing(self):
        """Defaulting to one-shot when repl flag absent matches the contract."""
        from click import Context
        from cli_anything.sbox import sbox_cli

        ctx = Context(sbox_cli.cli)
        ctx.obj = {"json": False}  # no 'repl' key
        with pytest.raises(SystemExit) as exc_info:
            sbox_cli._output_error(ctx, "test error")
        assert exc_info.value.code == 1
