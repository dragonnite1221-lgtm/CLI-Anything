# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _format_status_block, _format_table, _output, _output_error  # noqa: E402,E501
from .sbox_cli_p5 import scene  # noqa: E402,E501
# fmt: on


@scene.command("set-navmesh")
@click.argument("scene_path")
@click.option(
    "--enabled/--disabled",
    "navmesh_enabled",
    default=None,
    help="Enable/disable NavMesh",
)
@click.option("--agent-height", type=float, default=None, help="Agent height")
@click.option("--agent-radius", type=float, default=None, help="Agent radius")
@click.option("--agent-step-size", type=float, default=None, help="Agent step size")
@click.option(
    "--agent-max-slope", type=float, default=None, help="Agent max slope (degrees)"
)
@click.pass_context
def scene_set_navmesh(
    ctx,
    scene_path,
    navmesh_enabled,
    agent_height,
    agent_radius,
    agent_step_size,
    agent_max_slope,
):
    """Configure NavMesh properties for a scene."""
    try:
        kwargs = {}
        if navmesh_enabled is not None:
            kwargs["navmesh_enabled"] = navmesh_enabled
        if agent_height is not None:
            kwargs["navmesh_agent_height"] = agent_height
        if agent_radius is not None:
            kwargs["navmesh_agent_radius"] = agent_radius
        if agent_step_size is not None:
            kwargs["navmesh_agent_step_size"] = agent_step_size
        if agent_max_slope is not None:
            kwargs["navmesh_agent_max_slope"] = agent_max_slope

        if not kwargs:
            _output_error(ctx, "No NavMesh properties specified")
            return

        result = scene_mod.set_navmesh_properties(scene_path, **kwargs)
        _output(ctx, result, lambda d: _format_status_block(d, "NavMesh Properties"))
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@scene.command("list-presets")
@click.pass_context
def scene_list_presets(ctx):
    """List available component preset names."""
    try:
        from cli_anything.sbox.core.scene import COMPONENT_PRESETS

        presets = [
            {"name": k, "type": v["__type"]} for k, v in COMPONENT_PRESETS.items()
        ]
        _output(ctx, presets)
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@scene.command("modify-component")
@click.argument("scene_path")
@click.argument("object_guid")
@click.option("--component-guid", default=None, help="Component GUID")
@click.option(
    "--component-type", default=None, help="Component type (e.g. Sandbox.Rigidbody)"
)
@click.option("--properties", required=True, help="Properties to set as JSON")
@click.pass_context
def scene_modify_component(
    ctx, scene_path, object_guid, component_guid, component_type, properties
):
    """Modify properties of an existing component."""
    try:
        import json as json_mod

        props = json_mod.loads(properties)
        result = scene_mod.modify_component(
            scene_path,
            object_guid,
            component_guid=component_guid,
            component_type=component_type,
            properties=props,
        )
        _output(
            ctx,
            result,
            lambda d: (
                f"Modified {d['component_type']} on {d['object_guid']}: {', '.join(d['updated_keys'])}"
            ),
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@scene.command("query")
@click.argument("scene_path")
@click.option(
    "--has-component", default=None, help="Filter by component (preset or full type)"
)
@click.option(
    "--has-tag", default=None, help="Filter by tag (single token in Tags string)"
)
@click.option("--name-match", default=None, help="Filter by Name substring")
@click.option("--name-regex", default=None, help="Filter by Name regex pattern")
@click.option(
    "--in-bounds", default=None, help="AABB filter: x_min,y_min,z_min,x_max,y_max,z_max"
)
@click.option(
    "--enabled/--disabled", "enabled", default=None, help="Filter by Enabled state"
)
@click.pass_context
def scene_query(
    ctx, scene_path, has_component, has_tag, name_match, name_regex, in_bounds, enabled
):
    """Find GameObjects matching one or more filters (AND-combined)."""
    try:
        results = scene_mod.query_objects(
            scene_path,
            has_component=has_component,
            has_tag=has_tag,
            name_match=name_match,
            name_regex=name_regex,
            in_bounds=in_bounds,
            enabled=enabled,
        )

        def human(rows):
            if not rows:
                return "(no matches)"
            return _format_table(
                [
                    {
                        "name": r["name"],
                        "guid": r["guid"][:8],
                        "position": r["position"],
                        "components": ",".join(r["component_types"])[:60],
                    }
                    for r in rows
                ],
                ["name", "guid", "position", "components"],
            )

        _output(ctx, results, human)
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))
