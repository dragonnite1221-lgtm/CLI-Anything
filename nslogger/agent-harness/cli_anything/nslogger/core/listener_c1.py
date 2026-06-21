# ruff: noqa: F403, F405, E501
from .listener_base import *  # noqa: F403


class NSLoggerListenerMixin1:
    def _handle_client(self, conn: socket.socket, addr: tuple):
        host, port = addr[0], addr[1]
        saw_first_byte = False
        if self._ssl_ctx:
            try:
                conn.settimeout(10.0)
            except OSError:
                pass
            while not self._stop.is_set():
                mode, initial = _classify_connection(conn)
                if mode == "timeout":
                    self.on_debug(f"Waiting for first TLS/raw byte from {host}:{port}")
                    continue
                break
            else:
                conn.close()
                return
            initial_hex = initial.hex(" ")
            if mode == "empty":
                self.on_debug(
                    f"Ignoring connection closed before NSLogger data from {host}:{port}"
                )
                conn.close()
                return
            if mode == "raw" and self.allow_plaintext:
                self.on_debug(
                    f"Raw NSLogger connection from {host}:{port} first_bytes={initial_hex}"
                )
            elif mode == "tls":
                self.on_debug(
                    f"Starting TLS handshake for {host}:{port} client_hello={initial_hex}"
                )
                try:
                    conn = self._ssl_ctx.wrap_socket(conn, server_side=True)
                    self.on_debug(
                        f"TLS handshake completed for {host}:{port}"
                        f" protocol={conn.version()} cipher={conn.cipher()}"
                    )
                except (ssl.SSLError, OSError) as exc:
                    self.on_debug(f"TLS handshake failed for {host}:{port}: {exc!r}")
                    conn.close()
                    return
            else:
                self.on_debug(
                    f"Expected TLS ClientHello from {host}:{port}, got first_bytes={initial_hex}"
                )
                conn.close()
                return
        else:
            self.on_debug(f"Raw NSLogger connection from {host}:{port}")
        self.on_connect(host, port)
        try:
            conn.settimeout(2.0)
            while not self._stop.is_set():
                try:
                    header = b""
                    while len(header) < 4:
                        chunk = conn.recv(4 - len(header))
                        if not chunk:
                            if not saw_first_byte:
                                self.on_debug(
                                    f"No data before disconnect from {host}:{port}"
                                )
                            return
                        saw_first_byte = True
                        header += chunk
                    msg_len = struct.unpack(">I", header)[0]
                    self.on_debug(
                        f"Frame header from {host}:{port}: len={msg_len} bytes"
                    )
                    if msg_len == 0:
                        continue
                    raw = b""
                    while len(raw) < msg_len:
                        chunk = conn.recv(msg_len - len(raw))
                        if not chunk:
                            return
                        raw += chunk
                    try:
                        msg = _parse_message(raw)
                        self.messages.append(msg)
                        self.on_message(msg)
                    except ParseError as exc:
                        self.on_parse_error(host, port, raw, exc)
                except socket.timeout:
                    if not saw_first_byte:
                        self.on_debug(f"Waiting for first frame from {host}:{port}")
                    continue
                except OSError as exc:
                    self.on_debug(f"Socket error from {host}:{port}: {exc}")
                    return
        finally:
            conn.close()
            self.on_disconnect(host, port)
