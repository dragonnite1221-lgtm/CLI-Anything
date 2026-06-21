# ruff: noqa: F403, F405, E501
from .dap_base import *  # noqa: F403


class LLDBDebugAdapterMixin7:
    def _send_response(
        self,
        request_seq: int,
        command: str,
        body: dict[str, Any] | None = None,
        success: bool = True,
        message: str | None = None,
    ):
        with self._protocol_lock:
            payload: dict[str, Any] = {
                "seq": self._next_seq(),
                "type": "response",
                "request_seq": request_seq,
                "success": success,
                "command": command,
            }
            if body is not None:
                payload["body"] = body
            if message:
                payload["message"] = message
            self._write(payload)

    def _send_event(self, event: str, body: dict[str, Any] | None = None):
        with self._protocol_lock:
            payload: dict[str, Any] = {
                "seq": self._next_seq(),
                "type": "event",
                "event": event,
            }
            if body is not None:
                payload["body"] = body
            self._write(payload)

    def _next_seq(self) -> int:
        seq = self._seq
        self._seq += 1
        return seq

    def _write(self, payload: dict[str, Any]):
        if self._out is None:
            raise RuntimeError("DAP output stream is not initialized")
        self._out.write(encode_message(payload))
        self._out.flush()

    def _log(self, message: str):
        if self._log_file:
            with self._log_file.open("a", encoding="utf-8") as handle:
                handle.write(message + "\n")
        else:
            print(message, file=sys.stderr)
