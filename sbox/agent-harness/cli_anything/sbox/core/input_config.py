# ruff: noqa: F403, F405, E501
from .input_config_base import *  # noqa: F403

# fmt: off
# re-export full surface
from .input_config_p1 import load_input_config, save_input_config, list_actions, add_action, remove_action  # noqa: F401,E501
from .input_config_p2 import set_action, get_default_input_config  # noqa: F401,E501
# fmt: on
