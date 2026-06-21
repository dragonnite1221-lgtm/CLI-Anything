# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _format_status_block, _output, _output_error, _resolve_project_path  # noqa: E402,E501
from .sbox_cli_p2 import cli  # noqa: E402,E501
from .sbox_cli_p21 import session_group  # noqa: E402,E501
# fmt: on


@session_group.command("undo")
@click.pass_context
def session_undo(ctx):
    """Undo last operation."""
    try:
        sess = session_mod.Session()
        result = sess.undo()
        if result:
            _output(
                ctx,
                result,
                lambda d: f"Undone: {d.get('description', '(no description)')}",
            )
        else:
            msg = {"message": "Nothing to undo"}
            _output(ctx, msg, lambda d: d["message"])
    except Exception as exc:
        _output_error(ctx, str(exc))


@session_group.command("redo")
@click.pass_context
def session_redo(ctx):
    """Redo last undone operation."""
    try:
        sess = session_mod.Session()
        result = sess.redo()
        if result:
            _output(
                ctx,
                result,
                lambda d: f"Redone: {d.get('description', '(no description)')}",
            )
        else:
            msg = {"message": "Nothing to redo"}
            _output(ctx, msg, lambda d: d["message"])
    except Exception as exc:
        _output_error(ctx, str(exc))


@cli.group("test")
@click.pass_context
def test_group(ctx):
    """Run automated map generation tests."""
    pass


@test_group.command("setup")
@click.pass_context
def test_setup(ctx):
    """First-run setup: verify paths, create test scene."""
    try:
        sbox_install = sbox_backend.find_sbox_installation()
        sbproj = _resolve_project_path(ctx)
        if not sbproj:
            raise click.ClickException("No .sbproj found.")

        info = project_mod.get_project_info(sbproj)
        ident = info.get("ident", "hold_the_line")

        data_path = test_mod.resolve_data_path(sbox_install, ident)

        result = {
            "sbox_install": sbox_install,
            "data_path": data_path,
            "sbproj": sbproj,
            "ident": ident,
            "status": "ready",
        }
        _output(ctx, result, lambda d: _format_status_block(d, "Test Setup"))
    except Exception as exc:
        _output_error(ctx, str(exc))
