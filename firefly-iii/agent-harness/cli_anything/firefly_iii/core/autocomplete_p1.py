# ruff: noqa: F403, F405, E501
from .autocomplete_base import *  # noqa: F403


@click.group()
def autocomplete():
    """Autocomplete suggestions"""
    pass


@autocomplete.command(name="accounts")
@click.option("--query", help="Search query")
@click.option("--limit", default=10, help="Number of results")
@click.option("--date", help="Date for balance (YYYY-MM-DD)")
@click.option(
    "--types", help="Account types (comma-separated: asset,expense,revenue,liability)"
)
def autocomplete_accounts(query, limit, date, types):
    """Autocomplete accounts"""
    backend = get_backend()
    params = {"limit": limit}

    if query:
        params["query"] = query
    if date:
        params["date"] = date
    if types:
        params["types"] = types

    result = backend.autocomplete_accounts(params)
    output(result)


@autocomplete.command(name="bills")
@click.option("--query", help="Search query")
@click.option("--limit", default=10, help="Number of results")
def autocomplete_bills(query, limit):
    """Autocomplete bills"""
    backend = get_backend()
    params = {"limit": limit}

    if query:
        params["query"] = query

    result = backend.autocomplete_bills(params)
    output(result)


@autocomplete.command(name="budgets")
@click.option("--query", help="Search query")
@click.option("--limit", default=10, help="Number of results")
def autocomplete_budgets(query, limit):
    """Autocomplete budgets"""
    backend = get_backend()
    params = {"limit": limit}

    if query:
        params["query"] = query

    result = backend.autocomplete_budgets(params)
    output(result)


@autocomplete.command(name="categories")
@click.option("--query", help="Search query")
@click.option("--limit", default=10, help="Number of results")
def autocomplete_categories(query, limit):
    """Autocomplete categories"""
    backend = get_backend()
    params = {"limit": limit}

    if query:
        params["query"] = query

    result = backend.autocomplete_categories(params)
    output(result)


@autocomplete.command(name="currencies")
@click.option("--query", help="Search query")
@click.option("--limit", default=10, help="Number of results")
def autocomplete_currencies(query, limit):
    """Autocomplete currencies"""
    backend = get_backend()
    params = {"limit": limit}

    if query:
        params["query"] = query

    result = backend.autocomplete_currencies(params)
    output(result)


@autocomplete.command(name="piggy-banks")
@click.option("--query", help="Search query")
@click.option("--limit", default=10, help="Number of results")
def autocomplete_piggy_banks(query, limit):
    """Autocomplete piggy banks"""
    backend = get_backend()
    params = {"limit": limit}

    if query:
        params["query"] = query

    result = backend.autocomplete_piggy_banks(params)
    output(result)


@autocomplete.command(name="tags")
@click.option("--query", help="Search query")
@click.option("--limit", default=10, help="Number of results")
def autocomplete_tags(query, limit):
    """Autocomplete tags"""
    backend = get_backend()
    params = {"limit": limit}

    if query:
        params["query"] = query

    result = backend.autocomplete_tags(params)
    output(result)


@autocomplete.command(name="transactions")
@click.option("--query", help="Search query")
@click.option("--limit", default=10, help="Number of results")
def autocomplete_transactions(query, limit):
    """Autocomplete transactions"""
    backend = get_backend()
    params = {"limit": limit}

    if query:
        params["query"] = query

    result = backend.autocomplete_transactions(params)
    output(result)


@autocomplete.command(name="rule-groups")
@click.option("--query", help="Search query")
@click.option("--limit", default=10, help="Number of results")
def autocomplete_rule_groups(query, limit):
    """Autocomplete rule groups"""
    backend = get_backend()
    params = {"limit": limit}

    if query:
        params["query"] = query

    result = backend.autocomplete_rule_groups(params)
    output(result)
