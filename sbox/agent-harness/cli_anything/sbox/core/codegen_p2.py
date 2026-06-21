# ruff: noqa: F403, F405, E501
from .codegen_base import *  # noqa: F403

# fmt: off
from .codegen_p1 import _format_method, _format_property, _format_rpc_method  # noqa: E402,E501
# fmt: on


def generate_component(
    class_name: str,
    properties: Optional[list[dict]] = None,
    lifecycle_methods: Optional[list[str]] = None,
    interfaces: Optional[list[str]] = None,
    is_networked: bool = False,
    namespace: Optional[str] = None,
    rpc_methods: Optional[list[dict]] = None,
) -> dict:
    """Generate a C# component class file.

    Args:
        class_name: PascalCase name, e.g. "PlayerController".
        properties: List of dicts with keys:
            name (str), type (str), default (str|None),
            category (str|None), range_min (float|None), range_max (float|None).
            Type examples: "float", "int", "string", "GameObject", "Vector3", "Model".
        lifecycle_methods: Method names to override, e.g. ["OnUpdate", "OnFixedUpdate", "OnStart"].
        interfaces: Interface list, e.g. ["Component.ITriggerListener", "Component.IDamageable"].
        is_networked: If True the class is partial (not sealed) and properties get [Sync].
        namespace: Optional namespace wrapper.
        rpc_methods: List of dicts with 'name' (str) and 'type' (str: 'Broadcast',
            'Host', or 'Owner'). Forces is_networked=True when provided.

    Returns:
        Dict with keys: filename, content, class_name.
    """
    properties = properties or []
    lifecycle_methods = lifecycle_methods or []
    interfaces = interfaces or []
    rpc_methods = rpc_methods or []

    # RPC methods require networking support
    if rpc_methods:
        is_networked = True

    lines: list[str] = []
    lines.append("using Sandbox;")
    lines.append("")

    # Namespace open
    if namespace:
        lines.append(f"namespace {namespace}")
        lines.append("{")

    indent = "\t" if namespace else ""

    # Class declaration
    modifier = "partial" if is_networked else "sealed"
    base_parts = ["Component"] + interfaces
    base = ", ".join(base_parts)
    lines.append(f"{indent}public {modifier} class {class_name} : {base}")
    lines.append(f"{indent}{{")

    # Properties
    for prop in properties:
        prop_str = _format_property(prop, is_networked=is_networked)
        for pline in prop_str.split("\n"):
            lines.append(f"{indent}\t{pline}")

    # Blank line between properties and methods
    if properties and lifecycle_methods:
        lines.append("")

    # Lifecycle methods
    for i, method_name in enumerate(lifecycle_methods):
        body = ""
        if is_networked and method_name == "OnFixedUpdate":
            body = "if ( IsProxy ) return;"
        method_str = _format_method(method_name, body=body)
        for mline in method_str.split("\n"):
            lines.append(f"{indent}\t{mline}")
        if i < len(lifecycle_methods) - 1:
            lines.append("")

    # RPC method stubs
    if rpc_methods:
        if lifecycle_methods:
            lines.append("")
        for j, rpc in enumerate(rpc_methods):
            rpc_str = _format_rpc_method(rpc)
            for rline in rpc_str.split("\n"):
                lines.append(f"{indent}\t{rline}")
            if j < len(rpc_methods) - 1:
                lines.append("")

    lines.append(f"{indent}}}")

    # Namespace close
    if namespace:
        lines.append("}")

    lines.append("")
    content = "\r\n".join(lines)

    return {
        "filename": f"{class_name}.cs",
        "content": content,
        "class_name": class_name,
    }
