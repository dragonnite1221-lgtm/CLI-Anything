# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestNSLoggerListenerMixin0:
    def test_swift_helper_env_uses_temp_module_caches(self):
        env = _swift_helper_env()

        assert env["SWIFT_MODULE_CACHE_PATH"].startswith(tempfile.gettempdir())
        assert env["CLANG_MODULE_CACHE_PATH"].startswith(tempfile.gettempdir())
    def test_named_bonjour_service_uses_filter_txt_record(self):
        assert _dns_sd_txt_args("bazinga", filter_clients=True) == ["filterClients=1"]
    def test_named_bonjour_service_does_not_filter_by_default(self):
        assert _dns_sd_txt_args("bazinga") == []
    def test_empty_bonjour_service_has_no_filter_txt_record(self):
        assert _dns_sd_txt_args("") == []
    def test_ssl_bonjour_advertises_only_ssl_service(self):
        assert _bonjour_service_types(True) == ("_nslogger-ssl._tcp",)
    def test_auto_bonjour_advertises_raw_and_ssl_services(self):
        assert _bonjour_service_types(True, allow_plaintext=True) == ("_nslogger._tcp", "_nslogger-ssl._tcp")
    def test_non_ssl_bonjour_advertises_only_legacy_service(self):
        assert _bonjour_service_types(False) == ("_nslogger._tcp",)
    def test_macos_bonjour_prefers_native_netservice(self):
        listener = NSLoggerListener(bonjour=True, bonjour_name="bazinga")

        class DummyNativePublisher:
            def __init__(self, service_name, service_types, port, filter_clients, on_debug):
                self.service_name = service_name
                self.service_types = service_types
                self.port = port
                self.filter_clients = filter_clients
                self.on_debug = on_debug

        with patch("cli_anything.nslogger.core.listener.sys.platform", "darwin"), \
                patch("cli_anything.nslogger.core.listener._NativeBonjourPublisher", DummyNativePublisher), \
                patch("cli_anything.nslogger.core.listener._DnsSdBonjourPublisher") as dns_sd_publisher, \
                patch("cli_anything.nslogger.core.listener._ZeroconfBonjourPublisher") as zeroconf_publisher:
            publisher = listener._start_bonjour("192.168.10.1")

        assert isinstance(publisher, DummyNativePublisher)
        assert publisher.service_name == "bazinga"
        assert publisher.service_types == ("_nslogger-ssl._tcp",)
        assert publisher.filter_clients is True
        assert dns_sd_publisher.call_count == 0
        assert zeroconf_publisher.call_count == 0
    def test_bonjour_auto_mode_can_publish_raw_and_ssl_services(self):
        listener = NSLoggerListener(
            bonjour=True,
            bonjour_name="bazinga",
            allow_plaintext=True,
        )

        class DummyNativePublisher:
            def __init__(self, service_name, service_types, port, filter_clients, on_debug):
                self.service_types = service_types

        with patch("cli_anything.nslogger.core.listener.sys.platform", "darwin"), \
                patch("cli_anything.nslogger.core.listener._NativeBonjourPublisher", DummyNativePublisher):
            publisher = listener._start_bonjour("192.168.10.1")

        assert publisher.service_types == ("_nslogger._tcp", "_nslogger-ssl._tcp")
    def test_dns_sd_publisher_can_be_forced_on_macos(self):
        listener = NSLoggerListener(
            bonjour=True,
            bonjour_name="bazinga",
            bonjour_publisher="dns-sd",
        )

        class DummyDnsSdPublisher:
            def __init__(self, service_name, service_types, port, filter_clients, on_debug):
                self.service_name = service_name
                self.service_types = service_types
                self.port = port
                self.filter_clients = filter_clients

        with patch("cli_anything.nslogger.core.listener.sys.platform", "darwin"), \
                patch("cli_anything.nslogger.core.listener._NativeBonjourPublisher") as native_publisher, \
                patch("cli_anything.nslogger.core.listener._DnsSdBonjourPublisher", DummyDnsSdPublisher):
            publisher = listener._start_bonjour("192.168.10.1")

        assert isinstance(publisher, DummyDnsSdPublisher)
        assert native_publisher.call_count == 0
    def test_zeroconf_publisher_can_be_forced_on_macos(self):
        listener = NSLoggerListener(
            bonjour=True,
            bonjour_name="bazinga",
            bonjour_publisher="zeroconf",
        )

        class DummyZeroconfPublisher:
            def __init__(self, service_name, service_types, port, local_ip, filter_clients):
                self.service_name = service_name
                self.service_types = service_types
                self.port = port
                self.local_ip = local_ip
                self.filter_clients = filter_clients

        with patch("cli_anything.nslogger.core.listener.sys.platform", "darwin"), \
                patch("cli_anything.nslogger.core.listener._ZeroconfBonjourPublisher", DummyZeroconfPublisher), \
                patch("cli_anything.nslogger.core.listener._DnsSdBonjourPublisher") as dns_sd_publisher:
            publisher = listener._start_bonjour("192.168.10.5")

        assert isinstance(publisher, DummyZeroconfPublisher)
        assert publisher.local_ip == "192.168.10.5"
        assert dns_sd_publisher.call_count == 0
