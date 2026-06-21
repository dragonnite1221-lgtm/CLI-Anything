# ruff: noqa: F403, F405, E501
from .extract_tools_base import *  # noqa: F403
from .extract_tools_p5 import main  # noqa: F401


if __name__ == "__main__":
    sys.exit(main())

# fmt: off
# re-export full surface
from .extract_tools_p1 import _decode_js_string, _skip_ws, _skip_ws_comma, _find_string_end, _find_brace_end  # noqa: F401,E501
from .extract_tools_p2 import _split_top_level, _TYPE_MAP, _find_matching_paren  # noqa: F401,E501
from .extract_tools_p3 import _parse_modifier_chain, _parse_field  # noqa: F401,E501
from .extract_tools_p4 import _parse_schema_block, _coerce_default, _param_to_jsonschema, _parse_tool_block  # noqa: F401,E501
from .extract_tools_p5 import extract_tools, _extract_pkg_version  # noqa: F401,E501
# fmt: on
