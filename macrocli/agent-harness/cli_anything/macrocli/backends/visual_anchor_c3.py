# ruff: noqa: F403, F405, E501
from .visual_anchor_base import *  # noqa: F403
from .visual_anchor_p0 import _require_mss, _require_pil  # noqa: F401,E501


class VisualAnchorBackendMixin3:
    def _capture_region(self, p: dict, context: BackendContext) -> dict:
        """Screenshot a region of the screen and save as a template."""
        output_path = p.get("output", "")
        if not output_path:
            raise ValueError("capture_region requires 'output' param.")

        x = int(p.get("x", 0))
        y = int(p.get("y", 0))
        width = int(p.get("width", 100))
        height = int(p.get("height", 50))

        mss = _require_mss()
        Image = _require_pil()

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with mss.mss() as sct:
            region = {"left": x, "top": y, "width": width, "height": height}
            raw = sct.grab(region)
            img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
            img.save(output_path)

        size = Path(output_path).stat().st_size
        return {
            "saved": output_path,
            "region": [x, y, width, height],
            "file_size": size,
        }
