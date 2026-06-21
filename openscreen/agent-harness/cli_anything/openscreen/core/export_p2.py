# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import BG_COLORS, _compute_geometry, _event_boundaries, _segment_crop  # noqa: E402,E501
# fmt: on


def render(
    session: Session,
    output_path: str,
    on_progress: Optional[Callable] = None,
) -> dict:
    """Render the project to a final video file.

    Args:
        session: Active session with open project.
        output_path: Destination file path.
        on_progress: Optional callback(stage, message).

    Returns:
        Dict with output path, file_size, duration, resolution.
    """
    if not session.is_open:
        raise RuntimeError("No project is open")

    editor = session.editor
    media = session.data.get("media", {})
    video_path = media.get("screenVideoPath")
    if not video_path:
        video_path = session.data.get("videoPath")
    if not video_path or not os.path.isfile(video_path):
        raise FileNotFoundError(
            f"Source video not found: {video_path}. "
            "Set it with: project set-video <path>"
        )

    # Probe source
    if on_progress:
        on_progress("probe", "Probing source video...")
    meta = ffmpeg_backend.probe(video_path)
    src_w, src_h = meta["width"], meta["height"]
    duration = meta["duration"]
    fps = min(int(meta["fps"]), 30)

    # Read editor state
    zoom_regions = editor.get("zoomRegions", [])
    speed_regions = editor.get("speedRegions", [])
    trim_regions = editor.get("trimRegions", [])
    crop_region = editor.get("cropRegion", {"x": 0, "y": 0, "width": 1, "height": 1})
    aspect_ratio = editor.get("aspectRatio", "16:9")
    padding_pct = editor.get("padding", 50)
    background = editor.get("wallpaper", "gradient_dark")

    (
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
    ) = _compute_geometry(aspect_ratio, padding_pct, crop_region, src_w, src_h)

    # Build timeline segments
    trim_ranges = [(t["startMs"] / 1000, t["endMs"] / 1000) for t in trim_regions]

    def is_trimmed(t):
        return any(ts <= t <= te for ts, te in trim_ranges)

    def get_speed_at(t):
        for sr in speed_regions:
            if sr["startMs"] / 1000 <= t < sr["endMs"] / 1000:
                return sr["speed"]
        return 1.0

    def get_zoom_at(t):
        for zr in zoom_regions:
            if zr["startMs"] / 1000 <= t < zr["endMs"] / 1000:
                return zr
        return None

    events = _event_boundaries(duration, zoom_regions, speed_regions, trim_regions)

    segments = []
    for i in range(len(events) - 1):
        s, e = events[i], events[i + 1]
        if e - s < 0.05:
            continue
        mid = (s + e) / 2
        if is_trimmed(mid):
            continue
        segments.append(
            {
                "start": s,
                "end": e,
                "speed": get_speed_at(mid),
                "zoom": get_zoom_at(mid),
            }
        )

    if not segments:
        segments = [{"start": 0, "end": duration, "speed": 1.0, "zoom": None}]

    if on_progress:
        on_progress("timeline", f"Built {len(segments)} segments")

    # Render segments
    tmpdir = tempfile.mkdtemp(prefix="openscreen_export_")
    seg_files = []

    for idx, seg in enumerate(segments):
        seg_file = os.path.join(tmpdir, f"seg_{idx:04d}.mp4")
        if on_progress:
            on_progress("segment", f"Segment {idx + 1}/{len(segments)}")

        crop = _segment_crop(
            seg, effective_w, effective_h, crop_x, crop_y, crop_w, crop_h, crop_region
        )

        ffmpeg_backend.render_segment(
            input_path=video_path,
            output_path=seg_file,
            start_s=seg["start"],
            end_s=seg["end"],
            target_w=vid_w,
            target_h=vid_h,
            fps=fps,
            speed=seg["speed"],
            crop=crop,
        )
        if os.path.exists(seg_file):
            seg_files.append(seg_file)

    if not seg_files:
        raise RuntimeError("No segments rendered successfully")

    # Concat
    if on_progress:
        on_progress("concat", f"Concatenating {len(seg_files)} segments")

    concat_out = os.path.join(tmpdir, "concat.mp4")
    ffmpeg_backend.concat_segments(seg_files, concat_out)

    # Composite on background
    if on_progress:
        on_progress("composite", "Adding background and padding")

    bg_color = BG_COLORS.get(background, "#1a1a2e")
    ffmpeg_backend.composite_on_background(
        input_path=concat_out,
        output_path=output_path,
        canvas_w=out_w,
        canvas_h=out_h,
        video_w=vid_w,
        video_h=vid_h,
        bg_color=bg_color,
        fps=fps,
    )

    # Verify output
    if on_progress:
        on_progress("verify", "Verifying output...")

    out_meta = ffmpeg_backend.probe(output_path)

    # Cleanup
    for f in seg_files + [concat_out]:
        try:
            os.remove(f)
        except OSError:
            pass
    try:
        os.rmdir(tmpdir)
    except OSError:
        pass

    return {
        "output": os.path.abspath(output_path),
        "file_size": out_meta["file_size"],
        "duration": out_meta["duration"],
        "width": out_meta["width"],
        "height": out_meta["height"],
        "codec": out_meta["codec"],
        "segments_rendered": len(seg_files),
    }
