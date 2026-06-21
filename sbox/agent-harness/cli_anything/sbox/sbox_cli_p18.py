# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _format_status_block, _format_table, _output, _output_error, _resolve_project_dir  # noqa: E402,E501
from .sbox_cli_p17 import asset  # noqa: E402,E501
# fmt: on


@asset.command("info")
@click.argument("asset_path")
@click.pass_context
def asset_info(ctx, asset_path):
    """Show asset details."""
    try:
        result = export_mod.get_asset_info(asset_path)
        # _parse_json_asset embeds parse failures as json_info.error; surface
        # those so a malformed scene/prefab yields a non-zero exit code.
        json_info_error = (
            result.get("json_info", {}).get("error")
            if isinstance(result.get("json_info"), dict)
            else None
        )
        if json_info_error:
            _output_error(ctx, f"{result.get('name', asset_path)}: {json_info_error}")
            return
        _output(
            ctx,
            result,
            lambda d: _format_status_block(d, f"Asset: {d.get('name', '')}"),
        )
    except Exception as exc:
        _output_error(ctx, str(exc))


@asset.command("compile")
@click.argument("asset_path")
@click.pass_context
def asset_compile(ctx, asset_path):
    """Compile an asset using s&box resource compiler."""
    try:
        from cli_anything.sbox.utils import sbox_backend

        result = sbox_backend.run_resource_compiler(asset_path)
        if not result.get("success", False):
            rc = result.get("return_code", "?")
            stderr = (result.get("stderr") or "").strip()
            detail = f": {stderr}" if stderr else ""
            _output_error(
                ctx, f"Resource compilation failed (return code {rc}){detail}"
            )
            return
        _output(ctx, result, lambda d: f"Compiled: {d.get('asset_path', asset_path)}")
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@asset.command("find-refs")
@click.argument("asset_path")
@click.pass_context
def asset_find_refs(ctx, asset_path):
    """Find every scene/prefab in the project that references the given asset."""
    try:
        proj_dir = _resolve_project_dir(ctx)
        if not proj_dir:
            _output_error(ctx, "No project found")
            return
        result = export_mod.find_asset_refs(proj_dir, asset_path)

        def human(rows):
            if not rows:
                return f"(no references to {asset_path})"
            lines = [f"Found {len(rows)} reference(s) to {asset_path}:"]
            for row in rows:
                lines.append(
                    f"  {row['file']} ({row['category']}) -> {row['original_ref']}"
                )
            return "\n".join(lines)

        _output(ctx, result, human)
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@asset.command("find-unused")
@click.option(
    "--type",
    "asset_types",
    multiple=True,
    help="Asset types to check (model, material, sound, texture, prefab). Repeatable.",
)
@click.pass_context
def asset_find_unused(ctx, asset_types):
    """Find project assets that aren't referenced by any scene or prefab."""
    try:
        proj_dir = _resolve_project_dir(ctx)
        if not proj_dir:
            _output_error(ctx, "No project found")
            return
        types_list = list(asset_types) if asset_types else None
        result = export_mod.find_unused_assets(proj_dir, asset_types=types_list)

        def human(rows):
            if not rows:
                return "(no unused assets found)"
            return _format_table(
                [
                    {
                        "path": r["path"],
                        "type": r["type"],
                        "size_bytes": r["size_bytes"],
                    }
                    for r in rows
                ],
                ["path", "type", "size_bytes"],
            )

        _output(ctx, result, human)
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))
