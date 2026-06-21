# ruff: noqa: F403, F405, E501
from .listener_base_base import *  # noqa: F403

# fmt: off
from .listener_base_p1 import _swift_helper_env  # noqa: E402,E501
from .listener_base_p2 import _compiled_swift_helper  # noqa: E402,E501
# fmt: on


class _NativeBonjourListenerProcess:
    """macOS NetService listener using NSNetServiceListenForConnections."""

    def __init__(
        self,
        service_name: str,
        service_type: str,
        port: int,
        filter_clients: bool,
        secure: bool,
        p12_path: Optional[str],
        p12_password: Optional[str],
        on_debug: Callable[[str], None],
    ):
        helper = _compiled_swift_helper("native_bonjour_listener", on_debug)
        command = [
            helper,
            "--name",
            service_name,
            "--port",
            str(port),
            "--type",
            service_type,
        ]
        if filter_clients:
            command.extend(["--txt", "filterClients=1"])
        if secure:
            command.append("--secure")
            if p12_path:
                command.extend(["--p12", p12_path])
            if p12_password:
                command.extend(["--p12-pass", p12_password])

        self._proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=_swift_helper_env(),
            start_new_session=True,  # don't propagate terminal Ctrl-C SIGINT to this helper
        )
        on_debug(
            f"Started native Bonjour listener pid={self._proc.pid} command={' '.join(command)}"
        )

    @property
    def stdout(self):
        return self._proc.stdout

    def poll(self):
        return self._proc.poll()

    def close(self):
        try:
            self._proc.terminate()
            self._proc.wait(timeout=2.0)
        except Exception:
            try:
                self._proc.kill()
            except Exception:
                pass


__all__ = [
    "Callable",
    "LogMessage",
    "NSLOGGER_SERVICE_TYPE",
    "NSLOGGER_SSL_SERVICE_TYPE",
    "NSLoggerListener",
    "Optional",
    "ParseError",
    "_DnsSdBonjourPublisher",
    "_NativeBonjourListenerProcess",
    "_NativeBonjourPublisher",
    "_ZeroconfBonjourPublisher",
    "_bonjour_service_types",
    "_classify_connection",
    "_compiled_swift_helper",
    "_dns_sd_txt_args",
    "_get_local_ip",
    "_looks_like_tls_client_hello",
    "_make_pkcs12_identity",
    "_make_ssl_context",
    "_parse_message",
    "_peek",
    "_peek_hex",
    "_swift_helper_env",
    "annotations",
    "base64",
    "json",
    "os",
    "resources",
    "socket",
    "ssl",
    "struct",
    "subprocess",
    "sys",
    "tempfile",
    "threading",
]
