# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403
from .n8n_cli_p18 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .n8n_cli_p1 import _safe_filename, _INTERNAL_FIELDS, _conn, _json_flag, _clean_for_api, _auto_snapshot, _load_json_arg, cli, repl  # noqa: F401,E501
from .n8n_cli_p10 import template_deploy  # noqa: F401,E501
from .n8n_cli_p11 import workflow_validate  # noqa: F401,E501
from .n8n_cli_p12 import workflow_autofix  # noqa: F401,E501
from .n8n_cli_p13 import workflow_patch  # noqa: F401,E501
from .n8n_cli_p14 import health_check, workflow_versions_, versions_list  # noqa: F401,E501
from .n8n_cli_p15 import versions_rollback, versions_show, versions_diff, versions_prune  # noqa: F401,E501
from .n8n_cli_p16 import versions_stats, workflow_test, node_, node_search  # noqa: F401,E501
from .n8n_cli_p17 import node_info, workflow_scaffold, workflow_patterns, expression_validate  # noqa: F401,E501
from .n8n_cli_p2 import config_, config_show, config_set, config_test, install_completions, workflow_, workflow_list  # noqa: F401,E501
from .n8n_cli_p3 import workflow_search, workflow_get, workflow_create, workflow_update, workflow_delete, workflow_activate, workflow_deactivate, workflow_tags, workflow_set_tags, workflow_transfer  # noqa: F401,E501
from .n8n_cli_p4 import workflow_export, workflow_import, workflow_backup_all  # noqa: F401,E501
from .n8n_cli_p5 import workflow_restore_all, workflow_diff  # noqa: F401,E501
from .n8n_cli_p6 import workflow_bulk_activate, workflow_bulk_deactivate, execution_, execution_list, execution_get, execution_delete, execution_retry  # noqa: F401,E501
from .n8n_cli_p7 import execution_errors, execution_watch  # noqa: F401,E501
from .n8n_cli_p8 import status_dashboard, credential_, credential_create, credential_delete, credential_schema, credential_transfer, variable_, variable_list, variable_create  # noqa: F401,E501
from .n8n_cli_p9 import variable_update, variable_delete, tag_, tag_list, tag_get, tag_create, tag_update, tag_delete, template_, template_search, template_get  # noqa: F401,E501
# fmt: on
