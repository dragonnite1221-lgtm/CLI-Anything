# ruff: noqa: F403, F405, E501
from .qgis_cli_base import *  # noqa: F403

# fmt: off
from .qgis_cli_p1 import _requested_project_path, _sync_session_project_path, cli, handle_error, output  # noqa: E402,E501
from .qgis_cli_p2 import _auto_save_if_one_shot, _load_requested_project, _record, project  # noqa: E402,E501
# fmt: on


@project.command("open")
@click.argument("project_path", type=click.Path(path_type=Path))
@handle_error
def project_open(project_path: Path):
    """Open an existing QGIS project."""
    data = project_mod.open_project(str(project_path))
    _sync_session_project_path()
    _record("project open", {"project_path": str(project_path)}, data)
    output(data, f"Opened project: {data['path']}")


@project.command("save")
@click.argument("output_path", required=False, type=click.Path(path_type=Path))
@handle_error
def project_save(output_path: Path | None):
    """Save the current QGIS project."""
    if output_path is None:
        _load_requested_project(required=bool(_requested_project_path()))
    data = project_mod.save_project(str(output_path) if output_path else None)
    _sync_session_project_path()
    _record("project save", {"output": str(output_path) if output_path else None}, data)
    output(data, f"Saved project: {data['path']}")


@project.command("info")
@handle_error
def project_info():
    """Show information about the current QGIS project."""
    if _requested_project_path():
        _load_requested_project(required=True)
    data = project_mod.project_info()
    _record("project info", {}, data)
    output(data)


@project.command("set-crs")
@click.argument("crs")
@handle_error
def project_set_crs(crs: str):
    """Set the active project's CRS."""
    _load_requested_project(required=True)
    data = project_mod.set_project_crs(crs)
    _auto_save_if_one_shot()
    _record("project set-crs", {"crs": crs}, data)
    output(data, f"Updated project CRS to {crs}")


@cli.group()
def layer():
    """Layer management commands."""


@layer.command("create-vector")
@click.option("--name", required=True, help="Layer name")
@click.option(
    "--geometry",
    required=True,
    type=click.Choice(["point", "linestring", "polygon"], case_sensitive=False),
    help="Geometry type",
)
@click.option("--crs", default=None, help="Layer CRS, e.g. EPSG:4326")
@click.option("--field", "field_specs", multiple=True, help="Field spec as name:type")
@handle_error
def layer_create_vector(
    name: str, geometry: str, crs: str | None, field_specs: tuple[str, ...]
):
    """Create a GeoPackage-backed vector layer in the current project."""
    _load_requested_project(required=True)
    effective_crs = crs or project_mod.project_info().get("crs") or "EPSG:4326"
    data = layers_mod.create_vector_layer(name, geometry, effective_crs, field_specs)
    _auto_save_if_one_shot()
    _record(
        "layer create-vector",
        {
            "name": name,
            "geometry": geometry,
            "crs": effective_crs,
            "fields": list(field_specs),
        },
        data,
    )
    output(data, f"Created layer: {data['name']}")


@layer.command("list")
@handle_error
def layer_list():
    """List layers in the current project."""
    _load_requested_project(required=True)
    data = layers_mod.list_layers()
    _record("layer list", {}, data)
    output(data)


@layer.command("info")
@click.argument("identifier")
@handle_error
def layer_info(identifier: str):
    """Show detailed information for a layer."""
    _load_requested_project(required=True)
    data = layers_mod.layer_info(identifier)
    _record("layer info", {"identifier": identifier}, data)
    output(data)


@layer.command("remove")
@click.argument("identifier")
@handle_error
def layer_remove(identifier: str):
    """Remove a layer from the current project."""
    _load_requested_project(required=True)
    data = layers_mod.remove_layer(identifier)
    _auto_save_if_one_shot()
    _record("layer remove", {"identifier": identifier}, data)
    output(data, f"Removed layer: {data['name']}")


@cli.group()
def feature():
    """Feature editing commands."""


@feature.command("add")
@click.option(
    "--layer", "layer_identifier", required=True, help="Target layer id or name"
)
@click.option("--wkt", required=True, help="Geometry in WKT format")
@click.option(
    "--attr", "attr_specs", multiple=True, help="Feature attribute as key=value"
)
@handle_error
def feature_add(layer_identifier: str, wkt: str, attr_specs: tuple[str, ...]):
    """Add a feature to a vector layer using WKT geometry."""
    _load_requested_project(required=True)
    data = features_mod.add_feature(layer_identifier, wkt, list(attr_specs))
    _auto_save_if_one_shot()
    _record(
        "feature add",
        {"layer": layer_identifier, "wkt": wkt, "attrs": list(attr_specs)},
        data,
    )
    output(data, f"Added feature to {data['layer']['name']}")


@feature.command("list")
@click.option(
    "--layer", "layer_identifier", required=True, help="Target layer id or name"
)
@click.option(
    "--limit", default=20, show_default=True, type=int, help="Maximum features to show"
)
@handle_error
def feature_list(layer_identifier: str, limit: int):
    """List features from a vector layer."""
    _load_requested_project(required=True)
    data = features_mod.list_features(layer_identifier, limit=limit)
    _record("feature list", {"layer": layer_identifier, "limit": limit}, data)
    output(data)


@cli.group()
def layout():
    """Print layout authoring commands."""
