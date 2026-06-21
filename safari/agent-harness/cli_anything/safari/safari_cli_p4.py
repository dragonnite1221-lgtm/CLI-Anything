# ruff: noqa: F403, F405, E501
from .safari_cli_base import *  # noqa: F403

# fmt: off
from .safari_cli_p1 import _handle_error, handle_error  # noqa: E402,E501
from .safari_cli_p3 import tools_group  # noqa: E402,E501
# fmt: on


@tools_group.command("list")
@click.option("--filter", "pattern", default="", help="Substring to filter tool names")
@handle_error
def tools_list(pattern):
    """List every safari-mcp tool available to the CLI."""
    registry = load_registry()
    if _json_output:
        data = [
            {
                "name": t.name,
                "short_name": t.short_name,
                "description": t.description,
                "param_count": len(t.params),
            }
            for t in registry
            if pattern.lower() in t.name.lower()
        ]
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        return

    count = 0
    for t in registry:
        if pattern.lower() not in t.name.lower():
            continue
        count += 1
        desc = (t.description or "").split("\n", 1)[0]
        if len(desc) > 80:
            desc = desc[:77] + "..."
        click.echo(f"  {t.short_name:<30} {desc}")
    click.echo()
    click.echo(f"{count} tool(s) shown (registry version: {registry.source_version})")


@tools_group.command("describe")
@click.argument("tool_name")
@handle_error
def tools_describe(tool_name):
    """Show the full schema for a single tool."""
    registry = load_registry()
    tool = registry.get(tool_name) or registry.get_short(tool_name)
    if not tool:
        _handle_error(
            click.exceptions.UsageError(
                f"Unknown tool: {tool_name}. Use 'tools list' to see available tools."
            )
        )
        return

    if _json_output:
        click.echo(
            json.dumps(
                {
                    "name": tool.name,
                    "short_name": tool.short_name,
                    "description": tool.description,
                    "params": [
                        {
                            "name": p.name,
                            "cli_name": p.cli_name,
                            "type": p.type,
                            "description": p.description,
                            "required": p.required,
                            "default": p.default,
                            "choices": p.choices,
                        }
                        for p in tool.params
                    ],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    click.echo(f"Name:        {tool.name}")
    click.echo(f"CLI command: tool {tool.short_name}")
    click.echo(f"Description: {tool.description}")
    if not tool.params:
        click.echo("Parameters:  (none)")
        return
    click.echo("Parameters:")
    for p in tool.params:
        req = "required" if p.required else "optional"
        extra = f" [choices: {p.choices}]" if p.choices else ""
        default = f" [default: {p.default}]" if p.default is not None else ""
        click.echo(f"  --{p.cli_name} ({p.type}, {req}){extra}{default}")
        if p.description:
            click.echo(f"      {p.description}")


@tools_group.command("count")
@handle_error
def tools_count():
    """Print the number of tools in the bundled registry (for scripts)."""
    registry = load_registry()
    if _json_output:
        click.echo(json.dumps({"tool_count": len(registry)}))
    else:
        click.echo(str(len(registry)))
