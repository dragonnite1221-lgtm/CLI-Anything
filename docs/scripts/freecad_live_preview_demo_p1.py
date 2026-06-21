# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403


REPO_ROOT = Path(__file__).resolve().parents[2]
FREECAD_WORKDIR = REPO_ROOT / "freecad" / "agent-harness"
CLI_HUB_WORKDIR = REPO_ROOT / "cli-hub"
FREECAD_CLI = shutil.which("cli-anything-freecad") or "cli-anything-freecad"
CLI_HUB = shutil.which("cli-hub") or "cli-hub"
MONO_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_BOLD_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DISPLAY_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
VIDEO_W = 1600
VIDEO_H = 900
LEFT_W = 650
RIGHT_W = VIDEO_W - LEFT_W
FPS = 12
HOLD_TAIL_S = 2.5
DEFAULT_WAIT_TIMEOUT_S = 90.0
SHOWCASE_FRAME_COUNT = 12
SHOWCASE_DURATION_S = 7.0
SHOWCASE_HOLD_S = 1.1
TRUE_MOTION_DURATION_S = 6.0
TRUE_MOTION_KEYFRAME_COUNT = 13
SPIN_MOTION_DURATION_S = 7.0
SPIN_MOTION_KEYFRAME_COUNT = 19
COMBO_MOTION_DURATION_S = 9.0
COMBO_MOTION_KEYFRAME_COUNT = 25
COLORS = {
    "bg_top": "#030b16",
    "bg_bottom": "#081a2d",
    "grid": "#14314d",
    "grid_soft": "#0d2338",
    "panel": "#0b1522",
    "panel_soft": "#101d2f",
    "panel_line": "#224667",
    "panel_glow": "#2de2c5",
    "terminal_bg": "#07111b",
    "terminal_text": "#d9e7f5",
    "terminal_muted": "#6d839c",
    "terminal_success": "#8bf0c8",
    "terminal_error": "#ff8f98",
    "terminal_cmd": "#7ed6ff",
    "terminal_json": "#f7d488",
    "preview_shell": "#0b1220",
    "preview_stage": "#efe7da",
    "preview_stage_edge": "#cabca8",
    "preview_text": "#f2f5f8",
    "preview_muted": "#9fb2c8",
    "chip_bg": "#11263a",
    "chip_text": "#dfeaf5",
    "accent": "#23d7bb",
    "accent_warm": "#ff8a57",
    "accent_soft": "#173f40",
    "paper": "#f7f2ea",
    "paper_line": "#d2c6b5",
    "white": "#ffffff",
}
def _taipei_extend(steps, z):
    steps.extend(
        [
            {
                "id": "crown",
                "label": "Add crown block",
                "argv": [
                    "-p",
                    "{project_path}",
                    "part",
                    "add",
                    "box",
                    "--name",
                    "Crown",
                    "-P",
                    "length=9",
                    "-P",
                    "width=9",
                    "-P",
                    "height=8",
                    "-pos",
                    f"-4.5,-4.5,{z:.2f}",
                ],
                "wait_preview": True,
            },
            {
                "id": "spire-lower",
                "label": "Add lower spire",
                "argv": [
                    "-p",
                    "{project_path}",
                    "part",
                    "add",
                    "cylinder",
                    "--name",
                    "SpireLower",
                    "-P",
                    "radius=1.8",
                    "-P",
                    "height=14",
                    "-pos",
                    f"0,0,{z + 8.0:.2f}",
                ],
                "wait_preview": True,
            },
            {
                "id": "spire-upper",
                "label": "Add upper spire",
                "argv": [
                    "-p",
                    "{project_path}",
                    "part",
                    "add",
                    "cylinder",
                    "--name",
                    "SpireUpper",
                    "-P",
                    "radius=1.0",
                    "-P",
                    "height=12",
                    "-pos",
                    f"0,0,{z + 22.0:.2f}",
                ],
                "wait_preview": True,
            },
            {
                "id": "spire-tip",
                "label": "Add spire tip",
                "argv": [
                    "-p",
                    "{project_path}",
                    "part",
                    "add",
                    "cone",
                    "--name",
                    "SpireTip",
                    "-P",
                    "radius1=1.5",
                    "-P",
                    "radius2=0.18",
                    "-P",
                    "height=11",
                    "-pos",
                    f"0,0,{z + 34.0:.2f}",
                ],
                "wait_preview": True,
            },
        ]
    )
