# ruff: noqa: F403, F405, E501
from .extract_tools_base import *  # noqa: F403

# fmt: off
from .extract_tools_p1 import _decode_js_string  # noqa: E402,E501
from .extract_tools_p2 import _TYPE_MAP, _find_matching_paren  # noqa: E402,E501
# fmt: on


def _parse_modifier_chain(text: str) -> dict:
    """Parse `.foo(args).bar(args)...` returning {method: args_str}.

    Walks the chain sequentially. For each `.method(...)` found, records
    the argument text (inner of the parens). For `.describe(...)`, also
    decodes the string literal if the arg looks like `"..."`.
    """
    result: dict = {}
    i = 0
    while i < len(text):
        c = text[i]
        if c in " \t\r\n":
            i += 1
            continue
        if c != ".":
            break  # end of modifier chain
        m = re.match(r"\.(\w+)\s*\(", text[i:])
        if not m:
            break
        method = m.group(1)
        arg_open = i + m.end() - 1  # position of '('
        arg_close = _find_matching_paren(text, arg_open)
        if arg_close == -1:
            break
        arg_content = text[arg_open + 1 : arg_close]
        if method == "describe":
            # Handle both double- and single-quoted string literals.
            dq_match = re.match(
                r'\s*"((?:[^"\\]|\\.)*)"\s*',
                arg_content,
            )
            sq_match = re.match(
                r"\s*'((?:[^'\\]|\\.)*)'\s*",
                arg_content,
            )
            if dq_match:
                arg_content = _decode_js_string(dq_match.group(1))
            elif sq_match:
                arg_content = _decode_js_string(sq_match.group(1))
        result[method] = arg_content
        i = arg_close + 1
    return result


def _parse_field(field: str) -> dict | None:
    """Parse one field: `name: z.TYPE(...).modifier().describe(...)`."""
    m = re.match(r"(\w+)\s*:\s*(.*)", field, re.DOTALL)
    if not m:
        return None
    name = m.group(1)
    value = m.group(2).strip()

    # Extract root Zod type
    root_match = re.match(r"z\.(?:coerce\.)?(\w+)", value)
    if not root_match:
        return None
    zod_type = root_match.group(1)
    json_type = _TYPE_MAP.get(zod_type, "string")

    # Skip past the root call's parens so we can look at modifiers alone.
    root_args_text = ""
    modifier_text = ""
    after_root_start = root_match.end()
    if after_root_start < len(value) and value[after_root_start] == "(":
        close_pos = _find_matching_paren(value, after_root_start)
        if close_pos == -1:
            return None
        root_args_text = value[after_root_start + 1 : close_pos]
        modifier_text = value[close_pos + 1 :]
    else:
        # Root has no call (e.g. `z.string` without parens) — unusual but handled
        modifier_text = value[after_root_start:]

    # Parse modifier chain at top level only (nested modifiers inside
    # root_args_text are ignored, which is the fix for the old nested-describe bug).
    modifiers = _parse_modifier_chain(modifier_text)

    optional = "optional" in modifiers
    nullable = "nullable" in modifiers
    default_val = modifiers.get("default")
    description = modifiers.get("describe", "")

    # Enum / literal choices
    choices = None
    if zod_type == "enum":
        enum_match = re.match(r"\s*\[([^\]]*)\]", root_args_text, re.DOTALL)
        if enum_match:
            choices = []
            for s in enum_match.group(1).split(","):
                s = s.strip().strip('"').strip("'")
                if s:
                    choices.append(s)
    elif zod_type == "literal":
        lit_match = re.match(r'\s*"((?:[^"\\]|\\.)*)"', root_args_text)
        if lit_match:
            choices = [_decode_js_string(lit_match.group(1))]

    is_required = not (optional or nullable or default_val is not None)

    return {
        "name": name,
        "type": json_type,
        "description": description,
        "required": is_required,
        "default": default_val.strip() if default_val else None,
        "choices": choices,
    }
