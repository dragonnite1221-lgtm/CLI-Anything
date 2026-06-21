# ruff: noqa: F403, F405, E501
from .listener_base import *  # noqa: F403


class NSLoggerListenerMixin2:
    def _start_bonjour(self, local_ip: str) -> object:
        """Advertise NSLogger services via Bonjour/mDNS."""
        service_types = _bonjour_service_types(self.use_ssl, self.allow_plaintext)
        self.on_debug(
            "Bonjour service types: "
            f"{', '.join(service_types)} filter_clients={int(self.filter_clients)}"
        )
        if self.bonjour_publisher == "native" and sys.platform == "darwin":
            self.on_debug("Advertising Bonjour with macOS NetService")
            publisher = _NativeBonjourPublisher(
                self.bonjour_name,
                service_types,
                self.port,
                self.filter_clients,
                self.on_debug,
            )
            self.on_bonjour_ready(self.bonjour_name, self.port)
            return publisher

        if self.bonjour_publisher == "dns-sd" and sys.platform == "darwin":
            self.on_debug("Advertising Bonjour with macOS dns-sd")
            publisher = _DnsSdBonjourPublisher(
                self.bonjour_name,
                service_types,
                self.port,
                self.filter_clients,
                self.on_debug,
            )
            self.on_bonjour_ready(self.bonjour_name, self.port)
            return publisher

        try:
            self.on_debug(f"Advertising Bonjour with zeroconf address={local_ip}")
            publisher = _ZeroconfBonjourPublisher(
                self.bonjour_name,
                service_types,
                self.port,
                local_ip,
                self.filter_clients,
            )
        except ImportError:
            self.on_debug("zeroconf package unavailable; falling back to macOS dns-sd")
            publisher = _DnsSdBonjourPublisher(
                self.bonjour_name,
                service_types,
                self.port,
                self.filter_clients,
                self.on_debug,
            )
        self.on_bonjour_ready(self.bonjour_name, self.port)
        return publisher

    def _should_use_native_bonjour_listener(self) -> bool:
        if not (
            self.bonjour
            and self.bonjour_publisher == "native"
            and sys.platform == "darwin"
        ):
            return False
        # NSNetServiceListenForConnections owns the listening socket, so it can only
        # publish one service type on the port. The explicit "auto" mode still uses
        # Python's socket listener plus a publisher so it can advertise raw+SSL.
        return len(_bonjour_service_types(self.use_ssl, self.allow_plaintext)) == 1
