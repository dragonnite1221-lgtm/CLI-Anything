# ruff: noqa: F403, F405, E501
from .rms_cli_base import *  # noqa: F403
from .rms_cli_p9 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .rms_cli_p1 import _get_session, _get_token, _print_dict, _print_list, output, handle_error, cli  # noqa: F401,E501
from .rms_cli_p2 import repl, devices, devices_list, devices_get, devices_update, devices_delete, companies, companies_list  # noqa: F401,E501
from .rms_cli_p3 import companies_get, companies_create, companies_update, companies_delete, users, users_list, users_get, users_invite, users_update, users_delete, tags, tags_list, tags_get, tags_create  # noqa: F401,E501
from .rms_cli_p4 import tags_update, tags_delete, alerts, alerts_list, alerts_get, alerts_delete, alert_configs, alert_configs_list, alert_configs_get, alert_configs_create, alert_configs_update, alert_configs_delete, configs, configs_list, configs_get, configs_update  # noqa: F401,E501
from .rms_cli_p5 import remote_access, remote_access_list, remote_access_get, remote_access_create, remote_access_delete, logs, logs_list, logs_get, logs_delete, location, location_get, location_history, credits, credits_list, credits_transfer, credits_codes, files  # noqa: F401,E501
from .rms_cli_p6 import files_list, files_get, files_upload, files_delete, reports, reports_list, reports_get, reports_create, reports_delete, report_templates, report_templates_list, report_templates_get, report_templates_create, report_templates_update, report_templates_delete, hotspots  # noqa: F401,E501
from .rms_cli_p7 import hotspots_list, hotspots_get, hotspots_create, hotspots_update, hotspots_delete, passwords, passwords_get, passwords_update, smtp, smtp_list, smtp_get, smtp_create  # noqa: F401,E501
from .rms_cli_p8 import smtp_update, smtp_delete, auth, auth_test, auth_status, config_group, config_set, config_get, config_delete, config_path, session_group, session_status, session_clear  # noqa: F401,E501
from .rms_cli_p9 import session_history  # noqa: F401,E501
# fmt: on
