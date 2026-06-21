# ruff: noqa: F403, F405, E501
from .cli_base import *  # noqa: F403

# fmt: off
from .cli_p1 import _source_tag  # noqa: E402,E501
from .cli_p4 import main  # noqa: E402,E501
# fmt: on


@main.command("list")
@click.option("--category", "-c", default=None, help="Filter by category.")
@click.option(
    "--source",
    "-s",
    default=None,
    type=click.Choice(["harness", "public", "npm", "all"], case_sensitive=False),
    help="Filter by source (harness, public, or all). 'npm' is kept as an alias for public.",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def list_clis(category, source, as_json):
    """List all available CLIs."""
    try:
        all_clis = fetch_all_clis()
    except Exception as e:
        click.secho(f"Failed to fetch registry: {e}", fg="red", err=True)
        raise SystemExit(1)

    clis = all_clis
    if category:
        clis = [c for c in clis if c.get("category", "").lower() == category.lower()]
    if source == "npm":
        source = "public"
    if source and source != "all":
        clis = [c for c in clis if c.get("_source", "harness") == source]

    installed = get_installed()

    if as_json:
        import json as json_mod

        click.echo(json_mod.dumps(clis, indent=2))
        return

    if not clis:
        click.echo(
            "No CLIs found."
            + (f" Category '{category}' may not exist." if category else "")
        )
        return

    # Group by category
    by_cat = {}
    for cli in clis:
        cat = cli.get("category", "uncategorized")
        by_cat.setdefault(cat, []).append(cli)

    for cat in sorted(by_cat):
        click.secho(f"\n  {cat.upper()}", fg="blue", bold=True)
        for cli in sorted(by_cat[cat], key=lambda c: c["name"]):
            marker = click.style(" ●", fg="green") if cli["name"] in installed else "  "
            name = click.style(f"{cli['name']:20s}", bold=True)
            desc = cli["description"][:55]
            tag = _source_tag(cli)
            click.echo(f"  {marker} {name}{tag} {desc}")

    total = len(clis)
    inst = sum(1 for c in clis if c["name"] in installed)
    harness_count = sum(1 for c in clis if c.get("_source") == "harness")
    public_count = sum(1 for c in clis if c.get("_source") == "public")
    click.echo(
        f"\n  {total} CLIs available ({harness_count} harness, {public_count} public), {inst} installed"
    )
    cats = list_categories()
    click.echo(f"  Categories: {', '.join(cats)}")


@main.command()
@click.argument("query")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def search(query, as_json):
    """Search CLIs by name, description, or category."""
    results = search_clis(query)

    if as_json:
        import json as json_mod

        click.echo(json_mod.dumps(results, indent=2))
        return

    if not results:
        click.echo(f"No CLIs matching '{query}'.")
        return

    installed = get_installed()
    for cli in results:
        marker = click.style("●", fg="green") if cli["name"] in installed else " "
        name = click.style(cli["name"], bold=True)
        cat = click.style(f"[{cli.get('category', '')}]", fg="blue")
        tag = _source_tag(cli)
        click.echo(f"  {marker} {name} {cat}{tag} — {cli['description'][:65]}")
        click.echo(f"    Install: cli-hub install {cli['name']}")
