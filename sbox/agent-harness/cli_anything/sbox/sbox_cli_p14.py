# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _output, _output_error  # noqa: E402,E501
from .sbox_cli_p12 import codegen  # noqa: E402,E501
# fmt: on


@codegen.command("editor-menu")
@click.option("--name", required=True, help="Editor menu class name")
@click.option("--menu-path", default=None, help="Menu path (e.g. Tools/My Tool)")
@click.option("-o", "--output", "output_path", default=None, help="Output file path")
@click.pass_context
def codegen_editor_menu(ctx, name, menu_path, output_path):
    """Generate an editor menu class."""
    try:
        result = codegen_mod.generate_editor_menu(
            class_name=name,
            menu_path=menu_path or f"Tools/{name}",
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


@codegen.command("razor")
@click.option("--name", required=True, help="Component class name (PascalCase)")
@click.option("--inherits", default="PanelComponent", help="Base class")
@click.option("--properties", default=None, help="Properties as JSON array")
@click.option("--root-class", default=None, help="CSS class for root element")
@click.option(
    "-o", "--output", "output_path", default=None, help="Output .razor file path"
)
@click.pass_context
def codegen_razor(ctx, name, inherits, properties, root_class, output_path):
    """Generate a Razor UI component."""
    try:
        props = json.loads(properties) if properties else None
        result = codegen_mod.generate_razor(
            name, inherits=inherits, properties=props, root_class=root_class
        )

        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result["content"])
            # Also write scss
            if output_path.endswith(".razor"):
                scss_path = output_path + ".scss"
            elif output_path.endswith(".scss"):
                scss_path = output_path
            else:
                scss_path = output_path + ".scss"
            with open(scss_path, "w", encoding="utf-8") as f:
                f.write(result["scss_content"])
            result["path"] = os.path.abspath(output_path)
            result["scss_path"] = os.path.abspath(scss_path)

        _output(
            ctx,
            result,
            lambda d: (
                f"Razor component '{d['class_name']}' generated"
                + (f" at {d.get('path', '')}" if d.get("path") else "")
            ),
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@codegen.command("class")
@click.option("--name", required=True, help="Class name (PascalCase)")
@click.option("--base-class", default=None, help="Base class to inherit from")
@click.option("--static", "is_static", is_flag=True, help="Generate a static class")
@click.option("--properties", default=None, help="Properties as JSON array")
@click.option("--methods", default=None, help="Methods as JSON array")
@click.option(
    "-o", "--output", "output_path", default=None, help="Output .cs file path"
)
@click.pass_context
def codegen_class(ctx, name, base_class, is_static, properties, methods, output_path):
    """Generate a plain C# class."""
    try:
        props = json.loads(properties) if properties else None
        meths = json.loads(methods) if methods else None
        result = codegen_mod.generate_class(
            name,
            base_class=base_class,
            is_static=is_static,
            properties=props,
            methods=meths,
        )

        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result["content"])
            result["path"] = os.path.abspath(output_path)

        _output(
            ctx,
            result,
            lambda d: (
                f"Class '{d['class_name']}' generated"
                + (f" at {d.get('path', '')}" if d.get("path") else "")
            ),
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))
