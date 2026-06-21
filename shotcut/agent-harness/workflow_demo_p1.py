# ruff: noqa: F403, F405, E501
from .workflow_demo_base import *  # noqa: F403


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
VIDEO = "/root/shotcut/1.mp4"
OUTPUT = "/root/shotcut/agent-harness/output.mp4"
PROJECT_FILE = "/root/shotcut/agent-harness/highlight_reel.mlt"
def _main_part0(session):
    try:
        result = export_mod.render(session, OUTPUT, preset="default", overwrite=True)
        if result.get("action") == "render":
            size = result.get("size_bytes", 0)
            print(f"  Render complete!")
            print(f"  Output: {OUTPUT}")
            print(f"  Size: {size:,} bytes ({size/1024:.1f} KB)")
            print(f"  Method: {result.get('method', 'unknown')}")
        elif result.get("action") == "render_script":
            print(f"  Render script generated (no direct rendering available)")
            print(f"  MLT project: {result.get('project_file')}")
            print(f"  Run manually: {result.get('melt_command')}")
        else:
            print(f"  Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"  Render error: {e}")
        print(f"  (This is expected if the render pipeline needs melt for complex projects)")
        print(f"  Falling back to direct ffmpeg rendering...")

        # Direct ffmpeg fallback for our specific workflow
        import subprocess
        # Concat our 3 segments with re-encoding
        cmd = [
            "ffmpeg", "-y",
            "-ss", "0.5", "-to", "2.5", "-i", VIDEO,
            "-ss", "2.5", "-to", "5.0", "-i", VIDEO,
            "-ss", "5.0", "-to", "6.8", "-i", VIDEO,
            "-filter_complex",
            # Segment 0: brightness + fade in
            "[0:v]eq=brightness=0.06:saturation=1[v0_graded];"
            "[v0_graded]fade=t=in:st=0:d=0.5[v0];"
            # Segment 1: warm grade
            "[1:v]eq=brightness=0.02:saturation=1.3[v1];"
            # Segment 2: sepia-ish + fade out
            "[2:v]eq=brightness=-0.04:saturation=0.3[v2_graded];"
            "[v2_graded]fade=t=out:st=0:d=1.5[v2];"
            # Concat video
            "[v0][v1][v2]concat=n=3:v=1:a=0[vout];"
            # Concat audio with fades
            "[0:a]afade=t=in:st=0:d=0.8[a0];"
            "[1:a]anull[a1];"
            "[2:a]afade=t=out:st=0:d=1.0[a2];"
            "[a0][a1][a2]concat=n=3:v=0:a=1[aout]",
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-crf", "21", "-preset", "medium",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            OUTPUT,
        ]
        print(f"  Running ffmpeg directly...")
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode == 0 and os.path.isfile(OUTPUT):
            size = os.path.getsize(OUTPUT)
            print(f"  Render complete!")
            print(f"  Output: {OUTPUT}")
            print(f"  Size: {size:,} bytes ({size/1024:.1f} KB)")
        else:
            print(f"  ffmpeg error: {r.stderr[-500:]}")
