# ruff: noqa: F403, F405, E501
from .workflow_demo_base import *  # noqa: F403
# fmt: off
from .workflow_demo_p1 import OUTPUT, PROJECT_FILE, VIDEO, _main_part0  # noqa: E402,E501
# fmt: on


def main():
    print("=" * 60)
    print("  Workflow: Social Media Highlight Reel")
    print("=" * 60)

    # ---- Step 1: Probe source media ----
    print("\n[1/8] Probing source media...")
    probe = media_mod.probe_media(VIDEO)
    print(f"  Source: {probe['filename']}")
    print(f"  Duration: {probe['duration_seconds']:.1f}s")
    if probe.get("video_streams"):
        v = probe["video_streams"][0]
        print(f"  Video: {v['width']}x{v['height']} @ {v['fps']}fps, {v['codec']}")
    if probe.get("audio_streams"):
        a = probe["audio_streams"][0]
        print(f"  Audio: {a['codec']}, {a['sample_rate']}Hz, {a['channels']}ch")

    # ---- Step 2: Create project ----
    print("\n[2/8] Creating project...")
    session = Session("highlight_reel")
    # Use 1080p30 as our output profile (will scale the vertical video)
    proj_mod.new_project(session, "hd1080p30")
    print("  Profile: HD 1080p @ 29.97fps")

    # ---- Step 3: Build timeline structure ----
    print("\n[3/8] Building timeline...")
    tl_mod.add_track(session, "video", "Main")
    tl_mod.add_track(session, "video", "Titles")
    tl_mod.add_track(session, "audio", "Music")

    tracks = tl_mod.list_tracks(session)
    for t in tracks:
        if t["type"] != "background":
            print(f"  Track {t['index']}: {t['name']} ({t['type']})")

    # ---- Step 4: Add clips — 3 segments from the source ----
    print("\n[4/8] Adding clips to timeline...")

    # Segment 1: Opening shot (trimmed — skip first 0.5s)
    tl_mod.add_clip(session, VIDEO, 1,
                    in_point="00:00:00.500", out_point="00:00:02.500",
                    caption="Opening Shot")
    print("  [0] Opening Shot: 0.5s → 2.5s (2.0s)")

    # Segment 2: Middle highlight
    tl_mod.add_clip(session, VIDEO, 1,
                    in_point="00:00:02.500", out_point="00:00:05.000",
                    caption="Highlight")
    print("  [1] Highlight: 2.5s → 5.0s (2.5s)")

    # Segment 3: Closing shot (trim last bit)
    tl_mod.add_clip(session, VIDEO, 1,
                    in_point="00:00:05.000", out_point="00:00:06.800",
                    caption="Closing")
    print("  [2] Closing: 5.0s → 6.8s (1.8s)")

    clips = [c for c in tl_mod.list_clips(session, 1) if "clip_index" in c]
    print(f"  Total clips on Main: {len(clips)}")

    # ---- Step 5: Apply filters (color grading + effects) ----
    print("\n[5/8] Applying filters...")

    # Segment 1: Title text + brightness bump + fade-in
    filt_mod.add_filter(session, "brightness", track_index=1, clip_index=0,
                        params={"level": "1.15"})
    filt_mod.add_filter(session, "fadein-video", track_index=1, clip_index=0,
                        params={"level": "00:00:00.000=0;00:00:00.500=1"})
    filt_mod.add_filter(session, "text", track_index=1, clip_index=0,
                        params={
                            "argument": "HIGHLIGHT REEL",
                            "size": "48",
                            "fgcolour": "#ffffffff",
                            "bgcolour": "#00000000",
                            "halign": "center",
                            "valign": "bottom",
                            "family": "Sans",
                        })
    print("  [0] Opening: brightness +15%, fade-in 0.5s, title overlay")

    # Segment 2: Warm color grade (boost saturation + slight hue shift)
    filt_mod.add_filter(session, "brightness", track_index=1, clip_index=1,
                        params={"level": "1.05"})
    filt_mod.add_filter(session, "saturation", track_index=1, clip_index=1,
                        params={"saturation": "1.3"})
    filt_mod.add_filter(session, "hue", track_index=1, clip_index=1,
                        params={"shift": "0.02"})
    print("  [1] Highlight: brightness +5%, saturation +30%, warm hue shift")

    # Segment 3: Sepia/vintage look + fade-out
    filt_mod.add_filter(session, "sepia", track_index=1, clip_index=2,
                        params={"u": "75", "v": "150"})
    filt_mod.add_filter(session, "brightness", track_index=1, clip_index=2,
                        params={"level": "0.9"})
    filt_mod.add_filter(session, "fadeout-video", track_index=1, clip_index=2,
                        params={"level": "00:00:00.000=1;00:00:01.500=0"})
    print("  [2] Closing: sepia tone, brightness -10%, fade-out 1.5s")

    # Audio: fade in and fade out on the whole audio track
    filt_mod.add_filter(session, "fadein-audio", track_index=3,
                        params={"level": "00:00:00.000=0;00:00:00.800=1"})
    filt_mod.add_filter(session, "fadeout-audio", track_index=3,
                        params={"level": "00:00:00.000=1;00:00:01.000=0"})
    print("  Audio: fade-in 0.8s, fade-out 1.0s")

    # ---- Step 6: Review timeline ----
    print("\n[6/8] Timeline overview:")
    timeline = tl_mod.show_timeline(session)
    for track in reversed(timeline["tracks"]):
        if track.get("type") == "background":
            continue
        name = track.get("name") or track.get("type", "?")
        clip_count = len([c for c in track.get("clips", []) if "clip_index" in c])
        filter_count = 0
        # Count filters on clips
        for c in track.get("clips", []):
            if "clip_index" in c:
                try:
                    f = filt_mod.list_filters(session, track["index"], c["clip_index"])
                    filter_count += len(f)
                except Exception:
                    pass
        print(f"  Track {track['index']} [{track['type'][0].upper()}] {name}: "
              f"{clip_count} clips, {filter_count} filters")

    # ---- Step 7: Save project ----
    print(f"\n[7/8] Saving project to {PROJECT_FILE}...")
    proj_mod.save_project(session, PROJECT_FILE)
    print(f"  Saved: {os.path.getsize(PROJECT_FILE)} bytes")

    # ---- Step 8: Export/Render ----
    print(f"\n[8/8] Rendering to {OUTPUT}...")
    _main_part0(session)

    # ---- Final summary ----
    print("\n" + "=" * 60)
    print("  Workflow complete!")
    print(f"  Project: {PROJECT_FILE}")
    if os.path.isfile(OUTPUT):
        size = os.path.getsize(OUTPUT)
        print(f"  Output:  {OUTPUT} ({size:,} bytes)")
        # Probe the output
        out_probe = media_mod.probe_media(OUTPUT)
        if out_probe.get("video_streams"):
            v = out_probe["video_streams"][0]
            print(f"  Video:   {v['width']}x{v['height']} @ {v['fps']}fps")
        print(f"  Duration: {out_probe.get('duration_seconds', 0):.1f}s")
    print("=" * 60)
