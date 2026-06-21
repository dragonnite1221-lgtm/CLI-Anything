# ruff: noqa: F403, F405, E501
from .macrocli_cli_base import *  # noqa: F403

# fmt: off
from .macrocli_cli_p1 import handle_error, output  # noqa: E402,E501
from .macrocli_cli_p2 import macro  # noqa: E402,E501
# fmt: on


@macro.command("define")
@click.argument("name")
@click.option("--output", "-o", default=None, help="Write YAML to this file path.")
@handle_error
def macro_define(name, output):
    """Scaffold a new macro YAML definition."""
    import textwrap

    template = textwrap.dedent(f"""\
        name: {name}
        version: "1.0"
        description: "Describe what this macro does."
        tags: []

        parameters:
          # Add your parameters here
          # output:
          #   type: string
          #   required: true
          #   description: Output file path
          #   example: /tmp/result.txt

        preconditions:
          # Conditions that must be true before execution
          # - file_exists: /path/to/input
          # - process_running: my-app

        steps:
          - id: step_1
            backend: native_api   # or: file_transform, semantic_ui, gui_macro
            action: run_command
            params:
              command: [echo, "Hello from {name}"]
            timeout_ms: 30000
            on_failure: fail       # or: skip, continue

        postconditions:
          # Conditions verified after execution
          # - file_exists: ${{output}}

        outputs:
          # Named outputs the agent can use
          # - name: result_file
          #   path: ${{output}}

        agent_hints:
          danger_level: safe      # safe | moderate | dangerous
          side_effects: []
          reversible: true
    """)
    if output:
        from pathlib import Path

        p = Path(output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(template, encoding="utf-8")
        if _json_output:
            click.echo(json.dumps({"created": str(p.resolve())}))
        else:
            click.echo(f"✓ Macro scaffold written to: {p.resolve()}")
    else:
        click.echo(template)
