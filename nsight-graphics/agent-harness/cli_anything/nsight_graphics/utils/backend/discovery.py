# ruff: noqa: F403, F405, E501
from .discovery_base import *  # noqa: F403

# fmt: off
# re-export full surface
from .discovery_p1 import _scan_directory, _candidate_dirs_from_env, _fixed_windows_drive_roots, _default_windows_install_dirs  # noqa: F401,E501
from .discovery_p2 import _read_registry_installations, _normalized_install_key, _override_value, detect_tool_mode  # noqa: F401,E501
from .discovery_p3 import discover_binaries, _primary_executable  # noqa: F401,E501
from .discovery_p4 import list_installations  # noqa: F401,E501
from .discovery_p5 import get_version, probe_installation  # noqa: F401,E501
# fmt: on
from . import discovery_base as _coupbase  # noqa: E402

_coupbase._COUP_GLOBALS = globals()  # noqa: E402
