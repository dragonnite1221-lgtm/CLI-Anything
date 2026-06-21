# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _format_status_block, _format_table, _output, _output_error, _resolve_project_dir  # noqa: E402,E501
from .sbox_cli_p2 import cli  # noqa: E402,E501
from .sbox_cli_p3 import project  # noqa: E402,E501
# fmt: on


@project.command("validate")
@click.option("--no-refs", is_flag=True, help="Skip broken-reference detection")
@click.option("--no-guids", is_flag=True, help="Skip duplicate-GUID detection")
@click.option("--no-inputs", is_flag=True, help="Skip Input.config sanity checks")
@click.pass_context
def project_validate(ctx, no_refs, no_guids, no_inputs):
    """Validate project: broken asset refs, duplicate GUIDs, malformed inputs."""
    try:
        proj_dir = _resolve_project_dir(ctx)
        if not proj_dir:
            _output_error(ctx, "No project found")
            return
        result = validate_mod.validate_project(
            proj_dir,
            check_refs=not no_refs,
            check_guids=not no_guids,
            check_inputs=not no_inputs,
        )

        def human(d):
            lines = [
                f"Project validation: {'OK' if d['ok'] else 'FAIL'} ({d['issue_count']} issue(s))"
            ]
            for ref in d.get("broken_refs", []):
                lines.append(
                    f"  [broken-ref] {ref['file']} -> {ref['ref']} ({ref['category']})"
                )
            for guid in d.get("duplicate_guids", []):
                lines.append(f"  [duplicate-guid] {guid['file']} -> {guid['guid']}")
                for occ in guid.get("occurrences", []):
                    lines.append(f"      {occ}")
            for inp in d.get("invalid_inputs", []):
                lines.append(
                    f"  [input] {inp.get('file', '?')}: {inp.get('issue', '?')}"
                )
            return "\n".join(lines)

        _output(ctx, result, human)
        # Validation failure must exit non-zero so CI can gate on this command.
        if not result.get("ok", True) and not ctx.obj.get("repl"):
            sys.exit(1)
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@cli.group()
@click.pass_context
def scene(ctx):
    """Manage s&box scenes."""
    pass


@scene.command("new")
@click.option("--name", default="minimal", help="Scene name")
@click.option("-o", "--output", "output_path", default=None, help="Output file path")
@click.option(
    "--no-defaults",
    is_flag=True,
    help="Skip default objects (Sun, Skybox, Plane, Camera)",
)
@click.pass_context
def scene_new(ctx, name, output_path, no_defaults):
    """Create a new scene."""
    try:
        if not output_path:
            output_path = f"{name}.scene"
        result = scene_mod.create_scene(
            name=name,
            output_path=output_path,
            include_defaults=not no_defaults,
        )
        info = {
            "name": name,
            "path": os.path.abspath(output_path),
            "objects": len(result.get("GameObjects", [])),
            "defaults_included": not no_defaults,
        }
        _output(
            ctx, info, lambda d: _format_status_block(d, f"Scene '{d['name']}' created")
        )
    except Exception as exc:
        _output_error(ctx, str(exc))


@scene.command("info")
@click.argument("scene_path")
@click.pass_context
def scene_info(ctx, scene_path):
    """Show scene info."""
    try:
        result = scene_mod.get_scene_info(scene_path)
        _output(
            ctx,
            result,
            lambda d: _format_status_block(d, f"Scene: {d.get('title', '')}"),
        )
    except Exception as exc:
        _output_error(ctx, str(exc))


@scene.command("list")
@click.argument("scene_path")
@click.pass_context
def scene_list(ctx, scene_path):
    """List GameObjects in a scene."""
    try:
        objects = scene_mod.list_objects(scene_path)
        if ctx.obj.get("json"):
            _output(ctx, objects)
        else:
            rows = []
            for obj in objects:
                rows.append(
                    {
                        "guid": obj["guid"][:12] + "...",
                        "name": obj["name"],
                        "position": obj["position"],
                        "components": ", ".join(
                            t.split(".")[-1] for t in obj["component_types"]
                        ),
                    }
                )
            click.echo(_format_table(rows, ["guid", "name", "position", "components"]))
    except Exception as exc:
        _output_error(ctx, str(exc))
