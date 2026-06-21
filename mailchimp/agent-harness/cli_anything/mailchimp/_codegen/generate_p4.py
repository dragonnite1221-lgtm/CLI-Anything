# ruff: noqa: F403, F405, E501
from .generate_base import *  # noqa: F403

# fmt: off
from .generate_p1 import _tag_to_module  # noqa: E402,E501
from .generate_p3 import _generate_module  # noqa: E402,E501
# fmt: on


def generate(spec: dict, out_dir: Path = OUT_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    by_tag: dict[str, list[tuple[str, str, dict]]] = defaultdict(list)

    for path, path_item in spec.get("paths", {}).items():
        for method, operation in path_item.items():
            if method not in ("get", "post", "patch", "put", "delete"):
                continue
            if not isinstance(operation, dict):
                continue
            tags = operation.get("tags", ["misc"])
            tag = tags[0]
            if tag in _SKIP_TAGS:
                continue
            by_tag[tag].append((method, path, operation))

    generated: list[str] = []
    for tag, operations in sorted(by_tag.items()):
        module_name = _tag_to_module(tag)
        out_path = out_dir / f"{module_name}.py"
        code = _generate_module(tag, operations)
        out_path.write_text(code, encoding="utf-8")
        generated.append(module_name)
        print(
            f"  Generated {out_path.name} ({len(operations)} commands)", file=sys.stderr
        )

    # Write __init__.py that imports all groups
    init_lines = ['"""Auto-generated command groups for cli-anything-mailchimp."""', ""]
    for mod in sorted(generated):
        group_var = f"{mod}_group"
        init_lines.append(
            f"from cli_anything.mailchimp.commands.{mod} import {group_var}"
        )
    init_lines.append("")
    init_lines.append("ALL_GROUPS = [")
    for mod in sorted(generated):
        group_var = f"{mod}_group"
        init_lines.append(f"    {group_var},")
    init_lines.append("]")
    init_lines.append("")

    (out_dir / "__init__.py").write_text("\n".join(init_lines), encoding="utf-8")
    print(f"\nDone — {len(generated)} modules written to {out_dir}", file=sys.stderr)
