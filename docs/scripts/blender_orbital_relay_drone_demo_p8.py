# ruff: noqa: F403, F405, E501
from .blender_orbital_relay_drone_demo_base import *  # noqa: F403
# fmt: off
from .blender_orbital_relay_drone_demo_p7 import build_demo  # noqa: E402,E501
# fmt: on


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default="/root/preview-artifacts/20260422/blender-orbital-relay-drone-v6",
        help="Directory for the generated scene, preview bundles, live session, trajectory.json, final render, and motion video.",
    )
    parser.add_argument(
        "--no-live-preview",
        action="store_true",
        help="Skip stage-by-stage preview bundle capture.",
    )
    args = parser.parse_args()

    result = build_demo(Path(args.output_dir).expanduser().resolve(), use_live_preview=not args.no_live_preview)
    print(json.dumps(result, indent=2, ensure_ascii=False))
