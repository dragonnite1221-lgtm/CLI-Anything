# ruff: noqa: F403, F405, E501
from .blender_orbital_relay_drone_demo_base import *  # noqa: F403
from .blender_orbital_relay_drone_demo_p8 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .blender_orbital_relay_drone_demo_p1 import REPO_ROOT, BLENDER_HARNESS_ROOT, _object_index, _material_index, _assign, _set_parent, _render_via_script, _encode_video, _copy_motion_stills, _render_live_html, _add_materials, _configure_scene  # noqa: F401,E501
from .blender_orbital_relay_drone_demo_p2 import _build_stage_00_launch_platform, _build_stage_01_hull_blockout, _build_stage_02_wing_structure  # noqa: F401,E501
from .blender_orbital_relay_drone_demo_p3 import _build_stage_03_solar_arrays, _build_stage_04_propulsion  # noqa: F401,E501
from .blender_orbital_relay_drone_demo_p4 import _build_stage_05_sensor_payload, _build_stage_06_service_rig, _assign_materials  # noqa: F401,E501
from .blender_orbital_relay_drone_demo_p5 import _rig_parents, _add_motion, _capture_stage  # noqa: F401,E501
from .blender_orbital_relay_drone_demo_p6 import _build_demo_part0, _build_demo_part1  # noqa: F401,E501
from .blender_orbital_relay_drone_demo_p7 import build_demo  # noqa: F401,E501
# fmt: on
