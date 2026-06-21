# ruff: noqa: F403, F405, E501
from .listener_base_base import *  # noqa: F403

# fmt: off
from .listener_base_p1 import _swift_helper_env  # noqa: E402,E501
# fmt: on


def _compiled_swift_helper(helper_name: str, on_debug: Callable[[str], None]) -> str:
    helper = resources.files("cli_anything.nslogger").joinpath(
        f"helpers/{helper_name}.swift"
    )
    helper_path = str(helper)
    cache_dir = os.path.join(tempfile.gettempdir(), "nslogger_cli_swift_helpers")
    os.makedirs(cache_dir, exist_ok=True)
    try:
        stamp = f"{int(os.path.getmtime(helper_path))}_{os.path.getsize(helper_path)}"
    except OSError:
        stamp = "unknown"
    executable = os.path.join(cache_dir, f"{helper_name}_{stamp}")
    if not os.path.exists(executable):
        on_debug(f"Compiling native helper {helper_name}")
        subprocess.run(
            ["swiftc", helper_path, "-o", executable],
            check=True,
            capture_output=True,
            env=_swift_helper_env(),
        )
    return executable


def _peek(conn: socket.socket, size: int = 16) -> bytes:
    try:
        return conn.recv(size, socket.MSG_PEEK)
    except socket.timeout:
        raise
    except (AttributeError, OSError):
        return b""


def _peek_hex(conn: socket.socket, size: int = 16) -> str:
    return _peek(conn, size).hex(" ")


def _looks_like_tls_client_hello(conn: socket.socket) -> bool:
    """Best-effort TLS ClientHello detection without consuming bytes."""
    header = _peek(conn, 5)
    if len(header) < 3:
        return False
    # TLS record header: 0x16, 0x03, version
    return header[0] == 0x16 and header[1] == 0x03


def _classify_connection(conn: socket.socket) -> tuple[str, bytes]:
    """Classify the first bytes without consuming them: tls, raw, or empty."""
    try:
        header = _peek(conn, 5)
    except socket.timeout:
        return "timeout", b""
    if not header:
        return "empty", header
    if len(header) >= 3 and header[0] == 0x16 and header[1] == 0x03:
        return "tls", header
    return "raw", header


def _dns_sd_txt_args(service_name: str, filter_clients: bool = False) -> list[str]:
    """Return TXT records matching NSLogger.app's named-service publishing."""
    return ["filterClients=1"] if service_name and filter_clients else []


def _bonjour_service_types(
    use_ssl: bool, allow_plaintext: bool = False
) -> tuple[str, ...]:
    """Return the Bonjour service type advertised by NSLogger.app for this mode."""
    if use_ssl and allow_plaintext:
        return ("_nslogger._tcp", "_nslogger-ssl._tcp")
    return ("_nslogger-ssl._tcp",) if use_ssl else ("_nslogger._tcp",)


class _ZeroconfBonjourPublisher:
    """In-process Bonjour publisher so Ctrl-C cannot leave dns-sd children behind."""

    def __init__(
        self,
        service_name: str,
        service_types: tuple[str, ...],
        port: int,
        local_ip: str,
        filter_clients: bool,
    ):
        from zeroconf import ServiceInfo, Zeroconf

        self._zeroconf = Zeroconf()
        self._infos = []
        properties = {"filterClients": "1"} if service_name and filter_clients else {}
        addresses = [] if local_ip == "127.0.0.1" else [socket.inet_aton(local_ip)]
        hostname = socket.gethostname().split(".")[0]
        server = f"{hostname}.local."

        for service_type in service_types:
            type_domain = f"{service_type}.local."
            info = ServiceInfo(
                type_domain,
                f"{service_name}.{type_domain}",
                addresses=addresses,
                port=port,
                properties=properties,
                server=server,
            )
            self._zeroconf.register_service(info)
            self._infos.append(info)

    def close(self):
        for info in self._infos:
            try:
                self._zeroconf.unregister_service(info)
            except Exception:
                pass
        self._zeroconf.close()
