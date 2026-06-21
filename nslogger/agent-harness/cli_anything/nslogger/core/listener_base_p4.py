# ruff: noqa: F403, F405, E501
from .listener_base_base import *  # noqa: F403

# fmt: off
from .listener_base_p1 import _swift_helper_env  # noqa: E402,E501
from .listener_base_p2 import _compiled_swift_helper  # noqa: E402,E501
# fmt: on


class _NativeBonjourPublisher:
    """macOS Bonjour publisher backed by Foundation.NetService, matching NSLogger.app more closely."""

    def __init__(
        self,
        service_name: str,
        service_types: tuple[str, ...],
        port: int,
        filter_clients: bool,
        on_debug: Callable[[str], None],
    ):
        helper = _compiled_swift_helper("native_bonjour_publisher", on_debug)
        command = [
            helper,
            "--name",
            service_name,
            "--port",
            str(port),
            "--types",
            ",".join(service_types),
        ]
        if filter_clients:
            command.extend(["--txt", "filterClients=1"])

        self._proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=_swift_helper_env(),
        )
        on_debug(
            f"Started native Bonjour publisher pid={self._proc.pid} command={' '.join(command)}"
        )
        threading.Thread(
            target=self._drain_output,
            args=(self._proc, on_debug),
            daemon=True,
        ).start()

    @staticmethod
    def _drain_output(proc: subprocess.Popen, on_debug: Callable[[str], None]):
        if proc.stdout is None:
            return
        try:
            for line in proc.stdout:
                line = line.strip()
                if line:
                    on_debug(f"native-bonjour {line}")
        finally:
            code = proc.poll()
            if code is not None:
                on_debug(f"native-bonjour exited with code {code}")

    def close(self):
        try:
            self._proc.terminate()
            self._proc.wait(timeout=2.0)
        except Exception:
            try:
                self._proc.kill()
            except Exception:
                pass
