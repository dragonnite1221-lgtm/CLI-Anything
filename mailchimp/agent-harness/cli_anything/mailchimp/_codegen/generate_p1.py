# ruff: noqa: F403, F405, E501
from .generate_base import *  # noqa: F403


def _slugify(name: str) -> str:
    """Convert camelCase or PascalCase or space-separated to kebab-case."""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", name)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1-\2", s)
    s = s.replace(" ", "-").replace("_", "-").lower()
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def _safe_name(name: str) -> str:
    """Convert a string to a safe Python identifier (keywords and builtins get underscore suffix)."""
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if name and name[0].isdigit():
        name = "_" + name
    if keyword.iskeyword(name) or name in _BUILTIN_NAMES:
        name += "_"
    return name


def _tag_to_module(tag: str) -> str:
    return _slugify(tag).replace("-", "_")


def _tag_to_group(tag: str) -> str:
    return _slugify(tag)


def _infer_command_name(method: str, path: str, operation_id: str) -> str:
    """Derive a clean command name from the HTTP method and path."""
    # Action endpoints (POST to .../actions/xxx)
    action_match = re.search(r"/actions/([^/]+)$", path)
    if action_match:
        return _slugify(action_match.group(1))

    # Determine if this is a collection endpoint or single-resource by checking
    # whether the path ends with a path parameter.
    ends_with_param = bool(re.search(r"\{[^}]+\}$", path))

    if method == "get":
        return "get" if ends_with_param else "list"
    elif method == "post":
        return "create"
    elif method in ("patch", "put"):
        return "update"
    elif method == "delete":
        return "delete"
    else:
        return _slugify(operation_id)


def _dedup_suffix(cmd_name: str, path: str, operation_id: str, count: int) -> str:
    """Return a unique suffix for a colliding command name.

    Prefers a slug derived from the operationId over a raw path segment,
    because path segments are often path-param shaped ({list_id}) which
    produces confusing names like 'create-list-id'.
    """
    # Try a meaningful suffix from the operationId (strip the HTTP verb prefix)
    op_slug = _slugify(re.sub(r"^(get|post|patch|put|delete)", "", operation_id))
    if op_slug and op_slug != cmd_name:
        return f"{cmd_name}-{op_slug}"

    # Fall back to the last non-param path segment
    segments = [s for s in path.rstrip("/").split("/") if s and not s.startswith("{")]
    if segments:
        suffix = _slugify(segments[-1])
        if suffix and suffix != cmd_name:
            return f"{cmd_name}-{suffix}"

    return f"{cmd_name}-{count}"


def _param_type_to_click(param: dict) -> str:
    t = param.get("type", "string")
    if t == "integer":
        return "int"
    if t == "boolean":
        return "bool"
    return "str"


def _click_help_text(description: str) -> str:
    """Return a single-line Click help string without truncating useful API context."""
    first_line = description.split("\n")[0]
    return " ".join(first_line.replace('"', '\\"').split())


def _collect_params(
    operation: dict, path: str
) -> tuple[list[dict], list[dict], dict | None]:
    """Return (path_params, query_params, body_param) from operation."""
    params = operation.get("parameters", [])
    path_params = [p for p in params if p.get("in") == "path"]
    query_params = [p for p in params if p.get("in") == "query"]
    body_params = [p for p in params if p.get("in") == "body"]
    body = body_params[0] if body_params else None
    return path_params, query_params, body
