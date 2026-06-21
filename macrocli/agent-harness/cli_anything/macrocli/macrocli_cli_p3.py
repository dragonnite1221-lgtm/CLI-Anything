# ruff: noqa: F403, F405, E501
from .macrocli_cli_base import *  # noqa: F403

# fmt: off
from .macrocli_cli_p1 import _parse_params, get_runtime, get_session, handle_error, output  # noqa: E402,E501
from .macrocli_cli_p2 import macro  # noqa: E402,E501
# fmt: on


@macro.command("run")
@click.argument("name")
@click.option(
    "--param",
    "-p",
    multiple=True,
    help="Macro parameter in key=value format. Repeat for multiple.",
)
@click.option(
    "--macro-file",
    default=None,
    help="Run a macro directly from a YAML file path (bypasses registry).",
)
@handle_error
def macro_run(name, param, macro_file):
    """Execute a macro by name, or from a YAML file with --macro-file.

    \b
    Example:
      macro run export_file --param output=/tmp/out.txt
      macro run my_macro --macro-file /tmp/recording/my_macro.yaml --param key=val
    """
    params = _parse_params(param)

    if macro_file:
        # Load macro directly from file, bypassing the registry
        from cli_anything.macrocli.core.macro_model import load_from_yaml
        from cli_anything.macrocli.core.routing import RoutingEngine
        from cli_anything.macrocli.core.runtime import MacroRuntime, ExecutionResult
        from cli_anything.macrocli.core.registry import MacroRegistry

        try:
            macro_def = load_from_yaml(macro_file)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({"success": False, "error": str(e)}))
            else:
                click.echo(f"Error loading macro file: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
            return
        reg = MacroRegistry.__new__(MacroRegistry)
        reg._cache = {macro_def.name: macro_def}
        reg._scanned = True
        reg.macros_dir = None
        runtime = MacroRuntime(registry=reg, session=get_session())
        result = runtime.execute(macro_def.name, params, dry_run=_dry_run)
    else:
        runtime = get_runtime()
        result = runtime.execute(name, params, dry_run=_dry_run)

    if _json_output:
        output(result.to_dict())
    else:
        if result.success:
            click.echo(f"✓ Macro '{name}' completed successfully.")
            if result.output:
                for k, v in result.output.items():
                    if not k.startswith("_"):
                        click.echo(f"  {k}: {v}")
        else:
            click.echo(f"✗ Macro '{name}' failed.", err=True)
            click.echo(f"  {result.error}", err=True)
        if result.telemetry:
            click.echo(
                f"  [{result.telemetry.get('duration_ms', 0):.0f}ms, "
                f"backends: {', '.join(result.telemetry.get('backends_used', []))}]"
            )
    if not result.success and not _repl_mode:
        sys.exit(1)


@macro.command("list")
@handle_error
def macro_list():
    """List all available macros."""
    runtime = get_runtime()
    macros = runtime.registry.list_all()

    if _json_output:
        output(
            [
                {
                    "name": m.name,
                    "version": m.version,
                    "description": m.description,
                    "tags": m.tags,
                    "parameters": list(m.parameters.keys()),
                }
                for m in macros
            ]
        )
    else:
        if not macros:
            click.echo("No macros found.")
            return
        click.echo(f"Available macros ({len(macros)}):\n")
        for m in macros:
            tags = f"  [{', '.join(m.tags)}]" if m.tags else ""
            click.echo(f"  {m.name:<30}  {m.description}{tags}")
