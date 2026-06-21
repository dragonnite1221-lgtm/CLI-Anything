# ruff: noqa: F403, F405, E501
from .zotero_cli_base import *  # noqa: F403

# fmt: off
from .zotero_cli_p1 import current_runtime, current_session, root_json_output  # noqa: E402,E501
from .zotero_cli_p4 import cli  # noqa: E402,E501
from .zotero_cli_p5 import emit, item  # noqa: E402,E501
# fmt: on


@item.command("children")
@click.argument("ref", required=False)
@click.pass_context
def item_children_command(ctx: click.Context, ref: str | None) -> int:
    emit(
        ctx, catalog.item_children(current_runtime(ctx), ref, session=current_session())
    )
    return 0


@item.command("notes")
@click.argument("ref", required=False)
@click.pass_context
def item_notes_command(ctx: click.Context, ref: str | None) -> int:
    emit(ctx, catalog.item_notes(current_runtime(ctx), ref, session=current_session()))
    return 0


@item.command("attachments")
@click.argument("ref", required=False)
@click.pass_context
def item_attachments_command(ctx: click.Context, ref: str | None) -> int:
    emit(
        ctx,
        catalog.item_attachments(current_runtime(ctx), ref, session=current_session()),
    )
    return 0


@item.command("file")
@click.argument("ref", required=False)
@click.pass_context
def item_file_command(ctx: click.Context, ref: str | None) -> int:
    emit(ctx, catalog.item_file(current_runtime(ctx), ref, session=current_session()))
    return 0


@item.command("export")
@click.argument("ref", required=False)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(list(rendering.SUPPORTED_EXPORT_FORMATS)),
    required=True,
)
@click.pass_context
def item_export(ctx: click.Context, ref: str | None, fmt: str) -> int:
    payload = rendering.export_item(
        current_runtime(ctx), ref, fmt, session=current_session()
    )
    emit(ctx, payload if root_json_output(ctx) else payload["content"])
    return 0


@cli.group()
def style() -> None:
    """Installed CSL style inspection commands."""


@item.command("citation")
@click.argument("ref", required=False)
@click.option("--style", default=None)
@click.option("--locale", default=None)
@click.option("--linkwrap", is_flag=True)
@click.pass_context
def item_citation(
    ctx: click.Context,
    ref: str | None,
    style: str | None,
    locale: str | None,
    linkwrap: bool,
) -> int:
    payload = rendering.citation_item(
        current_runtime(ctx),
        ref,
        style=style,
        locale=locale,
        linkwrap=linkwrap,
        session=current_session(),
    )
    emit(ctx, payload if root_json_output(ctx) else (payload.get("citation") or ""))
    return 0


@item.command("bibliography")
@click.argument("ref", required=False)
@click.option("--style", default=None)
@click.option("--locale", default=None)
@click.option("--linkwrap", is_flag=True)
@click.pass_context
def item_bibliography(
    ctx: click.Context,
    ref: str | None,
    style: str | None,
    locale: str | None,
    linkwrap: bool,
) -> int:
    payload = rendering.bibliography_item(
        current_runtime(ctx),
        ref,
        style=style,
        locale=locale,
        linkwrap=linkwrap,
        session=current_session(),
    )
    emit(ctx, payload if root_json_output(ctx) else (payload.get("bibliography") or ""))
    return 0


@item.command("context")
@click.argument("ref", required=False)
@click.option("--include-notes", is_flag=True)
@click.option("--include-bibtex", is_flag=True)
@click.option("--include-csljson", is_flag=True)
@click.option("--include-links", is_flag=True)
@click.pass_context
def item_context_command(
    ctx: click.Context,
    ref: str | None,
    include_notes: bool,
    include_bibtex: bool,
    include_csljson: bool,
    include_links: bool,
) -> int:
    payload = analysis.build_item_context(
        current_runtime(ctx),
        ref,
        include_notes=include_notes,
        include_bibtex=include_bibtex,
        include_csljson=include_csljson,
        include_links=include_links,
        session=current_session(),
    )
    emit(ctx, payload if root_json_output(ctx) else payload["prompt_context"])
    return 0
