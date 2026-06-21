# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import make_msg  # noqa: F401,E501


class TestListenOutputFile:
    def test_format_live_output_text(self):
        assert _format_live_output_message(make_msg(text="live text"), "text").endswith("live text")

    def test_format_live_output_jsonl(self):
        line = _format_live_output_message(make_msg(text="live json"), "jsonl")
        data = json.loads(line)

        assert data["text"] == "live json"

    def test_open_live_output_file_creates_parent_and_replaces(self, tmp_path):
        path = tmp_path / "nested" / "live.log"

        with _open_live_output_file(str(path), append=False) as f:
            f.write("new\n")

        assert path.read_text(encoding="utf-8") == "new\n"

    def test_open_live_output_file_appends(self, tmp_path):
        path = tmp_path / "nested" / "live.log"

        with _open_live_output_file(str(path), append=False) as f:
            f.write("one\n")
        with _open_live_output_file(str(path), append=True) as f:
            f.write("two\n")

        assert path.read_text(encoding="utf-8") == "one\ntwo\n"


class TestCliDualMode:
    def test_root_invokes_repl_when_no_subcommand(self, monkeypatch):
        called = {}

        def fake_run_repl(ctx, file=None):
            called["ctx"] = ctx
            called["file"] = file

        monkeypatch.setattr(nslogger_cli, "_run_repl", fake_run_repl)

        result = CliRunner().invoke(nslogger_cli.cli, [])

        assert result.exit_code == 0
        assert called["file"] is None
        assert called["ctx"].invoked_subcommand is None

    def test_repl_command_uses_shared_repl_dispatch(self, monkeypatch, tmp_path):
        called = {}
        log_file = tmp_path / "sample.rawnsloggerdata"
        log_file.write_bytes(b"placeholder")

        def fake_run_repl(ctx, file=None):
            called["ctx"] = ctx
            called["file"] = file

        monkeypatch.setattr(nslogger_cli, "_run_repl", fake_run_repl)

        result = CliRunner().invoke(nslogger_cli.cli, ["repl", str(log_file)])

        assert result.exit_code == 0
        assert called["file"] == str(log_file)
        assert called["ctx"].info_name == "repl"
