# ruff: noqa: F403, F405, E501
from .generate_base import *  # noqa: F403


if __name__ == "__main__":
    spec = load_spec()
    generate(spec)

# fmt: off
# re-export full surface
from .generate_p1 import _slugify, _safe_name, _tag_to_module, _tag_to_group, _infer_command_name, _dedup_suffix, _param_type_to_click, _click_help_text, _collect_params  # noqa: F401,E501
from .generate_p2 import _generate_command_func  # noqa: F401,E501
from .generate_p3 import _generate_module, load_spec  # noqa: F401,E501
from .generate_p4 import generate  # noqa: F401,E501
# fmt: on
