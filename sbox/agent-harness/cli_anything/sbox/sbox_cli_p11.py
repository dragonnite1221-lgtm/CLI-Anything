# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _output, _output_error, _resolve_project_dir  # noqa: E402,E501
from .sbox_cli_p10 import prefab  # noqa: E402,E501
# fmt: on


@prefab.command("add-component")
@click.argument("prefab_path")
@click.argument("component_type")
@click.option("--properties", default=None, help="Component properties as JSON")
@click.pass_context
def prefab_add_component(ctx, prefab_path, component_type, properties):
    """Add a component to a prefab's root object."""
    try:
        import json as json_mod
        import uuid as uuid_mod
        import copy as copy_mod

        props = json_mod.loads(properties) if properties else {}
        data = prefab_mod.load_prefab(prefab_path)
        root = data.get("RootObject", {})
        comps = root.get("Components", [])
        from cli_anything.sbox.core.scene import COMPONENT_PRESETS

        if component_type in COMPONENT_PRESETS:
            comp = copy_mod.deepcopy(COMPONENT_PRESETS[component_type])
        else:
            comp = {"__type": component_type}
        comp["__guid"] = str(uuid_mod.uuid4())
        comp.update(props)
        comps.append(comp)
        root["Components"] = comps
        data["RootObject"] = root
        prefab_mod.save_prefab(prefab_path, data)
        _output(
            ctx,
            {"guid": comp["__guid"], "type": comp["__type"], "prefab": prefab_path},
            lambda d: f"Added {d['type']} ({d['guid']}) to prefab",
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@prefab.command("remove-component")
@click.argument("prefab_path")
@click.option("--component-guid", default=None, help="Component GUID to remove")
@click.option("--component-type", default=None, help="Component type to remove")
@click.pass_context
def prefab_remove_component(ctx, prefab_path, component_guid, component_type):
    """Remove a component from a prefab's root object."""
    try:
        if not component_guid and not component_type:
            _output_error(ctx, "Must provide --component-guid or --component-type")
            return
        data = prefab_mod.load_prefab(prefab_path)
        root = data.get("RootObject", {})
        comps = root.get("Components", [])
        original_count = len(comps)
        if component_guid:
            comps = [c for c in comps if c.get("__guid") != component_guid]
        elif component_type:
            comps = [c for c in comps if c.get("__type") != component_type]
        removed = original_count > len(comps)
        root["Components"] = comps
        data["RootObject"] = root
        prefab_mod.save_prefab(prefab_path, data)
        _output(
            ctx,
            {"removed": removed},
            lambda d: f"Component {'removed' if d['removed'] else 'not found'}",
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@prefab.command("list")
@click.pass_context
def prefab_list(ctx):
    """List prefabs in the project."""
    try:
        project_dir = _resolve_project_dir(ctx)
        if not project_dir:
            _output_error(ctx, "No project found")
            return
        from cli_anything.sbox.core import export as export_mod_local

        assets = export_mod_local.list_assets(project_dir, asset_type="prefab")
        _output(ctx, assets)
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@prefab.command("refs")
@click.argument("prefab_path")
@click.pass_context
def prefab_refs(ctx, prefab_path):
    """Extract every asset reference from a prefab, grouped by category."""
    try:
        result = prefab_mod.extract_asset_refs(prefab_path)

        def human(d):
            if not d:
                return "(no asset references)"
            lines = []
            for category in sorted(d.keys()):
                lines.append(f"{category} ({len(d[category])}):")
                for ref in d[category]:
                    lines.append(f"  {ref}")
            return "\n".join(lines)

        _output(ctx, result, human)
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))
