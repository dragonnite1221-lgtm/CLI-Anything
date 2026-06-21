# ruff: noqa: F403, F405, E501
from .codegen_base import *  # noqa: F403


def generate_class(
    class_name: str,
    base_class: Optional[str] = None,
    is_static: bool = False,
    properties: Optional[list[dict]] = None,
    methods: Optional[list[dict]] = None,
    namespace: Optional[str] = None,
) -> dict:
    """Generate a plain C# class (not a Component subclass).

    Args:
        class_name: PascalCase name.
        base_class: Optional base class to inherit from.
        is_static: If True, generates a static class (no instantiation).
        properties: List of dicts with name, type, default keys.
        methods: List of dicts with name, return_type, params, body, is_static keys.
        namespace: Optional namespace wrapper.

    Returns:
        Dict with filename, content, class_name.
    """
    if properties is None:
        properties = []
    if methods is None:
        methods = []

    lines = []
    lines.append("using Sandbox;")
    lines.append("")

    indent = ""
    if namespace:
        lines.append(f"namespace {namespace}")
        lines.append("{")
        indent = "\t"

    # Class declaration
    static_kw = "static " if is_static else ""
    if base_class:
        lines.append(f"{indent}public {static_kw}class {class_name} : {base_class}")
    else:
        lines.append(f"{indent}public {static_kw}class {class_name}")
    lines.append(f"{indent}{{")

    # Properties
    for prop in properties:
        pname = prop.get("name", "MyProperty")
        ptype = prop.get("type", "string")
        pdefault = prop.get("default", None)
        static_prop = "static " if is_static else ""
        if pdefault is not None:
            lines.append(
                f"{indent}\tpublic {static_prop}{ptype} {pname} {{ get; set; }} = {pdefault};"
            )
        else:
            lines.append(
                f"{indent}\tpublic {static_prop}{ptype} {pname} {{ get; set; }}"
            )

    if properties and methods:
        lines.append("")

    # Methods
    for method in methods:
        mname = method.get("name", "DoSomething")
        mreturn = method.get("return_type", "void")
        mparams = method.get("params", "")
        mbody = method.get("body", "")
        mstatic = "static " if method.get("is_static", is_static) else ""
        lines.append(f"{indent}\tpublic {mstatic}{mreturn} {mname}( {mparams} )")
        lines.append(f"{indent}\t{{")
        if mbody:
            for bline in mbody.split("\n"):
                lines.append(f"{indent}\t\t{bline}")
        lines.append(f"{indent}\t}}")

    lines.append(f"{indent}}}")

    if namespace:
        lines.append("}")

    lines.append("")

    content = "\r\n".join(lines)

    return {
        "filename": f"{class_name}.cs",
        "content": content,
        "class_name": class_name,
    }
