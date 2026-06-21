# ruff: noqa: F403, F405, E501
from .listener_base import *  # noqa: F403


class NSLoggerListenerMixin4:
    def _handle_native_bonjour_event(self, line: str):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            self.on_debug(f"native-bonjour {line.strip()}")
            return

        event_type = event.get("event")
        if event_type == "ready":
            self.port = int(event.get("port") or self.port)
            self.on_bonjour_ready(event.get("name", self.bonjour_name), self.port)
        elif event_type == "debug":
            self.on_debug(f"native-bonjour {event.get('message', '')}")
        elif event_type == "connect":
            self.on_connect("native-bonjour", 0)
        elif event_type == "disconnect":
            self.on_disconnect("native-bonjour", 0)
        elif event_type == "error":
            details = " ".join(
                str(event.get(key, ""))
                for key in ("message", "error", "status")
                if event.get(key, "") != ""
            )
            self.on_debug(f"native-bonjour error: {details}")
        elif event_type == "frame":
            try:
                raw = base64.b64decode(event.get("payload", ""), validate=True)
                self.on_debug(
                    f"Frame #{len(self.messages) + 1}: {len(raw)} bytes"
                    f" head={raw[:8].hex(' ')}"
                )
                msg = _parse_message(raw)
                self.messages.append(msg)
                self.on_message(msg)
            except (ValueError, ParseError) as exc:
                raw_bytes = base64.b64decode(
                    event.get("payload", "") or "", validate=False
                )
                self.on_parse_error("native-bonjour", 0, raw_bytes, exc)

    def listen(self):
        """Block until timeout or stop() is called. Returns collected messages."""
        if self._should_use_native_bonjour_listener():
            return self._listen_native_bonjour()

        tmp_dir = None
        if self.use_ssl:
            self._ssl_ctx, tmp_dir = _make_ssl_context()

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", self.port))
        server.listen(5)
        server.settimeout(1.0)

        publisher = None
        if self.bonjour:
            local_ip = self.advertise_host or _get_local_ip()
            publisher = self._start_bonjour(local_ip)

        deadline = None
        if self.timeout is not None:
            import time

            deadline = time.monotonic() + self.timeout

        threads = []
        try:
            import time

            while not self._stop.is_set():
                if deadline and time.monotonic() > deadline:
                    break
                try:
                    conn, addr = server.accept()
                    t = threading.Thread(
                        target=self._handle_client,
                        args=(conn, addr),
                        daemon=True,
                    )
                    t.start()
                    threads.append(t)
                except socket.timeout:
                    continue
        finally:
            server.close()
            self._stop.set()
            for t in threads:
                t.join(timeout=2.0)
            if publisher:
                publisher.close()
            if tmp_dir:
                import shutil

                shutil.rmtree(tmp_dir, ignore_errors=True)

        return self.messages
