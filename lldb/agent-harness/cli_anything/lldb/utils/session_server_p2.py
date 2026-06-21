# ruff: noqa: F403, F405, E501
from .session_server_base import *  # noqa: F403

# fmt: off
from .session_server_p1 import _encode_token, _recv_message, _remove_state_file, _send_message, _validate_request, _write_state_file  # noqa: E402,E501
# fmt: on


class SessionServer:
    """Owns one persistent LLDBSession inside a lightweight RPC daemon."""

    def __init__(self):
        self._session: LLDBSession | None = None

    def handle(self, request: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        _validate_request(request)
        method = request["method"]
        args = request.get("args", [])
        kwargs = request.get("kwargs", {})

        if method == "ping":
            return {"ok": True, "data": {"status": "ok"}}, False

        if method == "session_status":
            status = (
                self._session.session_status()
                if self._session is not None
                else {
                    "has_target": False,
                    "has_process": False,
                    "process_origin": None,
                }
            )
            return {"ok": True, "data": status}, False

        if method == "shutdown":
            self.close()
            return {"ok": True, "data": {"status": "closed"}}, True

        if method == "target_create" and self._session is not None:
            self.close()

        try:
            if method not in _ALLOWED_SESSION_METHODS:
                raise RuntimeError(f"Unsupported session method: {method}")
            if self._session is None:
                self._session = LLDBSession()

            handler = getattr(self._session, method)
            data = handler(*args, **kwargs)
            return {"ok": True, "data": data}, False
        except Exception as exc:
            return {
                "ok": False,
                "error": str(exc),
                "type": exc.__class__.__name__,
            }, False

    def close(self):
        if self._session is not None:
            self._session.destroy()
            self._session = None


def serve(state_file: Path, idle_timeout: int = 300):
    token = os.urandom(32)
    encoded_token = _encode_token(token)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 0))
    server_socket.listen()
    server_socket.settimeout(1.0)
    _write_state_file(state_file, server_socket.getsockname(), token)

    server = SessionServer()
    last_activity = time.time()

    try:
        while True:
            try:
                conn, _address = server_socket.accept()
            except socket.timeout:
                if time.time() - last_activity >= idle_timeout:
                    break
                continue

            last_activity = time.time()
            should_stop = False
            with conn:
                try:
                    request = _recv_message(conn)
                    request_token = request.get("token")
                    if not isinstance(request_token, str) or not hmac.compare_digest(
                        request_token, encoded_token
                    ):
                        response = {
                            "ok": False,
                            "error": "Unauthorized session client",
                            "type": "PermissionError",
                        }
                    else:
                        sanitized = {
                            "method": request.get("method"),
                            "args": request.get("args", []),
                            "kwargs": request.get("kwargs", {}),
                        }
                        response, should_stop = server.handle(sanitized)
                except Exception as exc:
                    response = {
                        "ok": False,
                        "error": str(exc),
                        "type": exc.__class__.__name__,
                    }
                _send_message(conn, response)

            if should_stop:
                break
    finally:
        server.close()
        server_socket.close()
        _remove_state_file(state_file)


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Internal LLDB session daemon")
    parser.add_argument("--state-file", required=True, help="Session state file path")
    parser.add_argument(
        "--idle-timeout",
        type=int,
        default=int(os.environ.get("CLI_ANYTHING_LLDB_IDLE_TIMEOUT", "300")),
        help="Seconds of inactivity before daemon exits",
    )
    args = parser.parse_args(argv)
    serve(Path(args.state_file), idle_timeout=args.idle_timeout)
