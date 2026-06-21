# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestSessionLifecycleMixin1:
    def test_process_info_public_wrapper(self):
        from cli_anything.lldb.core.session import LLDBSession

        session = self._make_session()
        process = MagicMock()
        process.IsValid.return_value = True
        process.GetProcessID.return_value = 77
        process.GetState.return_value = 5
        process.GetNumThreads.return_value = 2
        process.GetSelectedThread.return_value = None
        process.GetExitStatus.return_value = 0
        session.process = process

        data = LLDBSession.process_info(session)

        assert data == {
            "pid": 77,
            "state": "stopped",
            "num_threads": 2,
            "selected_thread_id": None,
            "stop": None,
            "exit_status": 0,
        }
    def test_find_memory_scans_in_chunks(self):
        from cli_anything.lldb.core.session import LLDBSession

        session = self._make_session()
        process = MagicMock()
        process.IsValid.return_value = True
        session.process = process

        haystack = b"abcneedlexyz"
        start = 0x1000

        def fake_read_memory(address: int, size: int):
            offset = address - start
            return {"hex": haystack[offset : offset + size].hex()}

        session.read_memory = MagicMock(side_effect=fake_read_memory)

        data = LLDBSession.find_memory(session, "needle", start, len(haystack), chunk_size=5)

        assert data["found"] is True
        assert data["address"] == hex(start + 3)
        assert session.read_memory.call_count >= 2
    def test_find_memory_rejects_oversized_scan(self):
        from cli_anything.lldb.core.session import LLDBSession, MEMORY_FIND_MAX_SCAN_SIZE

        session = self._make_session()
        process = MagicMock()
        process.IsValid.return_value = True
        session.process = process

        with pytest.raises(ValueError) as exc:
            LLDBSession.find_memory(session, "needle", 0x1000, MEMORY_FIND_MAX_SCAN_SIZE + 1)

        assert "max supported scan size" in str(exc.value)
    def test_unresolved_breakpoint_fails_by_default(self):
        from cli_anything.lldb.core.session import LLDBSession

        session = self._make_session()
        session.target = MagicMock()
        session.target.IsValid.return_value = True
        bp = MagicMock()
        bp.IsValid.return_value = True
        bp.GetID.return_value = 7
        bp.GetNumLocations.return_value = 0
        bp.GetHitCount.return_value = 0
        bp.IsEnabled.return_value = True
        bp.GetCondition.return_value = None
        session.target.BreakpointCreateByName.return_value = bp

        with pytest.raises(RuntimeError, match="unresolved"):
            LLDBSession.breakpoint_set(session, function="missing")

        session.target.BreakpointDelete.assert_called_once_with(7)
    def test_pending_breakpoint_returns_resolution_state(self):
        from cli_anything.lldb.core.session import LLDBSession

        session = self._make_session()
        session.target = MagicMock()
        session.target.IsValid.return_value = True
        bp = MagicMock()
        bp.IsValid.return_value = True
        bp.GetID.return_value = 7
        bp.GetNumLocations.return_value = 0
        bp.GetHitCount.return_value = 0
        bp.IsEnabled.return_value = True
        bp.GetCondition.return_value = None
        session.target.BreakpointCreateByName.return_value = bp

        payload = LLDBSession.breakpoint_set(session, function="missing", allow_pending=True)

        assert payload["id"] == 7
        assert payload["resolved"] is False
        assert payload["locations"] == 0
        session.target.BreakpointDelete.assert_not_called()
