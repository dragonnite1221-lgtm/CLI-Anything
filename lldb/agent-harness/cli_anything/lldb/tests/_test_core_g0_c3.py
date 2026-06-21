# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestDAPProtocolMixin3:
    def test_structured_stop_rule_marks_internal_trap_without_continuing(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter, read_message

        fake_session = MagicMock()
        fake_session.process_info.return_value = {
            "state": "stopped",
            "selected_thread_id": 99,
            "stop": {
                "reason": "exception",
                "description": "Exception 0x80000003 at ntdll.dll`DbgBreakPoint",
                "hit_breakpoint_ids": [],
                "module": "ntdll.dll",
                "function": "DbgBreakPoint",
            },
            "exit_status": 0,
        }
        out = io.BytesIO()
        adapter = LLDBDebugAdapter(session_factory=lambda: fake_session)
        adapter._out = out
        adapter._configure_stop_rules(
            {
                "stopRules": [
                    {
                        "name": "windows-startup-trap",
                        "action": "stop",
                        "origin": "internalTrap",
                        "reason": "exception",
                        "module": "ntdll.dll",
                        "regex": "DbgBreakPoint",
                    }
                ]
            }
        )
        adapter._start_continue_thread = MagicMock()

        adapter._emit_execution_event(default_reason="breakpoint")
        out.seek(0)
        stopped_event = read_message(out)

        assert stopped_event["event"] == "stopped"
        stop = stopped_event["body"]["cliAnythingStop"]
        assert stop["origin"] == "internalTrap"
        assert stop["module"] == "ntdll.dll"
        assert stop["function"] == "DbgBreakPoint"
        assert stop["matchedRule"]["name"] == "windows-startup-trap"
        adapter._start_continue_thread.assert_not_called()
    def test_stack_trace_reports_total_frames(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter, read_message

        fake_session = MagicMock()
        fake_session.backtrace.return_value = {
            "frames": [
                {"index": 0, "function": "main", "file": None, "line": None, "address": "0x1000"},
            ],
            "total_frames": 7,
        }
        out = io.BytesIO()
        adapter = LLDBDebugAdapter(session_factory=lambda: fake_session)
        adapter.run(
            io.BytesIO(
                __import__("cli_anything.lldb.dap", fromlist=["encode_message"]).encode_message(
                    {"seq": 1, "type": "request", "command": "stackTrace", "arguments": {"threadId": 123}}
                )
            ),
            out,
        )
        out.seek(0)
        response = read_message(out)

        assert response["success"] is True
        assert response["body"]["totalFrames"] == 7
        fake_session.thread_select.assert_called_once_with(123)
    def test_read_memory_response_is_base64(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter, read_message

        fake_session = MagicMock()
        fake_session.read_memory.return_value = {"address": "0x1000", "size": 3, "hex": "616263"}
        out = io.BytesIO()
        adapter = LLDBDebugAdapter(session_factory=lambda: fake_session)
        adapter.run(
            io.BytesIO(
                __import__("cli_anything.lldb.dap", fromlist=["encode_message"]).encode_message(
                    {
                        "seq": 1,
                        "type": "request",
                        "command": "readMemory",
                        "arguments": {"memoryReference": "0x1000", "count": 3},
                    }
                )
            ),
            out,
        )
        out.seek(0)
        response = read_message(out)

        assert response["success"] is True
        assert response["body"]["address"] == "0x1000"
        assert response["body"]["data"] == "YWJj"
        fake_session.read_memory.assert_called_once_with(0x1000, 3)
