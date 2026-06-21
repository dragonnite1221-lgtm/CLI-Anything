# ruff: noqa: F403, F405, E501
from .layers_base import *  # noqa: F403


def _field_type_enum(type_name: str):
    from qgis.PyQt.QtCore import QMetaType

    normalized = type_name.strip().lower()
    if normalized not in FIELD_TYPES:
        raise QgisBackendError(
            f"Unsupported field type: {type_name}. Use one of: int, double, string, bool"
        )

    enum_name = FIELD_TYPES[normalized][1]
    return getattr(QMetaType.Type, enum_name), FIELD_TYPES[normalized][0]


def parse_field_specs(field_specs: Iterable[str]) -> list[dict]:
    """Parse repeated name:type field specifications."""
    parsed: list[dict] = []
    seen_names: set[str] = set()

    for spec in field_specs:
        name, separator, raw_type = spec.partition(":")
        if not separator or not name.strip() or not raw_type.strip():
            raise QgisBackendError(
                f"Invalid field specification: {spec}. Use name:type, e.g. name:string"
            )

        field_name = name.strip()
        if field_name in seen_names:
            raise QgisBackendError(f"Duplicate field name: {field_name}")

        field_type, normalized_type = _field_type_enum(raw_type)
        parsed.append(
            {
                "name": field_name,
                "meta_type": field_type,
                "type": normalized_type,
            }
        )
        seen_names.add(field_name)

    return parsed


def _all_layers():
    return list(project_mod.current_project().mapLayers().values())


def get_layer(identifier: str):
    """Resolve a layer by id or exact name."""
    project = project_mod.current_project()
    if identifier in project.mapLayers():
        return project.mapLayer(identifier)

    matches = [
        layer for layer in project.mapLayers().values() if layer.name() == identifier
    ]
    if not matches:
        raise QgisBackendError(f"Layer not found: {identifier}")
    if len(matches) > 1:
        raise QgisBackendError(
            f"Layer name is ambiguous: {identifier}. Use the layer id instead."
        )
    return matches[0]


def _layer_type_name(layer) -> str:
    from qgis.core import QgsMapLayerType

    if layer.type() == QgsMapLayerType.VectorLayer:
        return "vector"
    if layer.type() == QgsMapLayerType.RasterLayer:
        return "raster"
    return "other"


def _field_descriptions(layer) -> list[dict]:
    descriptions = []
    for field in layer.fields():
        descriptions.append(
            {
                "name": field.name(),
                "type": field.typeName() or str(field.type()),
            }
        )
    return descriptions


def layer_summary(layer) -> dict:
    """Return a stable summary for a QGIS layer."""
    from qgis.core import QgsMapLayerType, QgsWkbTypes

    layer_type = _layer_type_name(layer)
    summary = {
        "id": layer.id(),
        "name": layer.name(),
        "type": layer_type,
        "provider": layer.providerType(),
        "source": layer.source(),
        "crs": layer.crs().authid() if layer.crs().isValid() else None,
    }

    if layer.type() == QgsMapLayerType.VectorLayer:
        summary.update(
            {
                "geometry_type": QgsWkbTypes.displayString(layer.wkbType()),
                "feature_count": int(layer.featureCount()),
                "fields": _field_descriptions(layer),
            }
        )
    else:
        summary.update(
            {
                "geometry_type": None,
                "feature_count": None,
                "fields": [],
            }
        )

    return summary


def list_layers() -> dict:
    """List all layers in the active project."""
    layers = sorted(
        (layer_summary(layer) for layer in _all_layers()), key=lambda item: item["name"]
    )
    return {"count": len(layers), "layers": layers}


def layer_info(identifier: str) -> dict:
    """Return detailed information for a single layer."""
    return layer_summary(get_layer(identifier))
