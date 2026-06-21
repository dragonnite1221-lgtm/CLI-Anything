# ruff: noqa: F403, F405, E501
from .listener_base_base import *  # noqa: F403

# fmt: off
from .listener_base_p2 import _dns_sd_txt_args  # noqa: E402,E501
# fmt: on


class _DnsSdBonjourPublisher:
    """Fallback Bonjour publisher using macOS dns-sd."""

    def __init__(
        self,
        service_name: str,
        service_types: tuple[str, ...],
        port: int,
        filter_clients: bool,
        on_debug: Callable[[str], None],
    ):
        self._procs = []
        txt_args = _dns_sd_txt_args(service_name, filter_clients)
        for service_type in service_types:
            command = [
                "dns-sd",
                "-R",
                service_name,
                service_type,
                "local",
                str(port),
                *txt_args,
            ]
            proc = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            self._procs.append(proc)
            on_debug(
                f"Started dns-sd publisher pid={proc.pid} command={' '.join(command)}"
            )
            threading.Thread(
                target=self._drain_output,
                args=(proc, service_type, on_debug),
                daemon=True,
            ).start()

    @staticmethod
    def _drain_output(
        proc: subprocess.Popen, service_type: str, on_debug: Callable[[str], None]
    ):
        if proc.stdout is None:
            return
        try:
            for line in proc.stdout:
                line = line.strip()
                if line:
                    on_debug(f"dns-sd[{service_type}] {line}")
        finally:
            code = proc.poll()
            if code is not None:
                on_debug(f"dns-sd[{service_type}] exited with code {code}")

    def close(self):
        for proc in self._procs:
            try:
                proc.terminate()
                proc.wait(timeout=2.0)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
