# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestDAPProtocolMixin4:
    def test_launch_transcript_keeps_dap_response_event_order(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter, encode_message, read_message

        breakpoint_payload = {
            "id": 1,
            "resolved": True,
            "location_details": [],
            "locations": 1,
        }
        fake_session = MagicMock()
        fake_session.target_create.return_value = {}
        fake_session.breakpoint_set.return_value = breakpoint_payload
        fake_session.breakpoint_list.return_value = {"breakpoints": [breakpoint_payload]}
        fake_session.launch.return_value = {}
        fake_session.process_info.return_value = {
            "state": "stopped",
            "selected_thread_id": 99,
            "stop": {"reason": "breakpoint", "description": "hit breakpoint", "hit_breakpoint_ids": [1]},
            "exit_status": 0,
        }
        messages = [
            {"seq": 1, "type": "request", "command": "initialize", "arguments": {}},
            {"seq": 2, "type": "request", "command": "launch", "arguments": {"program": "app.exe"}},
            {
                "seq": 3,
                "type": "request",
                "command": "setFunctionBreakpoints",
                "arguments": {"breakpoints": [{"name": "main"}]},
            },
            {"seq": 4, "type": "request", "command": "configurationDone", "arguments": {}},
        ]
        out = io.BytesIO()
        adapter = LLDBDebugAdapter(session_factory=lambda: fake_session)
        adapter.run(io.BytesIO(b"".join(encode_message(message) for message in messages)), out)
        out.seek(0)
        transcript = []
        while True:
            message = read_message(out)
            if message is None:
                break
            transcript.append(message)

        labels = [
            item.get("command") if item.get("type") == "response" else item.get("event")
            for item in transcript
        ]
        assert labels == [
            "initialize",
            "initialized",
            "launch",
            "setFunctionBreakpoints",
            "configurationDone",
            "breakpoint",
            "stopped",
        ]
        assert all(item["type"] in {"response", "event"} for item in transcript)
    def test_attach_accepts_process_id_without_program(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter, encode_message, read_message

        fake_session = MagicMock()
        fake_session.target_create_empty.return_value = {"executable": None}
        fake_session.attach_pid.return_value = {}
        fake_session.process_info.return_value = {
            "state": "stopped",
            "selected_thread_id": 77,
            "stop": None,
            "exit_status": 0,
        }
        messages = [
            {"seq": 1, "type": "request", "command": "attach", "arguments": {"processId": 4242}},
            {"seq": 2, "type": "request", "command": "configurationDone", "arguments": {}},
        ]
        out = io.BytesIO()
        adapter = LLDBDebugAdapter(session_factory=lambda: fake_session)
        adapter.run(io.BytesIO(b"".join(encode_message(message) for message in messages)), out)
        out.seek(0)

        attach_response = read_message(out)
        configuration_response = read_message(out)
        stopped_event = read_message(out)

        assert attach_response["success"] is True
        assert configuration_response["success"] is True
        assert stopped_event["event"] == "stopped"
        assert stopped_event["body"]["reason"] == "pause"
        fake_session.target_create.assert_not_called()
        fake_session.target_create_empty.assert_called_once_with(arch=None)
        fake_session.attach_pid.assert_called_once_with(4242)
