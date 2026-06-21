# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
from .freecad_live_preview_demo_p42 import main  # noqa: F401


if __name__ == "__main__":
    raise SystemExit(main())

# fmt: off
# re-export full surface
from .freecad_live_preview_demo_p1 import REPO_ROOT, FREECAD_WORKDIR, CLI_HUB_WORKDIR, FREECAD_CLI, CLI_HUB, MONO_FONT_PATH, MONO_BOLD_FONT_PATH, SANS_FONT_PATH, DISPLAY_FONT_PATH, VIDEO_W, VIDEO_H, LEFT_W, RIGHT_W, FPS, HOLD_TAIL_S, DEFAULT_WAIT_TIMEOUT_S, SHOWCASE_FRAME_COUNT, SHOWCASE_DURATION_S, SHOWCASE_HOLD_S, TRUE_MOTION_DURATION_S, TRUE_MOTION_KEYFRAME_COUNT, SPIN_MOTION_DURATION_S, SPIN_MOTION_KEYFRAME_COUNT, COMBO_MOTION_DURATION_S, COMBO_MOTION_KEYFRAME_COUNT, COLORS, _taipei_extend  # noqa: F401,E501
from .freecad_live_preview_demo_p10 import __curiosity_steps_lg0_3  # noqa: F401,E501
from .freecad_live_preview_demo_p11 import __curiosity_steps_lg0_4  # noqa: F401,E501
from .freecad_live_preview_demo_p12 import __curiosity_steps_lg0_5  # noqa: F401,E501
from .freecad_live_preview_demo_p13 import __curiosity_steps_lg0_6  # noqa: F401,E501
from .freecad_live_preview_demo_p14 import __curiosity_steps_lg0_7  # noqa: F401,E501
from .freecad_live_preview_demo_p15 import __curiosity_steps_lg0_8  # noqa: F401,E501
from .freecad_live_preview_demo_p16 import __curiosity_steps_lg0_9  # noqa: F401,E501
from .freecad_live_preview_demo_p17 import __curiosity_steps_lg0_10  # noqa: F401,E501
from .freecad_live_preview_demo_p18 import __curiosity_steps_lg0_11  # noqa: F401,E501
from .freecad_live_preview_demo_p19 import __curiosity_steps_lg0_12  # noqa: F401,E501
from .freecad_live_preview_demo_p2 import _taipei_loop, _taipei_101_steps  # noqa: F401,E501
from .freecad_live_preview_demo_p20 import __curiosity_steps_lg0_13  # noqa: F401,E501
from .freecad_live_preview_demo_p21 import __curiosity_steps_lg0_14  # noqa: F401,E501
from .freecad_live_preview_demo_p22 import __curiosity_steps_lg0_15  # noqa: F401,E501
from .freecad_live_preview_demo_p23 import __curiosity_steps_lg0_16  # noqa: F401,E501
from .freecad_live_preview_demo_p24 import __curiosity_steps_lg0_17, _curiosity_steps, _mod_cg0_0, _mod_cg3_0  # noqa: F401,E501
from .freecad_live_preview_demo_p25 import _mod_cg4_0  # noqa: F401,E501
from .freecad_live_preview_demo_p26 import _mod_cg4_1, _mod_cg3_1, _mod_cg0_1, _mod_cg1_0  # noqa: F401,E501
from .freecad_live_preview_demo_p27 import _mod_cg2_0  # noqa: F401,E501
from .freecad_live_preview_demo_p28 import _mod_cg2_1  # noqa: F401,E501
from .freecad_live_preview_demo_p29 import _mod_cg2_2, _mod_cg1_1, _mod_cg0_2, _mod_cg0_3, SCENARIOS, now_iso, get_scenario, ensure_clean_dir, load_json, write_json, shlex_quote, format_cmd, run_cli, _load_motion_module, _is_noop_alignment  # noqa: F401,E501
from .freecad_live_preview_demo_p3 import __mars_rover_steps_lg0_0  # noqa: F401,E501
from .freecad_live_preview_demo_p30 import wait_for_bundle_update, extract_bundle_artifacts, generate_live_html  # noqa: F401,E501
from .freecad_live_preview_demo_p31 import collect_demo  # noqa: F401,E501
from .freecad_live_preview_demo_p32 import fit_image, _make_box_part, _curiosity_showcase_project, _apply_curiosity_showcase_pose  # noqa: F401,E501
from .freecad_live_preview_demo_p33 import generate_curiosity_showcase_sequence, _apply_curiosity_true_motion_pose, _curiosity_motion_pivot, _rotate_xy  # noqa: F401,E501
from .freecad_live_preview_demo_p34 import _apply_curiosity_spin_motion_pose, _apply_curiosity_combo_motion_pose  # noqa: F401,E501
from .freecad_live_preview_demo_p35 import generate_curiosity_true_motion_showcase  # noqa: F401,E501
from .freecad_live_preview_demo_p36 import load_font, _hex_rgb, _rgba, _mix, _trim_middle, _wrap_trimmed, _readable_command_text, _draw_text_right, _alpha_box, _draw_panel, _draw_chip, _draw_segment_bar  # noqa: F401,E501
from .freecad_live_preview_demo_p37 import _draw_soft_glow, build_static_backdrop, text_lines, build_terminal_lines, pick_preview_event, progress_snapshot  # noqa: F401,E501
from .freecad_live_preview_demo_p38 import build_command_cards, draw_global_header  # noqa: F401,E501
from .freecad_live_preview_demo_p39 import draw_terminal_panel  # noqa: F401,E501
from .freecad_live_preview_demo_p4 import __mars_rover_steps_lg0_1  # noqa: F401,E501
from .freecad_live_preview_demo_p40 import compose_showcase_frame, parse_args  # noqa: F401,E501
from .freecad_live_preview_demo_p41 import _paste_preview_card, compose_preview_dashboard, draw_preview_panel  # noqa: F401,E501
from .freecad_live_preview_demo_p42 import render_video  # noqa: F401,E501
from .freecad_live_preview_demo_p5 import __mars_rover_steps_lg0_2  # noqa: F401,E501
from .freecad_live_preview_demo_p6 import __mars_rover_steps_lg0_3, _mars_rover_steps  # noqa: F401,E501
from .freecad_live_preview_demo_p7 import __curiosity_steps_lg0_0  # noqa: F401,E501
from .freecad_live_preview_demo_p8 import __curiosity_steps_lg0_1  # noqa: F401,E501
from .freecad_live_preview_demo_p9 import __curiosity_steps_lg0_2  # noqa: F401,E501
# fmt: on
