# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _output, _output_error  # noqa: E402,E501
from .sbox_cli_p12 import codegen  # noqa: E402,E501
# fmt: on


@codegen.command("component")
@click.option("--name", required=True, help="Component class name (PascalCase)")
@click.option("-o", "--output", "output_path", default=None, help="Output file path")
@click.option(
    "--properties",
    default=None,
    help="Properties as JSON array of {name, type, default?, category?}",
)
@click.option(
    "--methods",
    default=None,
    help="Comma-separated lifecycle methods (OnUpdate, OnFixedUpdate, OnStart)",
)
@click.option(
    "--networked",
    is_flag=True,
    help="Generate networked component (partial class, [Sync] attributes)",
)
@click.option("--interfaces", default=None, help="Comma-separated interface names")
@click.option(
    "--rpc-methods",
    default=None,
    help="RPC methods as Name:Type pairs (e.g. Fire:Broadcast,Die:Host)",
)
@click.pass_context
def codegen_component(
    ctx, name, output_path, properties, methods, networked, interfaces, rpc_methods
):
    """Generate a C# component class."""
    try:
        props = None
        if properties:
            props = json.loads(properties)

        method_list = None
        if methods:
            method_list = [m.strip() for m in methods.split(",")]

        iface_list = None
        if interfaces:
            iface_list = [i.strip() for i in interfaces.split(",")]

        rpc_list = None
        if rpc_methods:
            rpc_list = []
            for pair in rpc_methods.split(","):
                parts = pair.strip().split(":")
                rpc_list.append(
                    {
                        "name": parts[0].strip(),
                        "type": parts[1].strip() if len(parts) > 1 else "Broadcast",
                    }
                )

        result = codegen_mod.generate_component(
            class_name=name,
            properties=props,
            lifecycle_methods=method_list,
            interfaces=iface_list,
            is_networked=networked,
            rpc_methods=rpc_list,
        )

        if output_path:
            os.makedirs(
                os.path.dirname(output_path) if os.path.dirname(output_path) else ".",
                exist_ok=True,
            )
            with open(output_path, "w", encoding="utf-8", newline="\r\n") as f:
                f.write(result["content"])
            result["path"] = os.path.abspath(output_path)
        else:
            result["path"] = result["filename"]

        if ctx.obj.get("json"):
            _output(ctx, result)
        else:
            if output_path:
                click.echo(f"Generated {result['filename']} at {result['path']}")
            else:
                click.echo(f"--- {result['filename']} ---")
                click.echo(result["content"])
    except Exception as exc:
        _output_error(ctx, str(exc))


@codegen.command("gameresource")
@click.option("--name", required=True, help="GameResource class name")
@click.option("--display-name", default=None, help="Display name in editor")
@click.option("--extension", default=None, help="File extension for the resource")
@click.option("-o", "--output", "output_path", default=None, help="Output file path")
@click.option(
    "--properties",
    default=None,
    help="Properties as JSON array of {name, type, default?, category?}",
)
@click.pass_context
def codegen_gameresource(ctx, name, display_name, extension, output_path, properties):
    """Generate a GameResource class."""
    try:
        props = None
        if properties:
            props = json.loads(properties)

        result = codegen_mod.generate_gameresource(
            class_name=name,
            display_name=display_name or name,
            extension=extension or name.lower(),
            properties=props,
        )

        if output_path:
            os.makedirs(
                os.path.dirname(output_path) if os.path.dirname(output_path) else ".",
                exist_ok=True,
            )
            with open(output_path, "w", encoding="utf-8", newline="\r\n") as f:
                f.write(result["content"])
            result["path"] = os.path.abspath(output_path)
        else:
            result["path"] = result["filename"]

        if ctx.obj.get("json"):
            _output(ctx, result)
        else:
            if output_path:
                click.echo(f"Generated {result['filename']} at {result['path']}")
            else:
                click.echo(f"--- {result['filename']} ---")
                click.echo(result["content"])
    except Exception as exc:
        _output_error(ctx, str(exc))
