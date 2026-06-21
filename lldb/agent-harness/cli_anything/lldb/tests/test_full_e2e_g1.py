# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


@skip_no_lldb
class TestLLDBDAPE2E:
    def test_dap_source_line_breakpoint(self, lldb_test_exe: str):
        source_path = Path(lldb_test_exe).parent / "lldb_helper.c"
        lines = source_path.read_text(encoding="utf-8").splitlines()
        target_line = next(
            i for i, line in enumerate(lines, start=1) if "pause_ms(50);" in line
        )

        with DAPClient() as client:
            client.request("initialize", {"adapterID": "cli-anything-lldb"})
            client.read_event("initialized")
            client.request("launch", {"program": lldb_test_exe, "stopOnEntry": False})
            bps, _ = client.request(
                "setBreakpoints",
                {
                    "source": {"path": str(source_path)},
                    "breakpoints": [{"line": target_line}],
                },
            )
            breakpoint_payload = bps["body"]["breakpoints"][0]
            assert breakpoint_payload["verified"] is True
            assert breakpoint_payload["line"] == target_line

            client.request("configurationDone")
            stopped = client.read_until_event({"stopped"})

            assert stopped["body"]["reason"] == "breakpoint"
            threads, _ = client.request("threads")
            thread_id = threads["body"]["threads"][0]["id"]
            stack, _ = client.request(
                "stackTrace", {"threadId": thread_id, "levels": 10}
            )
            frame = stack["body"]["stackFrames"][0]
            scopes, _ = client.request("scopes", {"frameId": frame["id"]})
            variables_ref = scopes["body"]["scopes"][0]["variablesReference"]
            variables, _ = client.request(
                "variables", {"variablesReference": variables_ref}
            )
            variables_by_name = {
                item["name"]: item for item in variables["body"]["variables"]
            }
            assert variables_by_name["pair"]["variablesReference"] > 0

            pair_children, _ = client.request(
                "variables",
                {"variablesReference": variables_by_name["pair"]["variablesReference"]},
            )
            pair_values = {
                item["name"]: item["value"]
                for item in pair_children["body"]["variables"]
            }
            assert pair_values["left"] in {"2", "0x2"}
            assert pair_values["right"] in {"40", "0x28"}

            set_total, _ = client.request(
                "setVariable",
                {
                    "variablesReference": variables_ref,
                    "name": "total",
                    "value": "77",
                },
            )
            assert set_total["body"]["value"] in {"77", "0x4d"}
            total_eval, _ = client.request(
                "evaluate", {"expression": "total", "frameId": frame["id"]}
            )
            assert total_eval["body"]["result"] in {"77", "0x4d"}

    def test_dap_breakpoint_variables_source_disassemble_and_continue(
        self, lldb_test_exe: str
    ):
        with DAPClient() as client:
            initialize, _ = client.request(
                "initialize", {"adapterID": "cli-anything-lldb"}
            )
            assert initialize["body"]["supportsConfigurationDoneRequest"] is True
            client.read_event("initialized")

            client.request("launch", {"program": lldb_test_exe, "stopOnEntry": False})
            bps, _ = client.request(
                "setFunctionBreakpoints", {"breakpoints": [{"name": "probe"}]}
            )
            assert bps["body"]["breakpoints"]
            client.request("configurationDone")
            stopped = client.read_until_event({"stopped"})
            assert stopped["body"]["reason"] == "breakpoint"

            threads, _ = client.request("threads")
            thread_id = threads["body"]["threads"][0]["id"]
            stack, _ = client.request(
                "stackTrace", {"threadId": thread_id, "levels": 10}
            )
            frame = stack["body"]["stackFrames"][0]
            assert frame["instructionPointerReference"].startswith("0x")
            assert stack["body"]["totalFrames"] >= len(stack["body"]["stackFrames"])

            scopes, _ = client.request("scopes", {"frameId": frame["id"]})
            variables_ref = scopes["body"]["scopes"][0]["variablesReference"]
            variables, _ = client.request(
                "variables", {"variablesReference": variables_ref}
            )
            variables_by_name = {
                item["name"]: item for item in variables["body"]["variables"]
            }
            names = set(variables_by_name)
            assert {"a", "b"} <= names

            evaluated, _ = client.request(
                "evaluate", {"expression": "a + b", "frameId": frame["id"]}
            )
            assert evaluated["body"]["result"] in {"42", "0x2a"}

            source_path = frame.get("source", {}).get("path")
            assert source_path
            source, _ = client.request("source", {"source": {"path": source_path}})
            assert "GLOBAL_BUFFER" in source["body"]["content"]

            loaded_sources, _ = client.request("loadedSources")
            loaded_paths = {
                Path(item["path"]).name for item in loaded_sources["body"]["sources"]
            }
            assert "lldb_helper.c" in loaded_paths

            modules, _ = client.request("modules")
            module_names = {item["name"] for item in modules["body"]["modules"]}
            assert Path(lldb_test_exe).name in module_names

            exception_info, _ = client.request("exceptionInfo", {"threadId": thread_id})
            assert exception_info["body"]["exceptionId"]

            address_eval, _ = client.request(
                "evaluate",
                {"expression": "(char*)&GLOBAL_BUFFER[0]", "frameId": frame["id"]},
            )
            addr = _extract_address({"value": address_eval["body"]["result"]})
            memory, _ = client.request(
                "readMemory", {"memoryReference": addr, "count": 32}
            )
            raw = base64.b64decode(memory["body"]["data"])
            assert b"agent-native-lldb" in raw

            disassembly, _ = client.request(
                "disassemble",
                {
                    "memoryReference": frame["instructionPointerReference"],
                    "instructionCount": 4,
                },
            )
            assert disassembly["body"]["instructions"]

            client.request("next", {"threadId": thread_id})
            step_stop = client.read_until_event({"stopped", "terminated"})
            assert step_stop["event"] in {"stopped", "terminated"}

            if step_stop["event"] == "stopped":
                client.request("continue", {"threadId": thread_id})
                final_event = client.read_until_event(
                    {"exited", "terminated", "stopped"}
                )
                assert final_event["event"] in {"exited", "terminated", "stopped"}

    def test_dap_stop_on_entry(self, lldb_test_exe: str):
        with DAPClient() as client:
            client.request("initialize", {"adapterID": "cli-anything-lldb"})
            client.read_event("initialized")
            client.request("launch", {"program": lldb_test_exe, "stopOnEntry": True})
            client.request("configurationDone")
            stopped = client.read_until_event({"stopped"})

            assert stopped["body"]["reason"] == "entry"
