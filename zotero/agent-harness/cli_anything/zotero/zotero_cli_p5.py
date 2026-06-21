# ruff: noqa: F403, F405, E501
from .zotero_cli_base import *  # noqa: F403

# fmt: off
from .zotero_cli_p1 import _json_text, _safe_text_for_stdout, current_runtime, current_session, root_json_output  # noqa: E402,E501
from .zotero_cli_p4 import cli  # noqa: E402,E501
# fmt: on


def dispatch(argv: list[str] | None = None, prog_name: str | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        result = cli.main(
            args=args,
            prog_name=prog_name or "cli-anything-zotero",
            standalone_mode=False,
        )
    except click.exceptions.Exit as exc:
        return int(exc.exit_code)
    except click.ClickException as exc:
        exc.show()
        return int(exc.exit_code)
    return int(result or 0)


@cli.group()
def item() -> None:
    """Item inspection and rendering commands."""


def emit(ctx: click.Context | None, data: Any, *, message: str = "") -> None:
    if root_json_output(ctx):
        click.echo(_json_text(data))
        return
    if isinstance(data, str):
        click.echo(_safe_text_for_stdout(data))
        return
    if message:
        click.echo(_safe_text_for_stdout(message))
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                click.echo(_json_text(item))
            else:
                click.echo(_safe_text_for_stdout(str(item)))
        if not data:
            click.echo("[]")
        return
    if isinstance(data, dict):
        click.echo(_json_text(data))
        return
    click.echo(_safe_text_for_stdout(str(data)))


def _print_collection_tree(nodes: list[dict[str, Any]], level: int = 0) -> None:
    prefix = "  " * level
    for node in nodes:
        click.echo(f"{prefix}- {node['collectionName']} [{node['collectionID']}]")
        _print_collection_tree(node.get("children", []), level + 1)


def _require_experimental_flag(enabled: bool, command_name: str) -> None:
    if not enabled:
        raise click.ClickException(
            f"`{command_name}` is experimental and writes directly to zotero.sqlite. "
            "Pass --experimental to continue."
        )


def _import_exit_code(payload: dict[str, Any]) -> int:
    return 1 if payload.get("status") == "partial_success" else 0


@cli.group()
def app() -> None:
    """Application and runtime inspection commands."""


@app.command("status")
@click.pass_context
def app_status(ctx: click.Context) -> int:
    runtime = current_runtime(ctx)
    emit(ctx, runtime.to_status_payload())
    return 0


@app.command("version")
@click.pass_context
def app_version(ctx: click.Context) -> int:
    runtime = current_runtime(ctx)
    payload = {
        "package_version": __version__,
        "zotero_version": runtime.environment.version,
    }
    emit(ctx, payload if root_json_output(ctx) else runtime.environment.version)
    return 0


@app.command("launch")
@click.option("--wait-timeout", default=30, show_default=True, type=int)
@click.pass_context
def app_launch(ctx: click.Context, wait_timeout: int) -> int:
    runtime = current_runtime(ctx)
    payload = discovery.launch_zotero(runtime, wait_timeout=wait_timeout)
    ctx.find_root().obj["runtime"] = None
    emit(ctx, payload)
    return 0


@app.command("enable-local-api")
@click.option(
    "--launch",
    "launch_after_enable",
    is_flag=True,
    help="Launch Zotero and verify connector + Local API after enabling.",
)
@click.option("--wait-timeout", default=30, show_default=True, type=int)
@click.pass_context
def app_enable_local_api(
    ctx: click.Context, launch_after_enable: bool, wait_timeout: int
) -> int:
    payload = imports.enable_local_api(
        current_runtime(ctx), launch=launch_after_enable, wait_timeout=wait_timeout
    )
    ctx.find_root().obj["runtime"] = None
    emit(ctx, payload)
    return 0


@app.command("ping")
@click.pass_context
def app_ping(ctx: click.Context) -> int:
    runtime = current_runtime(ctx)
    if not runtime.connector_available:
        raise click.ClickException(runtime.connector_message)
    emit(ctx, {"connector_available": True, "message": runtime.connector_message})
    return 0


@cli.group()
def collection() -> None:
    """Collection inspection and selection commands."""


@collection.command("list")
@click.pass_context
def collection_list(ctx: click.Context) -> int:
    emit(ctx, catalog.list_collections(current_runtime(ctx), session=current_session()))
    return 0
