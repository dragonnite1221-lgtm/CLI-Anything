# ruff: noqa: F403, F405, E501
from .update_registry_dates_base import *  # noqa: F403
from .update_registry_dates_p3 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .update_registry_dates_p1 import REPO_ROOT, USER_AGENT, GITHUB_REPO_RE, GIT_URL_RE, SUBDIRECTORY_RE, _fetch_json, _fetch_last_modified, _git_log_timestamp, get_last_modified, get_github_repo_date, _extract_pypi_package  # noqa: F401,E501
from .update_registry_dates_p2 import get_pypi_date, _extract_npm_package, get_npm_date, _extract_install_subdirectory, _extract_skill_subdirectory, resolve_harness_path, extract_external_source_url, get_external_date  # noqa: F401,E501
from .update_registry_dates_p3 import get_cli_date, _load_registry  # noqa: F401,E501
# fmt: on
