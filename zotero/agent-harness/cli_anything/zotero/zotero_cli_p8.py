# ruff: noqa: F403, F405, E501
from .zotero_cli_base import *  # noqa: F403

# fmt: off
from .zotero_cli_p1 import current_runtime, current_session, root_json_output  # noqa: E402,E501
from .zotero_cli_p4 import cli  # noqa: E402,E501
from .zotero_cli_p5 import _require_experimental_flag, emit, item  # noqa: E402,E501
# fmt: on


@item.command("analyze")
@click.argument("ref", required=False)
@click.option("--question", required=True)
@click.option("--model", required=True)
@click.option("--include-notes", is_flag=True)
@click.option("--include-bibtex", is_flag=True)
@click.option("--include-csljson", is_flag=True)
@click.pass_context
def item_analyze_command(
    ctx: click.Context,
    ref: str | None,
    question: str,
    model: str,
    include_notes: bool,
    include_bibtex: bool,
    include_csljson: bool,
) -> int:
    payload = analysis.analyze_item(
        current_runtime(ctx),
        ref,
        question=question,
        model=model,
        include_notes=include_notes,
        include_bibtex=include_bibtex,
        include_csljson=include_csljson,
        session=current_session(),
    )
    emit(ctx, payload if root_json_output(ctx) else payload["answer"])
    return 0


@item.command("add-to-collection")
@click.argument("item_ref")
@click.argument("collection_ref")
@click.option(
    "--experimental",
    "experimental_mode",
    is_flag=True,
    help="Acknowledge experimental direct SQLite write mode.",
)
@click.pass_context
def item_add_to_collection_command(
    ctx: click.Context, item_ref: str, collection_ref: str, experimental_mode: bool
) -> int:
    _require_experimental_flag(experimental_mode, "item add-to-collection")
    emit(
        ctx,
        experimental.add_item_to_collection(
            current_runtime(ctx), item_ref, collection_ref, session=current_session()
        ),
    )
    return 0


@item.command("move-to-collection")
@click.argument("item_ref")
@click.argument("collection_ref")
@click.option(
    "--from",
    "from_refs",
    multiple=True,
    help="Source collection ID or key. Repeatable.",
)
@click.option(
    "--all-other-collections",
    is_flag=True,
    help="Remove the item from all other collections after adding the target.",
)
@click.option(
    "--experimental",
    "experimental_mode",
    is_flag=True,
    help="Acknowledge experimental direct SQLite write mode.",
)
@click.pass_context
def item_move_to_collection_command(
    ctx: click.Context,
    item_ref: str,
    collection_ref: str,
    from_refs: tuple[str, ...],
    all_other_collections: bool,
    experimental_mode: bool,
) -> int:
    _require_experimental_flag(experimental_mode, "item move-to-collection")
    emit(
        ctx,
        experimental.move_item_to_collection(
            current_runtime(ctx),
            item_ref,
            collection_ref,
            from_refs=list(from_refs),
            all_other_collections=all_other_collections,
            session=current_session(),
        ),
    )
    return 0


@cli.group()
def search() -> None:
    """Saved-search inspection commands."""


@search.command("list")
@click.pass_context
def search_list(ctx: click.Context) -> int:
    emit(ctx, catalog.list_searches(current_runtime(ctx), session=current_session()))
    return 0


@search.command("get")
@click.argument("ref")
@click.pass_context
def search_get(ctx: click.Context, ref: str) -> int:
    emit(ctx, catalog.get_search(current_runtime(ctx), ref, session=current_session()))
    return 0


@search.command("items")
@click.argument("ref")
@click.pass_context
def search_items_command(ctx: click.Context, ref: str) -> int:
    emit(
        ctx, catalog.search_items(current_runtime(ctx), ref, session=current_session())
    )
    return 0


@cli.group()
def tag() -> None:
    """Tag inspection commands."""


@tag.command("list")
@click.pass_context
def tag_list(ctx: click.Context) -> int:
    emit(ctx, catalog.list_tags(current_runtime(ctx), session=current_session()))
    return 0


@tag.command("items")
@click.argument("tag_ref")
@click.pass_context
def tag_items_command(ctx: click.Context, tag_ref: str) -> int:
    emit(
        ctx, catalog.tag_items(current_runtime(ctx), tag_ref, session=current_session())
    )
    return 0
