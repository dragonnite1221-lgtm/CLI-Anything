# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestDAPProtocolMixin1:
    def test_pause_request_interrupts_process_and_reports_stop(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter, read_message

        fake_session = MagicMock()
        fake_session.process_info.return_value = {
            "state": "stopped",
            "selected_thread_id": 99,
            "stop": {"reason": None, "description": None, "hit_breakpoint_ids": []},
            "exit_status": 0,
        }
        out = io.BytesIO()
        adapter = LLDBDebugAdapter(session_factory=lambda: fake_session)
        adapter.run(
            io.BytesIO(
                b"".join(
                    [
                        __import__("cli_anything.lldb.dap", fromlist=["encode_message"]).encode_message(
                            {"seq": 1, "type": "request", "command": "pause", "arguments": {"threadId": 99}}
                        )
                    ]
                )
            ),
            out,
        )
        out.seek(0)
        response = read_message(out)
        event = read_message(out)

        assert response["success"] is True
        assert event["event"] == "stopped"
        assert event["body"]["reason"] == "pause"
        assert event["body"]["cliAnythingStop"]["origin"] == "manualPause"
        fake_session.interrupt_async.assert_called_once()
    def test_set_breakpoints_interrupts_active_continue_before_mutation(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter

        fake_session = MagicMock()
        fake_session.breakpoint_set.return_value = {
            "id": 7,
            "resolved": True,
            "locations": 1,
            "location_details": [{"file": "C:/tmp/main.c", "line": 12}],
        }
        adapter = LLDBDebugAdapter(session_factory=lambda: fake_session)
        adapter._ensure_session()
        adapter._mutation_stop_timeout = 1.0
        with adapter._continue_state:
            adapter._continue_active = True

        release = threading.Timer(0.01, adapter._mark_continue_inactive)
        release.start()
        try:
            body, post_send = adapter._handle_setBreakpoints(
                {
                    "source": {"path": "C:/tmp/main.c"},
                    "breakpoints": [{"line": 12}],
                }
            )
        finally:
            release.join()

        assert post_send is None
        assert body["breakpoints"][0]["verified"] is True
        fake_session.interrupt_async.assert_called_once()
        fake_session.breakpoint_set.assert_called_once()
    def test_set_breakpoints_reports_timeout_if_running_target_will_not_stop(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter

        fake_session = MagicMock()
        adapter = LLDBDebugAdapter(session_factory=lambda: fake_session)
        adapter._ensure_session()
        adapter._mutation_stop_timeout = 0.01
        with adapter._continue_state:
            adapter._continue_active = True

        try:
            with pytest.raises(RuntimeError, match="Timed out waiting for debuggee to stop"):
                adapter._handle_setBreakpoints(
                    {
                        "source": {"path": "C:/tmp/main.c"},
                        "breakpoints": [{"line": 12}],
                    }
                )
        finally:
            adapter._mark_continue_inactive()

        fake_session.interrupt_async.assert_called_once()
        fake_session.breakpoint_set.assert_not_called()
