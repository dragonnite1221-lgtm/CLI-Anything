# ruff: noqa: F403, F405, E501
from .extract_tools_base import *  # noqa: F403

# fmt: off
from .extract_tools_p1 import _decode_js_string, _find_brace_end, _find_string_end, _skip_ws, _skip_ws_comma  # noqa: E402,E501
from .extract_tools_p2 import _split_top_level  # noqa: E402,E501
from .extract_tools_p3 import _parse_field  # noqa: E402,E501
# fmt: on


def _parse_schema_block(src: str) -> list[dict]:
    """Parse `{ foo: z.string()..., bar: z.number()..., }` into field dicts."""
    inner = src[1:-1].strip()
    if not inner:
        return []
    fields = _split_top_level(inner, ",")
    params: list[dict] = []
    for field in fields:
        field = field.strip().rstrip(",").strip()
        if not field or field.startswith("//"):
            continue
        p = _parse_field(field)
        if p:
            params.append(p)
    return params


def _coerce_default(raw: str, json_type: str):
    """Coerce a Zod ``.default(...)`` raw text into the JSON Schema type.

    The parser captures defaults as raw JS text (e.g. ``"false"``,
    ``"42"``, ``"\"auto\""``). We convert to the matching Python/JSON
    primitive so the bundled JSON Schema is type-correct.
    """
    raw = raw.strip()
    if json_type == "boolean":
        if raw == "true":
            return True
        if raw == "false":
            return False
        return raw
    if json_type in ("number", "integer"):
        try:
            if "." in raw:
                return float(raw)
            return int(raw)
        except ValueError:
            return raw
    if json_type == "null" or raw == "null":
        return None
    # String / array / object — try to strip quotes for plain string defaults
    if (raw.startswith('"') and raw.endswith('"')) or (
        raw.startswith("'") and raw.endswith("'")
    ):
        return raw[1:-1]
    return raw


def _param_to_jsonschema(param: dict) -> dict:
    schema: dict = {"type": param["type"]}
    if param.get("description"):
        schema["description"] = param["description"]
    if param.get("choices"):
        schema["enum"] = param["choices"]
    default = param.get("default")
    if default is not None:
        schema["default"] = _coerce_default(default, param["type"])
    return schema


def _parse_tool_block(source: str, start: int) -> dict | None:
    pos = start + len("server.tool(")
    pos = _skip_ws(source, pos)

    # Name
    if pos >= len(source) or source[pos] != '"':
        return None
    name_end = _find_string_end(source, pos)
    if name_end == -1:
        return None
    name = _decode_js_string(source[pos + 1 : name_end])
    pos = _skip_ws_comma(source, name_end + 1)

    # Description
    if pos >= len(source) or source[pos] != '"':
        return None
    desc_end = _find_string_end(source, pos)
    if desc_end == -1:
        return None
    description = _decode_js_string(source[pos + 1 : desc_end])
    pos = _skip_ws_comma(source, desc_end + 1)

    # Schema object
    if pos >= len(source) or source[pos] != "{":
        return None
    schema_end = _find_brace_end(source, pos)
    if schema_end == -1:
        return None
    schema_src = source[pos : schema_end + 1]
    params = _parse_schema_block(schema_src)
    pos = schema_end + 1

    properties: dict[str, dict] = {}
    required: list[str] = []
    for p in params:
        properties[p["name"]] = _param_to_jsonschema(p)
        if p["required"]:
            required.append(p["name"])

    return {
        "name": name,
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
        "_end": pos,
    }
