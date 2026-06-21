# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestDAPProtocolMixin2:
    def test_auto_continue_internal_breakpoint_emits_output_and_resumes(self):
        from cli_anything.lldb.dap import LLDBDebugAdapter, read_message

        fake_session = MagicMock()
        fake_session.process_info.return_value = {
            "state": "stopped",
            "selected_thread_id": 99,
            "stop": {
                "reason": "breakpoint",
                "description": "frame #0: nvgpucomp64.dll`__jit_debug_register_code",
                "hit_breakpoint_ids": [],
            },
            "exit_status": 0,
        }
        out = io.BytesIO()
        adapter = LLDBDebugAdapter(session_factory=lambda: fake_session)
        adapter._out = out
        adapter._configure_stop_rules({"autoContinueInternalBreakpoints": True})
        adapter._start_continue_thread = MagicMock()

        adapter._emit_execution_event(default_reason="breakpoint")
        out.seek(0)
        output_event = read_message(out)
        continued_event = read_message(out)
        stopped_event = read_message(out)

        assert output_event["event"] == "output"
        assert "auto-continued stop rule nvidia-shader-jit-debug-register" in output_event["body"]["output"]
        assert continued_event["event"] == "continued"
        assert stopped_event is None
        adapter._start_continue_thread.assert_called_once()
    def test_stop_rule_profile_can_auto_continue_structured_internal_stop(self, tmp_path: Path):
        from cli_anything.lldb.dap import LLDBDebugAdapter, read_message

        profile = tmp_path / "c4d-stop-rules.json"
        profile.write_text(
            json.dumps(
                {
                    "stopRules": [
                        {
                            "name": "c4d-nvidia-jit",
                            "action": "continue",
                            "origin": "internalTrap",
                            "module": "nvgpucomp64.dll",
                            "function": "__jit_debug_register_code",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        fake_session = MagicMock()
        fake_session.process_info.return_value = {
            "state": "stopped",
            "selected_thread_id": 99,
            "stop": {
                "reason": "breakpoint",
                "description": "driver JIT registration",
                "hit_breakpoint_ids": [],
                "frame": {
                    "module": "nvgpucomp64.dll",
                    "module_path": "C:/Windows/System32/DriverStore/nvgpucomp64.dll",
                    "function": "__jit_debug_register_code",
                },
            },
            "exit_status": 0,
        }
        out = io.BytesIO()
        adapter = LLDBDebugAdapter(session_factory=lambda: fake_session, profile_file=str(profile))
        adapter._out = out
        adapter._configure_stop_rules({})
        adapter._start_continue_thread = MagicMock()

        adapter._emit_execution_event(default_reason="breakpoint")
        out.seek(0)
        output_event = read_message(out)
        continued_event = read_message(out)
        stopped_event = read_message(out)

        assert "auto-continued stop rule c4d-nvidia-jit" in output_event["body"]["output"]
        assert continued_event["event"] == "continued"
        assert stopped_event is None
        adapter._start_continue_thread.assert_called_once()
