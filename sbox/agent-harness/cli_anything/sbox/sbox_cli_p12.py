# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _output, _output_error  # noqa: E402,E501
from .sbox_cli_p2 import cli  # noqa: E402,E501
from .sbox_cli_p10 import prefab  # noqa: E402,E501
# fmt: on


@prefab.command("modify-component")
@click.argument("prefab_path")
@click.option("--component-guid", default=None, help="Component GUID")
@click.option(
    "--component-type", default=None, help="Component type (e.g. Sandbox.Rigidbody)"
)
@click.option("--object-guid", default=None, help="Restrict search to a single object")
@click.option("--properties", required=True, help="Properties to set as JSON")
@click.pass_context
def prefab_modify_component(
    ctx, prefab_path, component_guid, component_type, object_guid, properties
):
    """Modify properties of a component within a prefab."""
    try:
        import json as json_mod

        props = json_mod.loads(properties)
        result = prefab_mod.modify_component(
            prefab_path,
            component_guid=component_guid,
            component_type=component_type,
            object_guid=object_guid,
            properties=props,
        )
        _output(
            ctx,
            result,
            lambda d: f"Modified {d['component_type']}: {', '.join(d['updated_keys'])}",
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@prefab.command("diff")
@click.argument("prefab_a")
@click.argument("prefab_b")
@click.pass_context
def prefab_diff(ctx, prefab_a, prefab_b):
    """Structural diff between two prefabs (root + children by Name)."""
    try:
        result = prefab_mod.diff_prefabs(prefab_a, prefab_b)

        def human(d):
            if d["identical"]:
                return f"Prefabs are identical: {d['prefab_a']} == {d['prefab_b']}"
            lines = [f"Diff: {d['prefab_a']} -> {d['prefab_b']}"]
            if d.get("root_changes"):
                keys = list(d["root_changes"]["changes"].keys())
                lines.append(f"  Root changed: {', '.join(keys)}")
            if d["children_added"]:
                lines.append(
                    f"  Children added ({len(d['children_added'])}): {', '.join(d['children_added'])}"
                )
            if d["children_removed"]:
                lines.append(
                    f"  Children removed ({len(d['children_removed'])}): {', '.join(d['children_removed'])}"
                )
            if d["children_modified"]:
                lines.append(f"  Children modified ({len(d['children_modified'])}):")
                for m in d["children_modified"]:
                    keys = list(m["changes"].keys())
                    lines.append(f"    {m['name']}: {', '.join(keys)}")
            return "\n".join(lines)

        _output(ctx, result, human)
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@cli.group()
@click.pass_context
def codegen(ctx):
    """Generate s&box C# code."""
    pass
