# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403


ZOOM_SCALES = {1: 1.25, 2: 1.5, 3: 1.8, 4: 2.2, 5: 3.5, 6: 5.0}
ASPECT_DIMENSIONS = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
    "4:3": (1440, 1080),
    "4:5": (1080, 1350),
    "16:10": (1920, 1200),
    "10:16": (1200, 1920),
}
BG_COLORS = {
    "gradient_dark": "#1a1a2e",
    "solid_dark": "#1a1a2e",
    "gradient_light": "#fdf6f0",
    "solid_light": "#f5f5f5",
    "gradient_sunset": "#2d1b3d",
    "blur": "#1a1a2e",
}


def list_presets() -> list[dict]:
    """List available export presets."""
    return [
        {
            "name": "mp4_good",
            "format": "mp4",
            "quality": "good",
            "description": "MP4 H.264, balanced quality",
        },
        {
            "name": "mp4_source",
            "format": "mp4",
            "quality": "source",
            "description": "MP4 H.264, source quality",
        },
        {
            "name": "mp4_medium",
            "format": "mp4",
            "quality": "medium",
            "description": "MP4 H.264, smaller file",
        },
        {
            "name": "gif_medium",
            "format": "gif",
            "quality": "medium",
            "description": "GIF, 720p, 15fps",
        },
    ]


def _event_boundaries(duration, zoom_regions, speed_regions, trim_regions):
    """Sorted, clamped set of timeline event boundary times (seconds)."""
    events = sorted(
        set(
            [0.0, duration]
            + [z["startMs"] / 1000 for z in zoom_regions]
            + [z["endMs"] / 1000 for z in zoom_regions]
            + [s["startMs"] / 1000 for s in speed_regions]
            + [s["endMs"] / 1000 for s in speed_regions]
            + [t["startMs"] / 1000 for t in trim_regions]
            + [t["endMs"] / 1000 for t in trim_regions]
        )
    )
    return [e for e in events if 0 <= e <= duration]


def _compute_geometry(aspect_ratio, padding_pct, crop_region, src_w, src_h):
    """Derive output/video/crop dimensions for the render pipeline."""
    out_w, out_h = ASPECT_DIMENSIONS.get(aspect_ratio, (1920, 1080))
    padding_scale = 1.0 - (padding_pct / 100.0) * 0.4
    vid_w = int(out_w * padding_scale)
    vid_h = int(out_h * padding_scale)

    crop_x = int(crop_region["x"] * src_w)
    crop_y = int(crop_region["y"] * src_h)
    crop_w = int(crop_region["width"] * src_w)
    crop_h = int(crop_region["height"] * src_h)
    effective_w = crop_w
    effective_h = crop_h

    src_ar = effective_w / effective_h
    if vid_w / vid_h > src_ar:
        vid_w = int(vid_h * src_ar)
    else:
        vid_h = int(vid_w / src_ar)
    vid_w -= vid_w % 2
    vid_h -= vid_h % 2
    out_w -= out_w % 2
    out_h -= out_h % 2
    return (
        out_w,
        out_h,
        vid_w,
        vid_h,
        crop_x,
        crop_y,
        crop_w,
        crop_h,
        effective_w,
        effective_h,
    )


def _segment_crop(
    seg, effective_w, effective_h, crop_x, crop_y, crop_w, crop_h, crop_region
):
    """Compute the ffmpeg crop rectangle for one timeline segment."""
    crop = None
    if seg["zoom"]:
        zr = seg["zoom"]
        zscale = ZOOM_SCALES.get(zr.get("depth", 3), 1.8)
        fx = max(0.05, min(0.95, zr["focus"]["cx"]))
        fy = max(0.05, min(0.95, zr["focus"]["cy"]))

        zw = int(effective_w / zscale)
        zh = int(effective_h / zscale)
        zw -= zw % 2
        zh -= zh % 2
        zx = max(0, min(effective_w - zw, int(fx * effective_w - zw / 2)))
        zy = max(0, min(effective_h - zh, int(fy * effective_h - zh / 2)))

        # Offset by crop region
        crop = {
            "w": zw,
            "h": zh,
            "x": crop_x + zx,
            "y": crop_y + zy,
        }
    elif crop_region != {"x": 0, "y": 0, "width": 1, "height": 1}:
        crop = {"w": crop_w, "h": crop_h, "x": crop_x, "y": crop_y}
    return crop
