# ruff: noqa: F403, F405, E501
from .codegen_base import *  # noqa: F403


def _format_property(prop: dict, is_networked: bool = False) -> str:
    """Format a single C# property with attributes.

    Args:
        prop: Dict with keys: name, type, and optionally default, category,
              range_min, range_max.
        is_networked: If True, adds [Sync] attribute before [Property].

    Returns:
        Multi-line string (no leading/trailing blank lines) with the
        attribute(s) and auto-property declaration.
    """
    name: str = prop["name"]
    prop_type: str = prop["type"]
    default = prop.get("default")
    category = prop.get("category")
    range_min = prop.get("range_min")
    range_max = prop.get("range_max")

    lines: list[str] = []

    # Sync attribute for networked properties (always on its own line)
    # NetList and NetDictionary are self-syncing - skip [Sync] for them
    if (
        is_networked
        and not prop_type.startswith("NetList<")
        and not prop_type.startswith("NetDictionary<")
    ):
        lines.append("[Sync]")

    # Property attribute with optional modifiers
    attr_inner_parts: list[str] = []
    if category:
        attr_inner_parts.append(f'Category = "{category}"')
    if range_min is not None and range_max is not None:
        attr_inner_parts.append(f"MinMax( {range_min}, {range_max} )")

    has_extra_attrs = bool(attr_inner_parts)

    if has_extra_attrs:
        attr_inner = ", ".join(attr_inner_parts)
        prop_attr = f"[Property( {attr_inner} )]"
    else:
        prop_attr = "[Property]"

    # Build the property declaration
    default_str = ""
    if default is not None:
        default_str = f" = {default};"

    decl = f"public {prop_type} {name} {{ get; set; }}{default_str}"

    # Simple properties: attribute and declaration on one line
    # Complex properties (extra attrs or networked): attribute on separate line
    if is_networked or has_extra_attrs:
        lines.append(prop_attr)
        lines.append(decl)
    else:
        lines.append(f"{prop_attr} {decl}")

    return "\n".join(lines)


def _format_method(
    name: str,
    body: str = "",
    params: str = "",
    return_type: str = "void",
    is_override: bool = True,
) -> str:
    """Format a C# method with proper s&box style.

    Args:
        name: Method name, e.g. "OnUpdate".
        body: Method body lines (newline-separated). Empty string for empty body.
        params: Parameter list string, e.g. "float delta, int count".
        return_type: Return type, default "void".
        is_override: If True, uses "protected override" modifier.

    Returns:
        Multi-line string with the full method definition using Allman braces.
    """
    modifier = "protected override" if is_override else "public"
    signature = (
        f"{modifier} {return_type} {name}( {params} )"
        if params
        else f"{modifier} {return_type} {name}()"
    )

    lines: list[str] = []
    lines.append(signature)
    lines.append("{")

    if body:
        for bline in body.split("\n"):
            lines.append(f"\t{bline}")

    lines.append("}")

    return "\n".join(lines)


def _format_rpc_method(rpc: dict) -> str:
    """Format an RPC method stub with the appropriate attribute.

    Args:
        rpc: Dict with 'name' (str) and 'type' (str: 'Broadcast', 'Host', or 'Owner').
    """
    rpc_type = rpc.get("type", "Broadcast")
    name = rpc.get("name", "RpcMethod")

    attr = f"[Rpc.{rpc_type}]"
    lines = []
    lines.append(f"{attr}")
    lines.append(f"public void {name}()")
    lines.append("{")
    lines.append("}")
    return "\n".join(lines)
