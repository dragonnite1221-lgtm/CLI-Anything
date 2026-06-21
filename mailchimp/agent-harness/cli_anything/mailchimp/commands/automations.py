# ruff: noqa: F403, F405, E501
from .automations_base import *  # noqa: F403

# fmt: off
# re-export full surface
from .automations_p1 import _parse_json_option, automations_group, _cmd_list_, _cmd_create, _cmd_get, _cmd_archive  # noqa: F401,E501
from .automations_p2 import _cmd_pause_all_emails, _cmd_start_all_emails, _cmd_list_automations_id_emails, _cmd_delete, _cmd_get_automations_id_emails_id, _cmd_update  # noqa: F401,E501
from .automations_p3 import _cmd_pause, _cmd_start, _cmd_list_automations_id_emails_id_queue, _cmd_create_automations_id_emails_id_queue, _cmd_get_automations_id_emails_id_queue_id  # noqa: F401,E501
from .automations_p4 import _cmd_list_automations_id_removed_subscribers, _cmd_create_automations_id_removed_subscribers, _cmd_get_automations_id_removed_subscribers_id  # noqa: F401,E501
# fmt: on
