# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestDAPProtocolMixin0:
    def test_encode_and_read_message(self):
        from cli_anything.lldb.dap import encode_message, read_message

        payload = {"seq": 1, "type": "request", "command": "initialize"}
        stream = io.BytesIO(encode_message(payload))

        assert read_message(stream) == payload
        assert read_message(stream) is None
    def test_read_message_rejects_missing_content_length(self):
        from cli_anything.lldb.dap import DAPProtocolError, read_message

        with pytest.raises(DAPProtocolError, match="Missing Content-Length"):
            read_message(io.BytesIO(b"Header: value\r\n\r\n{}"))
    def test_initialize_capabilities_and_event(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter, encode_message, read_message

        out = io.BytesIO()
        adapter = LLDBDebugAdapter(session_factory=MagicMock())
        adapter.run(
            io.BytesIO(encode_message({"seq": 1, "type": "request", "command": "initialize", "arguments": {}})),
            out,
        )
        out.seek(0)
        response = read_message(out)
        event = read_message(out)

        assert response["success"] is True
        assert response["body"]["supportsConfigurationDoneRequest"] is True
        assert response["body"]["supportsFunctionBreakpoints"] is True
        assert response["body"]["supportsLoadedSourcesRequest"] is True
        assert response["body"]["supportsReadMemoryRequest"] is True
        assert response["body"]["supportsSetVariable"] is True
        assert response["body"]["supportsModulesRequest"] is True
        assert response["body"]["supportsExceptionInfoRequest"] is True
        assert event["event"] == "initialized"
    def test_variable_references_reset_on_resume(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter

        adapter = LLDBDebugAdapter(session_factory=MagicMock())
        frame_ref = adapter._alloc_frame_ref(1, 0)
        variable_ref = adapter._alloc_variable_ref({"kind": "locals", "frame_ref": frame_ref})

        adapter._reset_refs_for_resume()

        assert frame_ref not in adapter._frame_refs
        assert variable_ref not in adapter._variable_refs
    def test_run_cleans_up_session_on_eof(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter

        fake_session = MagicMock()
        adapter = LLDBDebugAdapter(session_factory=lambda: fake_session)
        adapter._ensure_session()

        result = adapter.run(io.BytesIO(), io.BytesIO())

        assert result == 0
        fake_session.destroy.assert_called_once()
        assert adapter._session is None
    def test_running_state_emits_continued_not_stopped(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter, read_message

        fake_session = MagicMock()
        fake_session.process_info.return_value = {
            "state": "running",
            "selected_thread_id": 99,
            "stop": None,
            "exit_status": 0,
        }
        out = io.BytesIO()
        adapter = LLDBDebugAdapter(session_factory=lambda: fake_session)
        adapter._out = out
        adapter._ensure_session()

        adapter._emit_execution_event(default_reason="breakpoint")
        out.seek(0)
        event = read_message(out)

        assert event["event"] == "continued"
        assert event["body"]["threadId"] == 99
