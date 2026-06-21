# ruff: noqa: F403, F405, E501
from .document_base import *  # noqa: F403


def create_document(
    name: str = "untitled",
    width: float = 1920,
    height: float = 1080,
    units: str = "px",
    profile: Optional[str] = None,
    background: str = "#ffffff",
) -> Dict[str, Any]:
    """Create a new Inkscape document (JSON project)."""
    if profile and profile in PROFILES:
        p = PROFILES[profile]
        width = p["width"]
        height = p["height"]
        units = p["units"]

    if units not in VALID_UNITS:
        raise ValueError(
            f"Invalid units: {units}. Use one of: {', '.join(VALID_UNITS)}"
        )
    if width <= 0 or height <= 0:
        raise ValueError(f"Dimensions must be positive: {width}x{height}")

    viewbox = f"0 0 {width} {height}"

    project = {
        "version": PROJECT_VERSION,
        "name": name,
        "document": {
            "width": width,
            "height": height,
            "units": units,
            "viewBox": viewbox,
            "background": background,
        },
        "objects": [],
        "layers": [
            {
                "id": "layer1",
                "name": "Layer 1",
                "visible": True,
                "locked": False,
                "opacity": 1.0,
                "objects": [],
            }
        ],
        "gradients": [],
        "metadata": {
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "software": "inkscape-cli 1.0",
        },
    }
    return project


def open_document(path: str) -> Dict[str, Any]:
    """Open an .inkscape-cli.json project file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Document file not found: {path}")
    with open(path, "r") as f:
        project = json.load(f)
    if "version" not in project or "document" not in project:
        raise ValueError(f"Invalid document file: {path}")
    return project


def save_document(project: Dict[str, Any], path: str) -> str:
    """Save project to an .inkscape-cli.json file."""
    project["metadata"]["modified"] = datetime.now().isoformat()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(project, f, indent=2, default=str)
    return path


def _add_gradient_to_defs(defs, grad: Dict[str, Any]) -> None:
    """Add a gradient definition to the <defs> element."""
    import xml.etree.ElementTree as ET

    grad_type = grad.get("type", "linear")
    grad_id = grad.get("id", "gradient1")

    if grad_type == "linear":
        elem = ET.SubElement(
            defs,
            f"{{{SVG_NS}}}linearGradient",
            {
                "id": grad_id,
                "x1": str(grad.get("x1", 0)),
                "y1": str(grad.get("y1", 0)),
                "x2": str(grad.get("x2", 1)),
                "y2": str(grad.get("y2", 0)),
                "gradientUnits": grad.get("gradientUnits", "objectBoundingBox"),
            },
        )
    else:
        elem = ET.SubElement(
            defs,
            f"{{{SVG_NS}}}radialGradient",
            {
                "id": grad_id,
                "cx": str(grad.get("cx", 0.5)),
                "cy": str(grad.get("cy", 0.5)),
                "r": str(grad.get("r", 0.5)),
                "fx": str(grad.get("fx", grad.get("cx", 0.5))),
                "fy": str(grad.get("fy", grad.get("cy", 0.5))),
                "gradientUnits": grad.get("gradientUnits", "objectBoundingBox"),
            },
        )

    for stop in grad.get("stops", []):
        ET.SubElement(
            elem,
            f"{{{SVG_NS}}}stop",
            {
                "offset": str(stop.get("offset", 0)),
                "style": f"stop-color:{stop.get('color', '#000000')};stop-opacity:{stop.get('opacity', 1)}",
            },
        )
