# ruff: noqa: F403, F405, E501
from .macrocli_cli_base import *  # noqa: F403

# fmt: off
from .macrocli_cli_p1 import handle_error, output  # noqa: E402,E501
from .macrocli_cli_p2 import macro  # noqa: E402,E501
# fmt: on


@macro.command("record")
@click.argument("name")
@click.option(
    "--output-dir",
    "-d",
    default=".",
    help="Directory to write the macro package folder.",
)
@click.option(
    "--timeout",
    default=0,
    type=float,
    help="Auto-stop after N seconds (0 = wait for Ctrl+Alt+S).",
)
@click.option(
    "--agent-review",
    "do_agent_review",
    is_flag=True,
    help="After recording, review each step and mark some as "
    "agent steps with descriptions and end-state snapshots.",
)
@click.option(
    "--parameterize",
    "do_parameterize",
    is_flag=True,
    help="After recording, interactively choose which typed values "
    "become CLI parameters.",
)
@click.option(
    "--auto-parameterize",
    "do_auto_param",
    is_flag=True,
    help="After recording, use an LLM to automatically suggest "
    "parameter names (requires --api-key or MACROCLI_API_KEY).",
)
@click.option(
    "--api-key",
    default=None,
    envvar="MACROCLI_API_KEY",
    help="API key for --auto-parameterize.",
)
@handle_error
def macro_record(
    name, output_dir, timeout, do_agent_review, do_parameterize, do_auto_param, api_key
):
    """Record GUI interactions and generate a macro YAML package.

    \b
    The macro is saved as a folder:
      <name>/
        macro.yaml
        snapshots/   (end-state screenshots for agent steps)

    \b
    Examples:
      # Basic recording
      macro record my_export

      # Record + mark agent steps interactively
      macro record my_export --agent-review

      # Record + agent review + parameterize typed values
      macro record my_export --agent-review --parameterize

    Requires: pip install mss Pillow pynput
    """
    try:
        from cli_anything.macrocli.core.recorder import MacroRecorder
    except ImportError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if do_parameterize and do_auto_param:
        click.echo(
            "Error: --parameterize and --auto-parameterize are mutually exclusive.",
            err=True,
        )
        sys.exit(1)

    recorder = MacroRecorder(macro_name=name, output_dir=output_dir)

    if not _json_output:
        click.echo(f"Recording '{name}'. Press Ctrl+Alt+S to stop...")

    try:
        recorder.record(timeout_s=timeout if timeout > 0 else None)
    except Exception as e:
        if _json_output:
            output({"error": str(e), "success": False})
        else:
            click.echo(f"Error during recording: {e}", err=True)
        if not _repl_mode:
            sys.exit(1)
        return

    # ── Agent step review ─────────────────────────────────────────────────────
    if do_agent_review and recorder._steps:
        snap_dir = Path(output_dir) / name / "snapshots"
        recorder.interactive_agent_review(snapshots_dir=str(snap_dir))

    # ── Parameterization phase ────────────────────────────────────────────────
    parameters = None
    type_steps = recorder.get_type_steps()

    if do_auto_param and type_steps:
        try:
            from cli_anything.macrocli.core.parameterize import (
                llm_suggest_parameters,
                interactive_parameterize,
            )

            if not _json_output:
                click.echo(f"\nAsking LLM to suggest parameters...")
            suggestions = llm_suggest_parameters(type_steps, api_key=api_key)
            if suggestions and not _json_output:
                click.echo("  LLM suggestions:")
                for idx, pname in suggestions.items():
                    step = recorder._steps[idx]
                    click.echo(f"    step {idx + 1} {step.text!r} → ${{{pname}}}")
                click.echo()
                confirmed = interactive_parameterize(
                    [(i, s) for i, s in type_steps if i in suggestions],
                )
                final = {**suggestions, **confirmed}
                parameters = recorder.apply_parameterization(final)
            elif not suggestions and not _json_output:
                click.echo("  LLM found no values to parameterize.")
        except Exception as e:
            click.echo(f"  Warning: LLM parameterization failed: {e}", err=True)
            do_parameterize = True

    if do_parameterize and type_steps:
        from cli_anything.macrocli.core.parameterize import interactive_parameterize

        assignments = interactive_parameterize(type_steps)
        if assignments:
            parameters = recorder.apply_parameterization(assignments)

    # ── Save as package ───────────────────────────────────────────────────────
    try:
        yaml_path = recorder.save_as_package(
            output_dir=output_dir,
            parameters=parameters,
        )
    except Exception as e:
        if _json_output:
            output({"error": str(e), "success": False})
        else:
            click.echo(f"Error saving macro: {e}", err=True)
        if not _repl_mode:
            sys.exit(1)
        return

    pkg_dir = str(Path(output_dir) / name)
    agent_count = sum(1 for s in recorder._steps if s.is_agent_step)

    if _json_output:
        output(
            {
                "success": True,
                "yaml_path": yaml_path,
                "package_dir": pkg_dir,
                "steps": len(recorder._steps),
                "agent_steps": agent_count,
                "parameters": list((parameters or {}).keys()),
            }
        )
    else:
        click.echo(f"✓ Saved {len(recorder._steps)} steps to: {pkg_dir}/")
        if agent_count:
            click.echo(
                f"  Agent steps: {agent_count} (will use vision model at runtime)"
            )
        if parameters:
            click.echo(f"  Parameters: {', '.join(parameters.keys())}")
        click.echo(
            f"\n  Run with:\n"
            f"  macro run {name} --macro-file {yaml_path}"
            + (
                "".join(f" --param {k}=<value>" for k in (parameters or {}))
                if parameters
                else ""
            )
        )
