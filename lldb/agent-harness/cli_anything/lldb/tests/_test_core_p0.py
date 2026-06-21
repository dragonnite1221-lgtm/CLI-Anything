# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestOutputUtils:
    def test_output_json(self):
        from cli_anything.lldb.utils.output import output_json
        import io

        buf = io.StringIO()
        output_json({"ok": True, "value": 42}, file=buf)
        data = json.loads(buf.getvalue())
        assert data["ok"] is True
        assert data["value"] == 42

    def test_output_table(self):
        from cli_anything.lldb.utils.output import output_table
        import io

        buf = io.StringIO()
        output_table([["main", 1], ["worker", 2]], ["thread", "id"], file=buf)
        text = buf.getvalue()
        assert "main" in text
        assert "worker" in text

    def test_output_table_empty(self):
        from cli_anything.lldb.utils.output import output_table
        import io

        buf = io.StringIO()
        output_table([], ["col"], file=buf)
        assert "(no data)" in buf.getvalue()


class TestErrorUtils:
    def test_handle_error(self):
        from cli_anything.lldb.utils.errors import handle_error

        result = handle_error(ValueError("bad"))
        assert result["error"] == "bad"
        assert result["type"] == "ValueError"
        assert "traceback" not in result

    def test_handle_error_debug(self):
        from cli_anything.lldb.utils.errors import handle_error

        try:
            raise RuntimeError("boom")
        except RuntimeError as exc:
            result = handle_error(exc, debug=True)
        assert "traceback" in result
        assert "boom" in result["traceback"]


class TestCoreHelpers:
    def test_breakpoints_wrapper(self):
        from cli_anything.lldb.core.breakpoints import set_breakpoint

        session = MagicMock()
        session.breakpoint_set.return_value = {"id": 1}
        data = set_breakpoint(session, function="main", allow_pending=True)
        assert data["id"] == 1
        session.breakpoint_set.assert_called_once_with(
            file=None,
            line=None,
            function="main",
            condition=None,
            allow_pending=True,
        )

    def test_inspect_wrapper(self):
        from cli_anything.lldb.core.inspect import evaluate_expression

        session = MagicMock()
        session.evaluate.return_value = {"expression": "1+1", "value": "2"}
        data = evaluate_expression(session, "1+1")
        assert data["value"] == "2"

    def test_threads_wrapper(self):
        from cli_anything.lldb.core.threads import list_threads

        session = MagicMock()
        session.threads.return_value = {"threads": []}
        data = list_threads(session)
        assert "threads" in data


class TestCLIHelp:
    def test_main_help(self):
        from cli_anything.lldb.lldb_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "LLDB CLI" in result.output

    def test_groups_help(self):
        from cli_anything.lldb.lldb_cli import cli

        runner = CliRunner()
        for group in ("target", "process", "breakpoint", "thread", "frame", "step", "memory", "core", "session"):
            result = runner.invoke(cli, [group, "--help"])
            assert result.exit_code == 0, f"{group} help failed"
