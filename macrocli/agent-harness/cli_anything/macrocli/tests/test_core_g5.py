# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestExecutionSession:
    def test_record_and_retrieve(self):
        from cli_anything.macrocli.core.session import ExecutionSession, RunRecord

        sess = ExecutionSession(session_id="test_sess")
        rec = RunRecord("m1", {}, True, {}, "", 100.0, ["native_api"], 1)
        sess.record(rec)
        assert sess.last().macro_name == "m1"
        assert len(sess.history()) == 1

    def test_stats(self):
        from cli_anything.macrocli.core.session import ExecutionSession, RunRecord

        sess = ExecutionSession()
        sess.record(RunRecord("m1", {}, True, {}, "", 100.0, [], 1))
        sess.record(RunRecord("m2", {}, False, {}, "err", 50.0, [], 0))
        stats = sess.stats()
        assert stats["total"] == 2
        assert stats["success"] == 1
        assert stats["success_rate"] == 0.5

    def test_save_and_load(self, tmp_path, monkeypatch):
        from cli_anything.macrocli.core import session as sess_mod
        import cli_anything.macrocli.core.session as sess_module

        # Redirect SESSION_DIR to tmp_path
        monkeypatch.setattr(sess_module, "SESSION_DIR", tmp_path)
        from cli_anything.macrocli.core.session import ExecutionSession, RunRecord

        sess = ExecutionSession(session_id="save_test")
        sess.record(RunRecord("m1", {"k": "v"}, True, {}, "", 200.0, ["native_api"], 1))
        sess.save()

        loaded = ExecutionSession.load("save_test")
        assert loaded is not None
        assert loaded.session_id == "save_test"
        assert loaded.last().macro_name == "m1"
