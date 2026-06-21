# ruff: noqa: F403, F405, E501
from .listener_base import *  # noqa: F403


class NSLoggerListenerMixin0:
    """Listen on a TCP port for NSLogger client connections."""

    def __init__(
        self,
        port: int = 50001,
        timeout: Optional[float] = None,
        on_message: Optional[Callable[[LogMessage], None]] = None,
        on_connect: Optional[Callable[[str, int], None]] = None,
        on_disconnect: Optional[Callable[[str, int], None]] = None,
        on_bonjour_ready: Optional[Callable[[str, int], None]] = None,
        on_parse_error: Optional[Callable[[str, int, bytes, Exception], None]] = None,
        on_debug: Optional[Callable[[str], None]] = None,
        use_ssl: Optional[bool] = None,
        allow_plaintext: Optional[bool] = None,
        bonjour: bool = False,
        bonjour_name: Optional[str] = None,
        filter_clients: Optional[bool] = None,
        bonjour_publisher: str = "native",
        advertise_host: Optional[str] = None,
    ):
        self.port = port
        self.timeout = timeout
        self.on_message = on_message or (lambda m: None)
        self.on_connect = on_connect or (lambda h, p: None)
        self.on_disconnect = on_disconnect or (lambda h, p: None)
        self.on_bonjour_ready = on_bonjour_ready or (lambda name, port: None)
        self.on_parse_error = on_parse_error or (lambda h, p, raw, e: None)
        self.on_debug = on_debug or (lambda message: None)
        # Bonjour mode mirrors NSLogger.app: publish the SSL service by default.
        self.use_ssl = bonjour if use_ssl is None else use_ssl
        self.allow_plaintext = False if allow_plaintext is None else allow_plaintext
        self.bonjour = bonjour
        self.bonjour_name = bonjour_name if bonjour_name is not None else ""
        self.filter_clients = (
            bool(self.bonjour_name) if filter_clients is None else filter_clients
        )
        self.bonjour_publisher = bonjour_publisher
        self.advertise_host = advertise_host
        self._stop = threading.Event()
        self._ssl_ctx: Optional[ssl.SSLContext] = None
        self.messages: list[LogMessage] = []

    def stop(self):
        self._stop.set()
