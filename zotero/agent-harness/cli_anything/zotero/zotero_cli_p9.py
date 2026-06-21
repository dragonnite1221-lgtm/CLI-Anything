# ruff: noqa: F403, F405, E501
from .zotero_cli_base import *  # noqa: F403

# fmt: off
from .zotero_cli_p1 import current_runtime, current_session, root_json_output  # noqa: E402,E501
from .zotero_cli_p4 import cli  # noqa: E402,E501
from .zotero_cli_p5 import _import_exit_code, emit  # noqa: E402,E501
from .zotero_cli_p7 import style  # noqa: E402,E501
# fmt: on


@style.command("list")
@click.pass_context
def style_list(ctx: click.Context) -> int:
    emit(ctx, catalog.list_styles(current_runtime(ctx)))
    return 0


@cli.group("import")
def import_group() -> None:
    """Official Zotero import and write commands."""


@import_group.command("file")
@click.argument("path")
@click.option(
    "--collection",
    "collection_ref",
    default=None,
    help="Collection ID, key, or treeViewID target.",
)
@click.option(
    "--tag", "tags", multiple=True, help="Tag to apply after import. Repeatable."
)
@click.option(
    "--attachments-manifest",
    default=None,
    help="Optional JSON manifest describing attachments for imported records.",
)
@click.option(
    "--attachment-delay-ms",
    default=0,
    show_default=True,
    type=int,
    help="Default delay before each URL attachment download.",
)
@click.option(
    "--attachment-timeout",
    default=60,
    show_default=True,
    type=int,
    help="Default timeout in seconds for attachment download/upload.",
)
@click.pass_context
def import_file_command(
    ctx: click.Context,
    path: str,
    collection_ref: str | None,
    tags: tuple[str, ...],
    attachments_manifest: str | None,
    attachment_delay_ms: int,
    attachment_timeout: int,
) -> int:
    payload = imports.import_file(
        current_runtime(ctx),
        path,
        collection_ref=collection_ref,
        tags=list(tags),
        session=current_session(),
        attachments_manifest=attachments_manifest,
        attachment_delay_ms=attachment_delay_ms,
        attachment_timeout=attachment_timeout,
    )
    emit(ctx, payload)
    return _import_exit_code(payload)


@import_group.command("json")
@click.argument("path")
@click.option(
    "--collection",
    "collection_ref",
    default=None,
    help="Collection ID, key, or treeViewID target.",
)
@click.option(
    "--tag", "tags", multiple=True, help="Tag to apply after import. Repeatable."
)
@click.option(
    "--attachment-delay-ms",
    default=0,
    show_default=True,
    type=int,
    help="Default delay before each URL attachment download.",
)
@click.option(
    "--attachment-timeout",
    default=60,
    show_default=True,
    type=int,
    help="Default timeout in seconds for attachment download/upload.",
)
@click.pass_context
def import_json_command(
    ctx: click.Context,
    path: str,
    collection_ref: str | None,
    tags: tuple[str, ...],
    attachment_delay_ms: int,
    attachment_timeout: int,
) -> int:
    payload = imports.import_json(
        current_runtime(ctx),
        path,
        collection_ref=collection_ref,
        tags=list(tags),
        session=current_session(),
        attachment_delay_ms=attachment_delay_ms,
        attachment_timeout=attachment_timeout,
    )
    emit(ctx, payload)
    return _import_exit_code(payload)


@cli.group()
def note() -> None:
    """Read and add child notes."""


@note.command("get")
@click.argument("ref")
@click.pass_context
def note_get_command(ctx: click.Context, ref: str) -> int:
    payload = notes.get_note(current_runtime(ctx), ref, session=current_session())
    emit(
        ctx,
        payload
        if root_json_output(ctx)
        else (payload.get("noteText") or payload.get("noteContent") or ""),
    )
    return 0


@note.command("add")
@click.argument("item_ref")
@click.option("--text", default=None, help="Inline note content.")
@click.option(
    "--file", "file_path", default=None, help="Read note content from a file."
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "markdown", "html"]),
    default="text",
    show_default=True,
)
@click.pass_context
def note_add_command(
    ctx: click.Context,
    item_ref: str,
    text: str | None,
    file_path: str | None,
    fmt: str,
) -> int:
    emit(
        ctx,
        notes.add_note(
            current_runtime(ctx),
            item_ref,
            text=text,
            file_path=file_path,
            fmt=fmt,
            session=current_session(),
        ),
    )
    return 0
