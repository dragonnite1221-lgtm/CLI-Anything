# ruff: noqa: F403, F405, E501
from .autocomplete_base import *  # noqa: F403

# fmt: off
from .autocomplete_p1 import autocomplete  # noqa: E402,E501
# fmt: on


@autocomplete.command(name="rules")
@click.option("--query", help="Search query")
@click.option("--limit", default=10, help="Number of results")
def autocomplete_rules(query, limit):
    """Autocomplete rules"""
    backend = get_backend()
    params = {"limit": limit}

    if query:
        params["query"] = query

    result = backend.autocomplete_rules(params)
    output(result)


@autocomplete.command(name="recurring")
@click.option("--query", help="Search query")
@click.option("--limit", default=10, help="Number of results")
def autocomplete_recurring(query, limit):
    """Autocomplete recurring transactions"""
    backend = get_backend()
    params = {"limit": limit}

    if query:
        params["query"] = query

    result = backend.autocomplete_recurring(params)
    output(result)


@autocomplete.command(name="object-groups")
@click.option("--query", help="Search query")
@click.option("--limit", default=10, help="Number of results")
def autocomplete_object_groups(query, limit):
    """Autocomplete object groups"""
    backend = get_backend()
    params = {"limit": limit}

    if query:
        params["query"] = query

    result = backend.autocomplete_object_groups(params)
    output(result)


@autocomplete.command(name="transaction-types")
@click.option("--query", help="Search query")
@click.option("--limit", default=10, help="Number of results")
def autocomplete_transaction_types(query, limit):
    """Autocomplete transaction types"""
    backend = get_backend()
    params = {"limit": limit}

    if query:
        params["query"] = query

    result = backend.autocomplete_transaction_types(params)
    output(result)
