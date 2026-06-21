# ruff: noqa: F403, F405, E501
from .codegen_base import *  # noqa: F403


def generate_razor(
    class_name: str,
    inherits: str = "PanelComponent",
    properties: Optional[list[dict]] = None,
    root_class: Optional[str] = None,
    namespace: Optional[str] = None,
) -> dict:
    """Generate a Razor UI component (.razor) and its stylesheet (.razor.scss).

    Args:
        class_name: PascalCase name, e.g. "HudPanel".
        inherits: Base class - "PanelComponent", "Panel", etc.
        properties: List of property dicts with 'name' and 'type' keys.
        root_class: CSS class for root element. Defaults to kebab-case of class_name.
        namespace: Optional namespace.

    Returns:
        Dict with filename, content, class_name, scss_filename, scss_content.
    """
    if properties is None:
        properties = []
    if root_class is None:
        # Convert PascalCase to kebab-case
        import re

        root_class = re.sub(r"(?<!^)(?=[A-Z])", "-", class_name).lower()

    # Build .razor content
    lines = []
    lines.append("@using Sandbox;")
    lines.append("@using Sandbox.UI;")
    if namespace:
        lines.append(f"@namespace {namespace}")
    lines.append(f"@inherits {inherits}")
    lines.append("")
    lines.append(f'<root class="{root_class}">')
    lines.append('\t<div class="content">')
    lines.append("\t</div>")
    lines.append("</root>")
    lines.append("")
    lines.append("@code")
    lines.append("{")

    # Properties
    for prop in properties:
        pname = prop.get("name", "MyProperty")
        ptype = prop.get("type", "string")
        pdefault = prop.get("default", None)
        default_str = f" = {pdefault};" if pdefault is not None else ";"
        lines.append(
            f"\t[Property] public {ptype} {pname} {{ get; set; }}{default_str}"
        )

    if properties:
        lines.append("")

    # BuildHash
    if properties:
        prop_names = [p.get("name", "MyProperty") for p in properties]
        # System.HashCode.Combine supports up to 8 args
        if len(prop_names) <= 8:
            hash_args = ", ".join(prop_names)
            lines.append(
                f"\tprotected override int BuildHash() => System.HashCode.Combine( {hash_args} );"
            )
        else:
            # Chain for more than 8
            lines.append("\tprotected override int BuildHash()")
            lines.append("\t{")
            lines.append("\t\tvar hash = new System.HashCode();")
            for pname in prop_names:
                lines.append(f"\t\thash.Add( {pname} );")
            lines.append("\t\treturn hash.ToHashCode();")
            lines.append("\t}")

    lines.append("}")
    lines.append("")

    content = "\r\n".join(lines)

    # Build .razor.scss content
    scss_lines = []
    scss_lines.append(f".{root_class}")
    scss_lines.append("{")
    scss_lines.append("\tposition: absolute;")
    scss_lines.append("\twidth: 100%;")
    scss_lines.append("\theight: 100%;")
    scss_lines.append("\tpointer-events: none;")
    scss_lines.append("")
    scss_lines.append("\t> .content")
    scss_lines.append("\t{")
    scss_lines.append("\t\tflex-direction: column;")
    scss_lines.append("\t}")
    scss_lines.append("}")
    scss_lines.append("")

    scss_content = "\r\n".join(scss_lines)

    razor_filename = f"{class_name}.razor"
    scss_filename = f"{class_name}.razor.scss"

    return {
        "filename": razor_filename,
        "content": content,
        "class_name": class_name,
        "scss_filename": scss_filename,
        "scss_content": scss_content,
    }
