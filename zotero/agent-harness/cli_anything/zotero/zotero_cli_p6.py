# ruff: noqa: F403, F405, E501
from .zotero_cli_base import *  # noqa: F403

# fmt: off
from .zotero_cli_p1 import current_runtime, current_session, root_json_output  # noqa: E402,E501
from .zotero_cli_p2 import _persist_selected_collection  # noqa: E402,E501
from .zotero_cli_p5 import _print_collection_tree, _require_experimental_flag, collection, emit, item  # noqa: E402,E501
# fmt: on


@collection.command("find")
@click.argument("query")
@click.option("--limit", default=20, show_default=True, type=int)
@click.pass_context
def collection_find_command(ctx: click.Context, query: str, limit: int) -> int:
    emit(
        ctx,
        catalog.find_collections(
            current_runtime(ctx), query, limit=limit, session=current_session()
        ),
    )
    return 0


@collection.command("tree")
@click.pass_context
def collection_tree_command(ctx: click.Context) -> int:
    tree = catalog.collection_tree(current_runtime(ctx), session=current_session())
    if root_json_output(ctx):
        emit(ctx, tree)
    else:
        _print_collection_tree(tree)
    return 0


@collection.command("get")
@click.argument("ref", required=False)
@click.pass_context
def collection_get(ctx: click.Context, ref: str | None) -> int:
    emit(
        ctx,
        catalog.get_collection(current_runtime(ctx), ref, session=current_session()),
    )
    return 0


@collection.command("items")
@click.argument("ref", required=False)
@click.pass_context
def collection_items_command(ctx: click.Context, ref: str | None) -> int:
    emit(
        ctx,
        catalog.collection_items(current_runtime(ctx), ref, session=current_session()),
    )
    return 0


@collection.command("use-selected")
@click.pass_context
def collection_use_selected(ctx: click.Context) -> int:
    selected = catalog.use_selected_collection(current_runtime(ctx))
    _persist_selected_collection(selected)
    session_mod.append_command_history("collection use-selected")
    emit(ctx, selected)
    return 0


@collection.command("create")
@click.argument("name")
@click.option(
    "--parent", "parent_ref", default=None, help="Parent collection ID or key."
)
@click.option(
    "--library",
    "library_ref",
    default=None,
    help="Library ID or treeView ID (user library only).",
)
@click.option(
    "--experimental",
    "experimental_mode",
    is_flag=True,
    help="Acknowledge experimental direct SQLite write mode.",
)
@click.pass_context
def collection_create_command(
    ctx: click.Context,
    name: str,
    parent_ref: str | None,
    library_ref: str | None,
    experimental_mode: bool,
) -> int:
    _require_experimental_flag(experimental_mode, "collection create")
    emit(
        ctx,
        experimental.create_collection(
            current_runtime(ctx),
            name,
            parent_ref=parent_ref,
            library_ref=library_ref,
            session=current_session(),
        ),
    )
    return 0


@item.command("list")
@click.option("--limit", default=20, show_default=True, type=int)
@click.pass_context
def item_list(ctx: click.Context, limit: int) -> int:
    emit(
        ctx,
        catalog.list_items(
            current_runtime(ctx), session=current_session(), limit=limit
        ),
    )
    return 0


@item.command("find")
@click.argument("query")
@click.option(
    "--collection", "collection_ref", default=None, help="Collection ID or key scope."
)
@click.option("--limit", default=20, show_default=True, type=int)
@click.option(
    "--exact-title", is_flag=True, help="Use exact title matching via SQLite."
)
@click.pass_context
def item_find_command(
    ctx: click.Context,
    query: str,
    collection_ref: str | None,
    limit: int,
    exact_title: bool,
) -> int:
    emit(
        ctx,
        catalog.find_items(
            current_runtime(ctx),
            query,
            collection_ref=collection_ref,
            limit=limit,
            exact_title=exact_title,
            session=current_session(),
        ),
    )
    return 0


@item.command("get")
@click.argument("ref", required=False)
@click.pass_context
def item_get(ctx: click.Context, ref: str | None) -> int:
    emit(ctx, catalog.get_item(current_runtime(ctx), ref, session=current_session()))
    return 0
