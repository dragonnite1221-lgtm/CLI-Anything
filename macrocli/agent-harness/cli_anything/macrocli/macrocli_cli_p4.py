# ruff: noqa: F403, F405, E501
from .macrocli_cli_base import *  # noqa: F403

# fmt: off
from .macrocli_cli_p1 import _parse_params, get_runtime, handle_error, output  # noqa: E402,E501
from .macrocli_cli_p2 import macro  # noqa: E402,E501
# fmt: on


@macro.command("info")
@click.argument("name")
@handle_error
def macro_info(name):
    """Show full details for a macro (schema, parameters, steps)."""
    runtime = get_runtime()
    m = runtime.registry.load(name)

    if _json_output:
        output(m.to_dict())
    else:
        click.echo(f"\nMacro: {m.name}  (v{m.version})")
        click.echo(f"  {m.description}\n")

        if m.parameters:
            click.echo("Parameters:")
            for pname, pspec in m.parameters.items():
                req = (
                    "(required)" if pspec.required else f"(default: {pspec.default!r})"
                )
                click.echo(f"  --param {pname}=<{pspec.type}>  {req}")
                if pspec.description:
                    click.echo(f"           {pspec.description}")

        if m.preconditions:
            click.echo(f"\nPreconditions ({len(m.preconditions)}):")
            for c in m.preconditions:
                click.echo(f"  {c.type}: {c.args}")

        if m.steps:
            click.echo(f"\nSteps ({len(m.steps)}):")
            for s in m.steps:
                click.echo(f"  [{s.id}] backend={s.backend}  action={s.action}")

        if m.postconditions:
            click.echo(f"\nPostconditions ({len(m.postconditions)}):")
            for c in m.postconditions:
                click.echo(f"  {c.type}: {c.args}")

        if m.outputs:
            click.echo(f"\nOutputs:")
            for o in m.outputs:
                click.echo(f"  {o.name}: {o.path or o.value}")

        if m.agent_hints:
            click.echo(f"\nAgent hints: {m.agent_hints}")
        click.echo()


@macro.command("validate")
@click.argument("name", required=False)
@handle_error
def macro_validate(name):
    """Validate macro definition(s). Pass a name or omit to validate all."""
    runtime = get_runtime()

    if name:
        names = [name]
    else:
        names = runtime.registry.list_names()

    results = {}
    for n in names:
        errors = runtime.validate_macro(n)
        results[n] = errors

    if _json_output:
        output({n: {"valid": len(e) == 0, "errors": e} for n, e in results.items()})
    else:
        all_ok = True
        for n, errors in results.items():
            if errors:
                all_ok = False
                click.echo(f"✗ {n}:")
                for err in errors:
                    click.echo(f"    - {err}", err=True)
            else:
                click.echo(f"✓ {n}")
        if all_ok:
            click.echo("\nAll macros valid.")
        else:
            if not _repl_mode:
                sys.exit(1)


@macro.command("dry-run")
@click.argument("name")
@click.option("--param", "-p", multiple=True, help="Parameter in key=value format.")
@handle_error
def macro_dry_run(name, param):
    """Simulate macro execution without any side effects."""
    params = _parse_params(param)
    runtime = get_runtime()
    result = runtime.execute(name, params, dry_run=True)

    if _json_output:
        output(result.to_dict())
    else:
        click.echo(f"[dry-run] Macro '{name}'")
        if result.success:
            click.echo("  Would execute successfully.")
            click.echo(f"  Steps: {len(result.step_results)}")
        else:
            click.echo(f"  Would fail: {result.error}", err=True)
