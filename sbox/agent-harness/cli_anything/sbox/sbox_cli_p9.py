# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _output, _output_error  # noqa: E402,E501
from .sbox_cli_p5 import scene  # noqa: E402,E501
# fmt: on


@scene.command("refs")
@click.argument("scene_path")
@click.pass_context
def scene_refs(ctx, scene_path):
    """Extract every asset reference from a scene, grouped by category."""
    try:
        result = scene_mod.extract_asset_refs(scene_path)

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


@scene.command("bulk-modify")
@click.argument("scene_path")
@click.option("--has-component", default=None, help="Filter: object has this component")
@click.option("--has-tag", default=None, help="Filter: object has this tag")
@click.option("--name-match", default=None, help="Filter: Name contains substring")
@click.option("--name-regex", default=None, help="Filter: Name matches regex")
@click.option("--in-bounds", default=None, help="Filter: position inside AABB")
@click.option(
    "--filter-enabled/--filter-disabled",
    "filter_enabled",
    default=None,
    help="Filter by Enabled state",
)
@click.option("--position", "new_position", default=None, help="New Position 'x,y,z'")
@click.option("--rotation", "new_rotation", default=None, help="New Rotation 'x,y,z,w'")
@click.option("--scale", "new_scale", default=None, help="New Scale 'x,y,z'")
@click.option("--tags", "new_tags", default=None, help="New Tags string")
@click.option(
    "--enable/--disable", "new_enabled", default=None, help="Set Enabled state"
)
@click.pass_context
def scene_bulk_modify(
    ctx,
    scene_path,
    has_component,
    has_tag,
    name_match,
    name_regex,
    in_bounds,
    filter_enabled,
    new_position,
    new_rotation,
    new_scale,
    new_tags,
    new_enabled,
):
    """Apply the same modification to every object matching the filters."""
    try:
        result = scene_mod.bulk_modify_objects(
            scene_path,
            has_component=has_component,
            has_tag=has_tag,
            name_match=name_match,
            name_regex=name_regex,
            in_bounds=in_bounds,
            enabled_filter=filter_enabled,
            new_position=new_position,
            new_rotation=new_rotation,
            new_scale=new_scale,
            new_tags=new_tags,
            new_enabled=new_enabled,
        )
        _output(
            ctx,
            result,
            lambda d: (
                f"Modified {d['modified_count']} object(s); fields: {', '.join(d['modified_fields'])}"
            ),
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@scene.command("diff")
@click.argument("scene_a")
@click.argument("scene_b")
@click.pass_context
def scene_diff(ctx, scene_a, scene_b):
    """Structural diff between two scenes (objects added/removed/modified by Name)."""
    try:
        result = scene_mod.diff_scenes(scene_a, scene_b)

        def human(d):
            if d["identical"]:
                return f"Scenes are identical: {d['scene_a']} == {d['scene_b']}"
            lines = [f"Diff: {d['scene_a']} -> {d['scene_b']}"]
            if d["added"]:
                lines.append(f"  Added ({len(d['added'])}): {', '.join(d['added'])}")
            if d["removed"]:
                lines.append(
                    f"  Removed ({len(d['removed'])}): {', '.join(d['removed'])}"
                )
            if d["modified"]:
                lines.append(f"  Modified ({len(d['modified'])}):")
                for m in d["modified"]:
                    keys = list(m["changes"].keys())
                    lines.append(f"    {m['name']}: {', '.join(keys)}")
            if d.get("scene_property_changes"):
                lines.append(
                    f"  SceneProperties changes: {', '.join(d['scene_property_changes'].keys())}"
                )
            return "\n".join(lines)

        _output(ctx, result, human)
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))
