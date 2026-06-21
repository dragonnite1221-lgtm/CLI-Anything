# ruff: noqa: F403, F405, E501
from .layers_base import *  # noqa: F403

# fmt: off
from .layers_p1 import _all_layers, get_layer, layer_summary, parse_field_specs  # noqa: E402,E501
# fmt: on


def create_vector_layer(
    name: str,
    geometry: str,
    crs: str,
    field_specs: Iterable[str],
) -> dict:
    """Create a GeoPackage-backed vector layer and add it to the current project."""
    ensure_qgis_app()
    from qgis.core import (
        QgsCoordinateReferenceSystem,
        QgsField,
        QgsVectorFileWriter,
        QgsVectorLayer,
    )

    if any(layer.name() == name for layer in _all_layers()):
        raise QgisBackendError(f"Layer already exists: {name}")

    geometry_key = geometry.strip().lower()
    if geometry_key not in GEOMETRY_TYPES:
        raise QgisBackendError(
            f"Unsupported geometry type: {geometry}. Use point, linestring, or polygon."
        )

    crs_value = QgsCoordinateReferenceSystem(crs)
    if not crs_value.isValid():
        raise QgisBackendError(f"Invalid CRS: {crs}")

    fields = parse_field_specs(field_specs)
    project = project_mod.current_project()
    datastore_path = project_mod.default_datastore_path()

    memory_layer = QgsVectorLayer(
        f"{GEOMETRY_TYPES[geometry_key]}?crs={crs}", name, "memory"
    )
    if not memory_layer.isValid():
        raise QgisBackendError("Failed to create the in-memory source layer")

    provider = memory_layer.dataProvider()
    provider.addAttributes(
        [QgsField(field["name"], field["meta_type"]) for field in fields]
    )
    memory_layer.updateFields()

    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "GPKG"
    options.layerName = name
    if Path(datastore_path).exists():
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer

    error_code, error_message, new_filename, new_layer = (
        QgsVectorFileWriter.writeAsVectorFormatV3(
            memory_layer,
            datastore_path,
            project.transformContext(),
            options,
        )
    )
    if error_code != QgsVectorFileWriter.NoError:
        raise QgisBackendError(
            error_message or f"Failed to write layer to {datastore_path}"
        )

    stored_layer = QgsVectorLayer(
        f"{new_filename or datastore_path}|layername={new_layer or name}",
        name,
        "ogr",
    )
    if not stored_layer.isValid():
        raise QgisBackendError("Failed to reopen the GeoPackage-backed layer")

    project.addMapLayer(stored_layer)
    return layer_summary(stored_layer)


def remove_layer(identifier: str) -> dict:
    """Remove a layer from the active project."""
    project = project_mod.current_project()
    layer = get_layer(identifier)
    removed = layer_summary(layer)
    project.removeMapLayer(layer.id())
    return removed
