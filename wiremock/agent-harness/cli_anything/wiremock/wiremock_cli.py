# ruff: noqa: F403, F405, E501
from .wiremock_cli_base import *  # noqa: F403


if __name__ == "__main__":
    cli()

# fmt: off
# re-export full surface
from .wiremock_cli_p1 import cli, stub, stub_list, stub_get, stub_create  # noqa: F401,E501
from .wiremock_cli_p2 import status, stub_quick, stub_delete, stub_reset, stub_save, stub_import, request, request_list  # noqa: F401,E501
from .wiremock_cli_p3 import request_find, request_count, request_unmatched, request_reset, scenario, scenario_list, scenario_set, scenario_reset, record  # noqa: F401,E501
from .wiremock_cli_p4 import record_start, record_stop, record_status, record_snapshot, settings, settings_get, settings_version, reset_all, shutdown  # noqa: F401,E501
# fmt: on
