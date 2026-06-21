# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


@skip_no_lldb
class TestLLDBE2E:
    def test_persistent_target_info(self, lldb_test_exe: str, session_file: Path):
        try:
            create = _run_cli(
                "target", "create", "--exe", lldb_test_exe, session_file=session_file
            )
            info = _run_cli("target", "info", session_file=session_file)
        finally:
            _close_session(session_file)

        assert create["executable"] == lldb_test_exe
        assert info["executable"]
        assert info["num_breakpoints"] == 0

    def test_breakpoint_step_expr_and_memory_workflow(
        self, lldb_test_exe: str, session_file: Path
    ):
        try:
            _run_cli(
                "target", "create", "--exe", lldb_test_exe, session_file=session_file
            )
            bp = _run_cli(
                "breakpoint", "set", "--function", "probe", session_file=session_file
            )
            launched = _run_cli("process", "launch", session_file=session_file)
            threads = _run_cli("thread", "list", session_file=session_file)
            backtrace = _run_cli("thread", "backtrace", session_file=session_file)
            locals_payload = _run_cli("frame", "locals", session_file=session_file)
            expr_payload = _run_cli("expr", "a + b", session_file=session_file)
            address_payload = _run_cli(
                "expr", "(char*)&GLOBAL_BUFFER[0]", session_file=session_file
            )
            addr = _extract_address(address_payload)
            memory = _run_cli(
                "memory",
                "read",
                "--address",
                addr,
                "--size",
                "32",
                session_file=session_file,
            )
            found = _run_cli(
                "memory",
                "find",
                "agent-native-lldb",
                "--start",
                addr,
                "--size",
                "32",
                session_file=session_file,
            )
            stepped = _run_cli("step", "over", session_file=session_file)
            _run_cli(
                "breakpoint", "delete", "--id", str(bp["id"]), session_file=session_file
            )
            finished = _run_cli("process", "continue", session_file=session_file)
        finally:
            _close_session(session_file)

        assert launched["state"] == "stopped"
        assert bp["locations"] >= 1
        assert threads["threads"]
        assert backtrace["frames"]
        local_names = {item["name"] for item in locals_payload["variables"]}
        assert {"a", "b"} <= local_names
        assert expr_payload["error"] is None
        assert expr_payload["value"] in {"42", "0x2a"}
        assert len(memory["hex"]) >= 32
        assert found["found"] is True
        assert stepped["address"].startswith("0x")
        assert finished["state"] in {"exited", "stopped"}

    def test_attach_cleanup_does_not_kill_process(
        self, lldb_test_exe: str, session_file: Path
    ):
        proc = subprocess.Popen(
            [lldb_test_exe, "sleep"], cwd=Path(lldb_test_exe).parent
        )
        try:
            _run_cli(
                "target", "create", "--exe", lldb_test_exe, session_file=session_file
            )
            attached = _run_cli(
                "process", "attach", "--pid", str(proc.pid), session_file=session_file
            )
            assert attached["pid"] == proc.pid

            _close_session(session_file)

            assert proc.poll() is None
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)
