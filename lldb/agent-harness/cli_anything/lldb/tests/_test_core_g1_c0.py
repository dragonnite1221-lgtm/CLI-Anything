# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestSessionLifecycleMixin0:
    def _make_session(self):
        from cli_anything.lldb.core.session import LLDBSession

        session = object.__new__(LLDBSession)
        session._lldb = MagicMock()
        session._lldb.eStateDetached = 9
        session._lldb.eStateExited = 10
        session.debugger = MagicMock()
        session.target = None
        session.process = None
        session._process_origin = None
        return session
    def test_destroy_detaches_attached_process(self):
        from cli_anything.lldb.core.session import LLDBSession

        session = self._make_session()
        process = MagicMock()
        process.IsValid.return_value = True
        session.process = process
        session._process_origin = "attached"

        LLDBSession.destroy(session)

        process.Detach.assert_called_once()
        process.Kill.assert_not_called()
        session._lldb.SBDebugger.Destroy.assert_called_once_with(session.debugger)
        session._lldb.SBDebugger.Terminate.assert_called_once()
    def test_destroy_kills_launched_process(self):
        from cli_anything.lldb.core.session import LLDBSession

        session = self._make_session()
        process = MagicMock()
        process.IsValid.return_value = True
        process.GetState.return_value = 5
        session.process = process
        session._process_origin = "launched"

        LLDBSession.destroy(session)

        process.Kill.assert_called_once()
        process.Detach.assert_not_called()
    def test_interrupt_stops_process(self):
        from cli_anything.lldb.core.session import LLDBSession

        session = self._make_session()
        process = MagicMock()
        process.IsValid.return_value = True
        process.Stop.return_value = MagicMock()
        process.Stop.return_value.Success.return_value = True
        process.GetState.return_value = 5
        process.GetSelectedThread.return_value = None
        process.GetProcessID.return_value = 123
        process.GetNumThreads.return_value = 0
        process.GetExitStatus.return_value = 0
        session.process = process

        payload = LLDBSession.interrupt(session)

        process.Stop.assert_called_once()
        assert payload["pid"] == 123
    def test_interrupt_async_requests_async_interrupt(self):
        from cli_anything.lldb.core.session import LLDBSession

        session = self._make_session()
        process = MagicMock()
        process.IsValid.return_value = True
        process.SendAsyncInterrupt.return_value = MagicMock(Success=lambda: True)
        session.process = process

        payload = LLDBSession.interrupt_async(session)

        process.SendAsyncInterrupt.assert_called_once()
        assert payload == {"status": "interrupt_requested"}
    def test_session_status_reports_target_and_process(self):
        from cli_anything.lldb.core.session import LLDBSession

        session = self._make_session()
        session.target = MagicMock()
        session.target.IsValid.return_value = True
        session.process = MagicMock()
        session.process.IsValid.return_value = True
        session._process_origin = "attached"

        status = LLDBSession.session_status(session)

        assert status["has_target"] is True
        assert status["has_process"] is True
        assert status["process_origin"] == "attached"
    def test_target_create_empty_uses_attach_target(self):
        from cli_anything.lldb.core.session import LLDBSession

        session = self._make_session()
        target = MagicMock()
        target.IsValid.return_value = True
        target.GetTriple.return_value = "x86_64-unknown-linux-gnu"
        session.debugger.CreateTarget.return_value = target

        payload = LLDBSession.target_create_empty(session)

        session.debugger.CreateTarget.assert_called_once_with("")
        assert session.target is target
        assert payload == {
            "executable": None,
            "arch": None,
            "triple": "x86_64-unknown-linux-gnu",
        }
