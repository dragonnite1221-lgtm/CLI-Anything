# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestDAPProtocolMixin5:
    def test_attach_accepts_process_name_without_program(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter, encode_message, read_message

        fake_session = MagicMock()
        fake_session.target_create_empty.return_value = {"executable": None}
        fake_session.attach_name.return_value = {}
        fake_session.process_info.return_value = {
            "state": "stopped",
            "selected_thread_id": 78,
            "stop": None,
            "exit_status": 0,
        }
        messages = [
            {
                "seq": 1,
                "type": "request",
                "command": "attach",
                "arguments": {"processName": "sample-app", "waitFor": True},
            },
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
        fake_session.attach_name.assert_called_once_with("sample-app", wait_for=True)
    def test_modules_response_shape(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter, read_message

        fake_session = MagicMock()
        fake_session.modules.return_value = {
            "modules": [
                {
                    "id": 1,
                    "name": "app.exe",
                    "path": "C:/tmp/app.exe",
                    "symbol_status": "loaded",
                    "address": "0x1000",
                    "version": [1, 2, 3],
                }
            ]
        }
        out = io.BytesIO()
        adapter = LLDBDebugAdapter(session_factory=lambda: fake_session)
        adapter.run(
            io.BytesIO(
                __import__("cli_anything.lldb.dap", fromlist=["encode_message"]).encode_message(
                    {"seq": 1, "type": "request", "command": "modules", "arguments": {}}
                )
            ),
            out,
        )
        out.seek(0)
        response = read_message(out)

        assert response["success"] is True
        module = response["body"]["modules"][0]
        assert module["name"] == "app.exe"
        assert module["symbolStatus"] == "loaded"
    def test_exception_info_uses_current_stop_reason(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter, read_message

        fake_session = MagicMock()
        fake_session.process_info.return_value = {
            "state": "stopped",
            "stop": {"reason": "breakpoint", "description": "breakpoint 1.1"},
        }
        out = io.BytesIO()
        adapter = LLDBDebugAdapter(session_factory=lambda: fake_session)
        adapter.run(
            io.BytesIO(
                __import__("cli_anything.lldb.dap", fromlist=["encode_message"]).encode_message(
                    {"seq": 1, "type": "request", "command": "exceptionInfo", "arguments": {"threadId": 1}}
                )
            ),
            out,
        )
        out.seek(0)
        response = read_message(out)

        assert response["success"] is True
        assert response["body"]["exceptionId"] == "breakpoint"
        assert response["body"]["description"] == "breakpoint 1.1"
