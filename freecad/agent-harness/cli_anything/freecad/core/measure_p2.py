# ruff: noqa: F403, F405, E501
from .measure_base import *  # noqa: F403

# fmt: off
from .measure_p1 import _compute_volume  # noqa: E402,E501
# fmt: on


def _compute_area(part: Dict[str, Any]) -> Optional[float]:
    """Compute surface area from primitive parameters. Returns *None* for unknowns."""
    p = part["params"]
    t = part["type"]

    if t == "box":
        l, w, h = p["length"], p["width"], p["height"]
        return 2.0 * (l * w + w * h + l * h)
    elif t == "cylinder":
        r, h = p["radius"], p["height"]
        return 2.0 * math.pi * r * (r + h)
    elif t == "sphere":
        return 4.0 * math.pi * p["radius"] ** 2
    elif t == "cone":
        r1, r2, h = p["radius1"], p["radius2"], p["height"]
        slant = math.sqrt((r1 - r2) ** 2 + h**2)
        return math.pi * r1**2 + math.pi * r2**2 + math.pi * (r1 + r2) * slant
    elif t == "torus":
        R, r = p["radius1"], p["radius2"]
        return 4.0 * math.pi**2 * R * r
    elif t == "wedge":
        dx = p["xmax"] - p["xmin"]
        dy = p["ymax"] - p["ymin"]
        dz = p["zmax"] - p["zmin"]
        return 2.0 * (dx * dy + dy * dz + dx * dz)
    return None


def _compute_inertia(part: Dict[str, Any]) -> Optional[Dict[str, float]]:
    """Estimate principal moments of inertia (Ixx, Iyy, Izz) assuming unit density."""
    p = part["params"]
    t = part["type"]
    vol = _compute_volume(part)
    if vol is None:
        return None
    m = vol  # unit density

    if t == "box":
        l, w, h = p["length"], p["width"], p["height"]
        return {
            "Ixx": m * (w**2 + h**2) / 12.0,
            "Iyy": m * (l**2 + h**2) / 12.0,
            "Izz": m * (l**2 + w**2) / 12.0,
        }
    elif t == "cylinder":
        r, h = p["radius"], p["height"]
        return {
            "Ixx": m * (3.0 * r**2 + h**2) / 12.0,
            "Iyy": m * (3.0 * r**2 + h**2) / 12.0,
            "Izz": m * r**2 / 2.0,
        }
    elif t == "sphere":
        r = p["radius"]
        I = 2.0 * m * r**2 / 5.0
        return {"Ixx": I, "Iyy": I, "Izz": I}
    elif t == "cone":
        r1, r2, h = p["radius1"], p["radius2"], p["height"]
        # Approximate using average radius
        r_avg = (r1 + r2) / 2.0
        return {
            "Ixx": m * (3.0 * r_avg**2 + h**2) / 12.0,
            "Iyy": m * (3.0 * r_avg**2 + h**2) / 12.0,
            "Izz": m * r_avg**2 / 2.0,
        }
    elif t == "torus":
        R, r = p["radius1"], p["radius2"]
        Ixx = m * (5.0 * r**2 + 4.0 * R**2) / 8.0
        return {
            "Ixx": Ixx,
            "Iyy": Ixx,
            "Izz": m * (3.0 * r**2 + 4.0 * R**2) / 4.0,
        }
    return None
