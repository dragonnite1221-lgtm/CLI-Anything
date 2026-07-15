# ruff: noqa: F403, F405, E501
from .cli_base import *  # noqa: F403

# fmt: off
# fmt: on


@main.command()
@click.argument("name")
def info(name):
    """Show details for a specific CLI."""
    cli = get_cli(name)
    if not cli:
        click.secho(f"CLI '{name}' not found.", fg="red", err=True)
        raise SystemExit(1)

    installed = get_installed()
    is_installed = cli["name"] in installed
    source = cli.get("_source", "harness")

    click.secho(f"\n  {cli['display_name']}", bold=True)
    click.echo(f"  {cli['description']}")
    click.echo(f"  Category:    {cli.get('category', 'N/A')}")
    click.echo(f"  Source:      {source}")
    if source == "public":
        click.echo(
            f"  Install via: {cli.get('package_manager') or cli.get('install_strategy') or 'public'}"
        )
        if cli.get("npm_package"):
            click.echo(f"  npm package: {cli['npm_package']}")
        if cli.get("npx_cmd"):
            click.echo(f"  npx command: {cli['npx_cmd']}")
        if cli.get("install_cmd"):
            click.echo(f"  Install cmd: {cli['install_cmd']}")
        if cli.get("install_notes"):
            click.echo(f"  Notes:       {cli['install_notes']}")
    click.echo(f"  Version:     {cli['version']}")
    click.echo(f"  Requires:    {cli.get('requires') or 'nothing'}")
    click.echo(f"  Entry point: {cli['entry_point']}")
    click.echo(f"  Homepage:    {cli.get('homepage', 'N/A')}")
    contributors = cli.get("contributors", [])
    if contributors:
        names = ", ".join(ct["name"] for ct in contributors)
        click.echo(f"  Contributors: {names}")
    status = click.style("installed", fg="green") if is_installed else "not installed"
    click.echo(f"  Status:      {status}")
    click.echo(f"\n  Install: cli-hub install {cli['name']}")
    click.echo()


@main.command()
@click.argument("name")
@click.argument("args", nargs=-1)
def launch(name, args):
    """Launch an installed CLI, passing through any extra arguments."""
    cli = get_cli(name)
    if not cli:
        click.secho(f"CLI '{name}' not found in registry.", fg="red", err=True)
        raise SystemExit(1)

    entry = cli["entry_point"]
    if not shutil.which(entry):
        click.secho(
            f"'{entry}' not found on PATH. Install it first: cli-hub install {name}",
            fg="red",
            err=True,
        )
        raise SystemExit(1)

    track_launch(name)
    os.execvp(entry, [entry] + list(args))


@main.group(name="previews", invoke_without_command=True)
@click.pass_context
def previews(ctx):
    """Inspect existing preview bundles or live sessions; this command does not publish previews."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@previews.command("inspect")
@click.argument("preview_ref")
@click.option(
    "--json", "as_json", is_flag=True, help="Output preview metadata as JSON."
)
def preview_inspect(preview_ref, as_json):
    """Inspect a preview bundle or live session."""
    if is_live_session_ref(preview_ref):
        payload = inspect_session(preview_ref)
        if as_json:
            click.echo(json_mod.dumps(payload, indent=2))
            return
        click.echo(render_session_text(preview_ref), nl=False)
        return
    if as_json:
        click.echo(json_mod.dumps(inspect_bundle(preview_ref), indent=2))
        return
    click.echo(render_inspect_text(preview_ref), nl=False)


@previews.command("html")
@click.argument("preview_ref")
@click.option("--output", "-o", "output_path", default=None, help="Output HTML path.")
@click.option(
    "--poll-ms",
    default=1500,
    show_default=True,
    help="Polling interval for live session pages.",
)
def preview_html(preview_ref, output_path, poll_ms):
    """Render HTML for a preview bundle or live session."""
    if is_live_session_ref(preview_ref):
        session_dir, _session = load_session(preview_ref)
        if output_path is None:
            output_path = os.path.join(session_dir, "live.html")
        rendered = render_live_html(preview_ref, output_path, poll_ms=poll_ms)
        click.echo(rendered)
        return
    if output_path is None:
        payload = inspect_bundle(preview_ref)
        output_path = os.path.join(payload["bundle_dir"], "preview.html")
    rendered = render_html(preview_ref, output_path)
    click.echo(rendered)
