# ruff: noqa: F403, F405, E501
from .adguardhome_cli_base import *  # noqa: F403
from .adguardhome_cli_p5 import main  # noqa: F401

# fmt: off
# re-export full surface
from .adguardhome_cli_p1 import make_client, output, cli, repl, config  # noqa: F401,E501
from .adguardhome_cli_p2 import config_show, config_save, config_test, server_, server_status, server_version, server_restart, filter_, filter_list, filter_status, filter_toggle, filter_add, filter_remove  # noqa: F401,E501
from .adguardhome_cli_p3 import filter_enable, filter_disable, filter_refresh, blocking, parental, parental_status, parental_enable, parental_disable, safebrowsing, safebrowsing_status, safebrowsing_enable, safebrowsing_disable, safesearch, safesearch_status, safesearch_enable, safesearch_disable, blocked_services, blocked_services_list, blocked_services_set, clients_  # noqa: F401,E501
from .adguardhome_cli_p4 import clients_list, clients_add, clients_remove, clients_show, stats_, stats_show, stats_reset, stats_config, log_, log_show, log_config, log_clear, rewrite_, rewrite_list, rewrite_add, rewrite_remove  # noqa: F401,E501
from .adguardhome_cli_p5 import dhcp_, dhcp_status, dhcp_leases, dhcp_add_static, dhcp_remove_static, tls_, tls_status  # noqa: F401,E501
# fmt: on
