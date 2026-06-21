# ruff: noqa: F403, F405, E501
from .listener_base import *  # noqa: F403


class NSLoggerListenerMixin3:
    def _listen_native_bonjour(self):
        """Use macOS NetService as both Bonjour publisher and listener."""
        import select
        import shutil
        import time

        p12_path = None
        tmp_dir = None
        if self.use_ssl:
            p12_path, p12_password, tmp_dir = _make_pkcs12_identity()
        else:
            p12_password = None

        service_type = _bonjour_service_types(self.use_ssl, self.allow_plaintext)[0]
        listener = _NativeBonjourListenerProcess(
            self.bonjour_name,
            service_type,
            self.port,
            self.filter_clients,
            self.use_ssl,
            p12_path,
            p12_password,
            self.on_debug,
        )

        deadline = None
        if self.timeout is not None:
            deadline = time.monotonic() + self.timeout

        def _drain(stdout, timeout_s: float = 1.0):
            """Read any frames already buffered in the pipe before closing."""
            drain_deadline = time.monotonic() + timeout_s
            while time.monotonic() < drain_deadline:
                try:
                    readable, _, _ = select.select([stdout], [], [], 0.1)
                except (OSError, ValueError):
                    break
                if not readable:
                    break
                line = stdout.readline()
                if not line:
                    break
                self._handle_native_bonjour_event(line)

        try:
            stdout = listener.stdout
            while not self._stop.is_set():
                if deadline and time.monotonic() > deadline:
                    break
                if stdout is None:
                    break
                readable, _, _ = select.select([stdout], [], [], 0.2)
                if not readable:
                    code = listener.poll()
                    if code is not None:
                        self.on_debug(
                            f"native-bonjour listener exited with code {code} (no pending output)"
                        )
                        break
                    continue
                line = stdout.readline()
                if not line:
                    code = listener.poll()
                    if code is not None:
                        self.on_debug(
                            f"native-bonjour listener exited with code {code}"
                        )
                        break
                    continue
                self._handle_native_bonjour_event(line)
        except KeyboardInterrupt:
            self._stop.set()
            if stdout is not None:
                _drain(stdout, timeout_s=1.0)
            raise
        finally:
            listener.close()
            if tmp_dir:
                shutil.rmtree(tmp_dir, ignore_errors=True)

        return self.messages
