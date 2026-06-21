# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _format_status_block, _output, _output_error, _resolve_project_path  # noqa: E402,E501
from .sbox_cli_p2 import cli  # noqa: E402,E501
from .sbox_cli_p20 import localization  # noqa: E402,E501
# fmt: on


@localization.command("new")
@click.option("--lang", default="en", help="Language code")
@click.option(
    "-o", "--output", "output_path", default=None, help="Output .json file path"
)
@click.pass_context
def localization_new(ctx, lang, output_path):
    """Create a new translation file."""
    try:
        result = localization_mod.create_translation_file(
            lang=lang, output_path=output_path
        )
        _output(
            ctx,
            result,
            lambda d: (
                f"Translation file ({d['lang']}) created"
                + (f" at {d.get('path', '')}" if d.get("path") else "")
            ),
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@localization.command("list")
@click.argument("file_path")
@click.pass_context
def localization_list(ctx, file_path):
    """List translation keys."""
    try:
        keys = localization_mod.list_keys(file_path)
        _output(ctx, keys)
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@localization.command("set")
@click.argument("file_path")
@click.option("--key", required=True, help="Translation key")
@click.option("--value", required=True, help="Translation value")
@click.pass_context
def localization_set(ctx, file_path, key, value):
    """Set a translation key-value pair."""
    try:
        result = localization_mod.set_key(file_path, key, value)
        _output(
            ctx,
            {"key": key, "value": value, "total_keys": len(result)},
            lambda d: (
                f"Set '{d['key']}' = '{d['value']}' ({d['total_keys']} keys total)"
            ),
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@localization.command("get")
@click.argument("file_path")
@click.option("--key", required=True, help="Translation key")
@click.pass_context
def localization_get(ctx, file_path, key):
    """Get a translation value by key."""
    try:
        value = localization_mod.get_key(file_path, key)
        if value is None:
            _output_error(ctx, f"Key '{key}' not found")
            return
        _output(
            ctx, {"key": key, "value": value}, lambda d: f"{d['key']} = {d['value']}"
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@localization.command("remove")
@click.argument("file_path")
@click.option("--key", required=True, help="Translation key to remove")
@click.pass_context
def localization_remove(ctx, file_path, key):
    """Remove a translation key."""
    try:
        removed = localization_mod.remove_key(file_path, key)
        result = {"key": key, "removed": removed}
        _output(
            ctx,
            result,
            lambda d: f"Key '{d['key']}' {'removed' if d['removed'] else 'not found'}",
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@localization.command("bulk-set")
@click.argument("file_path")
@click.option("--keys", required=True, help="Key-value pairs as JSON object")
@click.pass_context
def localization_bulk_set(ctx, file_path, keys):
    """Set multiple translation keys at once."""
    try:
        keys_dict = json.loads(keys)
        result = localization_mod.bulk_set(file_path, keys_dict)
        _output(
            ctx,
            {"total_keys": len(result), "added": len(keys_dict)},
            lambda d: f"Set {d['added']} keys ({d['total_keys']} total)",
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@cli.command()
@click.pass_context
def launch(ctx):
    """Open project in the s&box editor."""
    try:
        sbproj = _resolve_project_path(ctx)
        project_arg = sbproj if sbproj else None
        proc = sbox_backend.launch_editor(project_path=project_arg)
        result = {"pid": proc.pid, "project": project_arg, "status": "launched"}
        _output(ctx, result, lambda d: f"s&box editor launched (PID {d['pid']})")
    except Exception as exc:
        _output_error(ctx, str(exc))


@cli.group("session")
@click.pass_context
def session_group(ctx):
    """Manage CLI session state."""
    pass


@session_group.command("status")
@click.pass_context
def session_status(ctx):
    """Show session state."""
    try:
        sess = session_mod.Session()
        result = sess.get_status()
        _output(ctx, result, lambda d: _format_status_block(d, "Session Status"))
    except Exception as exc:
        _output_error(ctx, str(exc))
