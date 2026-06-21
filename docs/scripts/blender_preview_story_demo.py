# ruff: noqa: F403, F405, E501
from .blender_preview_story_demo_base import *  # noqa: F403
from .blender_preview_story_demo_p7 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .blender_preview_story_demo_p1 import REPO_ROOT, FREECAD_DEMO_SCRIPT, _load_style_module, STYLE, VIDEO_W, VIDEO_H, LEFT_W, FPS, COLORS, HOLD_TAIL_S, BASELINE_START_S, PREVIEW_SWITCH_LATENCY_S, FINAL_STILL_STEP_S, TURNTABLE_STEP_S, DISPLAY_FONT_PATH, SANS_FONT_PATH, MONO_FONT_PATH, MONO_BOLD_FONT_PATH, load_json, write_json, _stage_title, _stage_story, _stage_display_cmd  # noqa: F401,E501
from .blender_preview_story_demo_p2 import build_trajectory  # noqa: F401,E501
from .blender_preview_story_demo_p3 import _fonts, _draw_text_right, progress_snapshot, pick_preview_event, build_command_cards, draw_global_header  # noqa: F401,E501
from .blender_preview_story_demo_p4 import draw_trace_panel  # noqa: F401,E501
from .blender_preview_story_demo_p5 import transform_turntable, concat_videos, parse_args, _paste_preview_card  # noqa: F401,E501
from .blender_preview_story_demo_p6 import draw_preview_panel  # noqa: F401,E501
from .blender_preview_story_demo_p7 import render_process_video, render_story  # noqa: F401,E501
# fmt: on
