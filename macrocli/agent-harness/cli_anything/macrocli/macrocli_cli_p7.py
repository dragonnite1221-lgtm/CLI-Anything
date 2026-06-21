# ruff: noqa: F403, F405, E501
from .macrocli_cli_base import *  # noqa: F403

# fmt: off
from .macrocli_cli_p1 import handle_error, output  # noqa: E402,E501
from .macrocli_cli_p2 import macro  # noqa: E402,E501
# fmt: on


@macro.command("parameterize")
@click.argument("yaml_file")
@click.option(
    "--auto",
    "do_auto",
    is_flag=True,
    help="Use an LLM to suggest parameter names automatically.",
)
@click.option(
    "--api-key", default=None, envvar="MACROCLI_API_KEY", help="API key for --auto."
)
@handle_error
def macro_parameterize(yaml_file, do_auto, api_key):
    """Interactively parameterize typed values in an existing macro YAML.

    \b
    Finds all hardcoded type_text steps in the file and lets you choose
    which values become CLI parameters (e.g. ${output_path}).

    \b
    Examples:
      macro parameterize /tmp/recording/my_export.yaml
      macro parameterize my_export.yaml --auto --api-key $MACROCLI_API_KEY
    """
    from cli_anything.macrocli.core.parameterize import (
        parameterize_yaml_file,
        llm_suggest_parameters,
        interactive_parameterize,
        _YamlTypeStep,
    )

    p = Path(yaml_file)
    if not p.is_file():
        click.echo(f"Error: file not found: {yaml_file}", err=True)
        if not _repl_mode:
            sys.exit(1)
        return

    if do_auto:
        # Load the file, extract type_text steps, ask LLM, then apply
        import yaml as _yaml

        with open(p, encoding="utf-8") as f:
            macro_dict = _yaml.safe_load(f)

        steps = macro_dict.get("steps") or []
        type_steps_raw = [
            (i, s)
            for i, s in enumerate(steps)
            if isinstance(s, dict)
            and s.get("action") == "type_text"
            and not s.get("params", {}).get("text", "").startswith("${")
        ]
        if not type_steps_raw:
            click.echo("No hardcoded type_text steps found.")
            return

        wrapped = [(i, _YamlTypeStep(i, s)) for i, s in type_steps_raw]

        try:
            click.echo(
                f"Asking LLM to suggest parameters for "
                f"{len(wrapped)} type_text step(s)..."
            )
            suggestions = llm_suggest_parameters(wrapped, api_key=api_key)
        except Exception as e:
            click.echo(f"LLM failed: {e}\nFalling back to interactive.", err=True)
            suggestions = {}
            do_auto = False

        if suggestions:
            click.echo("  Suggestions:")
            for idx, pname in suggestions.items():
                w = next(w for i, w in wrapped if i == idx)
                click.echo(f"    step {idx + 1} {w.text!r} → ${{{pname}}}")
            click.echo()

        # Let user confirm (pre-fill LLM suggestions as defaults)
        existing = set((macro_dict.get("parameters") or {}).keys())
        confirmed = interactive_parameterize(
            [(i, w) for i, w in wrapped if i in suggestions],
            existing_params=existing,
        )
        final = {**suggestions, **confirmed}

        if not final:
            click.echo("No parameters applied.")
            return

        # Apply and save
        import yaml as _yaml
        from cli_anything.macrocli.core.recorder import MacroRecorder

        parameters: dict = dict(macro_dict.get("parameters") or {})
        for idx, param_name in final.items():
            w = next(w for i, w in wrapped if i == idx)
            original = w.text
            w.apply(param_name)
            ptype = "string"
            try:
                int(original)
                ptype = "integer"
            except ValueError:
                try:
                    float(original)
                    ptype = "float"
                except ValueError:
                    pass
            parameters[param_name] = {
                "type": ptype,
                "required": True,
                "description": f"Value typed at step {idx + 1}",
                "example": original,
            }
        macro_dict["parameters"] = parameters
        with open(p, "w", encoding="utf-8") as f:
            _yaml.dump(
                macro_dict,
                f,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False,
            )
        if _json_output:
            output(
                {
                    "success": True,
                    "file": str(p.resolve()),
                    "parameters": list(final.values()),
                }
            )
        else:
            click.echo(f"✓ Updated: {p.resolve()}")
            click.echo(f"  Parameters added: {', '.join(final.values())}")
    else:
        changed = parameterize_yaml_file(yaml_file)
        if _json_output:
            output({"success": True, "changed": changed, "file": str(p.resolve())})
