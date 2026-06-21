# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers_base import *  # noqa: F403


class DAPClient:
    def __init__(self):
        from cli_anything.lldb.dap import read_message

        self._read_message = read_message
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "cli_anything.lldb.dap"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=HARNESS_ROOT,
        )
        self.seq = 1
        self.messages: queue.Queue = queue.Queue()
        self.reader = threading.Thread(target=self._reader_loop, daemon=True)
        self.reader.start()

    def _reader_loop(self):
        assert self.proc.stdout is not None
        try:
            while True:
                msg = self._read_message(self.proc.stdout)
                if msg is None:
                    return
                self.messages.put(msg)
        except Exception as exc:
            self.messages.put(exc)

    def request(self, command: str, arguments: dict | None = None, timeout: int = 30):
        from cli_anything.lldb.dap import encode_message

        seq = self.seq
        self.seq += 1
        payload = {"seq": seq, "type": "request", "command": command}
        if arguments is not None:
            payload["arguments"] = arguments
        assert self.proc.stdin is not None
        self.proc.stdin.write(encode_message(payload))
        self.proc.stdin.flush()

        events = []
        while True:
            msg = self._next_message(timeout)
            if msg.get("type") == "response" and msg.get("request_seq") == seq:
                assert msg.get("success"), msg.get("message")
                return msg, events
            events.append(msg)

    def read_event(self, name: str, timeout: int = 30):
        while True:
            msg = self._next_message(timeout)
            if msg.get("type") == "event" and msg.get("event") == name:
                return msg

    def read_until_event(self, names: set[str], timeout: int = 30):
        while True:
            msg = self._next_message(timeout)
            if msg.get("type") == "event" and msg.get("event") in names:
                return msg

    def _next_message(self, timeout: int):
        item = self.messages.get(timeout=timeout)
        if isinstance(item, Exception):
            raise item
        return item

    def close(self):
        if self.proc.poll() is None:
            try:
                self.request("disconnect", {"terminateDebuggee": True}, timeout=10)
                self.read_until_event({"terminated"}, timeout=10)
            except Exception:
                self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=10)

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _tb):
        self.close()


__all__ = [
    "DAPClient",
    "HARNESS_ROOT",
    "HELPER_SOURCE",
    "Path",
    "TEST_CORE",
    "_close_session",
    "_extract_address",
    "_find_compiler",
    "_run_cli",
    "annotations",
    "base64",
    "core_file",
    "json",
    "lldb_test_exe",
    "os",
    "pytest",
    "queue",
    "re",
    "session_file",
    "shutil",
    "skip_no_lldb",
    "subprocess",
    "sys",
    "threading",
]
