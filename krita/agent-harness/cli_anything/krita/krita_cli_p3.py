# ruff: noqa: F403, F405, E501
from .krita_cli_base import *  # noqa: F403

# fmt: off
from .krita_cli_p1 import _load_project, _output, _save_current, cli, handle_error, project  # noqa: E402,E501
# fmt: on


@project.command("new")
@click.option("-n", "--name", default="Untitled", help="Project name.")
@click.option("-w", "--width", default=1920, type=int, help="Canvas width in pixels.")
@click.option("-h", "--height", default=1080, type=int, help="Canvas height in pixels.")
@click.option(
    "--colorspace", default="RGBA", help="Color space (RGBA, CMYKA, GRAYA, LABA, XYZA)."
)
@click.option("--depth", default="U8", help="Bit depth (U8, U16, F16, F32).")
@click.option("--resolution", default=300, type=int, help="DPI resolution.")
@click.option(
    "-o", "--output", type=click.Path(), default=None, help="Save project JSON to file."
)
@click.pass_context
@handle_error
def project_new(ctx, name, width, height, colorspace, depth, resolution, output):
    """Create a new Krita project."""
    global _current_project, _current_project_path
    proj = create_project(
        name=name,
        width=width,
        height=height,
        colorspace=colorspace,
        depth=depth,
        resolution=resolution,
    )
    _current_project = proj
    if output:
        save_project(proj, output)
        _current_project_path = output
    _session.snapshot(proj, f"Created project '{name}'")
    _output(
        {
            "status": "created",
            "name": name,
            "width": width,
            "height": height,
            "colorspace": colorspace,
            "depth": depth,
            "resolution": resolution,
            "saved_to": output or "(in memory)",
        },
        ctx,
    )


@project.command("open")
@click.argument("path", type=click.Path(exists=True))
@click.pass_context
@handle_error
def project_open(ctx, path):
    """Open an existing project JSON file."""
    global _current_project, _current_project_path
    proj = open_project(path)
    _current_project = proj
    _current_project_path = path
    _session.snapshot(proj, f"Opened project from '{path}'")
    info = project_info(proj)
    _output({"status": "opened", **info}, ctx)


@project.command("save")
@click.option(
    "-o", "--output", type=click.Path(), default=None, help="Save to a new path."
)
@click.pass_context
@handle_error
def project_save(ctx, output):
    """Save the current project."""
    global _current_project_path
    proj = _load_project(ctx)
    path = output or _current_project_path
    if not path:
        raise RuntimeError(
            "No output path specified. Use -o or open an existing project."
        )
    save_project(proj, path)
    _current_project_path = path
    _output({"status": "saved", "path": path}, ctx)


@project.command("info")
@click.pass_context
@handle_error
def project_info_cmd(ctx):
    """Show project information."""
    proj = _load_project(ctx)
    info = project_info(proj)
    _output(info, ctx)


@cli.group()
@click.pass_context
def layer(ctx):
    """Manage layers in the current project."""
    pass


@layer.command("add")
@click.argument("name")
@click.option(
    "-t",
    "--type",
    "layer_type",
    default="paintlayer",
    type=click.Choice(
        [
            "paintlayer",
            "grouplayer",
            "vectorlayer",
            "filterlayer",
            "filllayer",
            "clonelayer",
            "filelayer",
        ]
    ),
    help="Layer type.",
)
@click.option("--opacity", default=255, type=int, help="Layer opacity (0-255).")
@click.option("--blending", default="normal", help="Blending mode.")
@click.option("--hidden", is_flag=True, default=False, help="Create layer hidden.")
@click.pass_context
@handle_error
def layer_add(ctx, name, layer_type, opacity, blending, hidden):
    """Add a new layer to the project."""
    proj = _load_project(ctx)
    add_layer(
        proj,
        name,
        layer_type=layer_type,
        opacity=opacity,
        visible=not hidden,
        blending_mode=blending,
    )
    _session.snapshot(proj, f"Added layer '{name}'")
    _save_current(ctx)
    _output(
        {"status": "added", "layer": name, "type": layer_type, "opacity": opacity}, ctx
    )


@layer.command("remove")
@click.argument("name")
@click.pass_context
@handle_error
def layer_remove(ctx, name):
    """Remove a layer by name."""
    proj = _load_project(ctx)
    remove_layer(proj, name)
    _session.snapshot(proj, f"Removed layer '{name}'")
    _save_current(ctx)
    _output({"status": "removed", "layer": name}, ctx)


@layer.command("list")
@click.pass_context
@handle_error
def layer_list(ctx):
    """List all layers in the project."""
    proj = _load_project(ctx)
    layers = list_layers(proj)
    if ctx.obj.get("json"):
        click.echo(json.dumps(layers, indent=2))
    else:
        for i, lyr in enumerate(layers):
            vis = "visible" if lyr.get("visible", True) else "hidden"
            click.echo(
                f"  [{i}] {lyr['name']} ({lyr['type']}) opacity={lyr['opacity']} {vis}"
            )
