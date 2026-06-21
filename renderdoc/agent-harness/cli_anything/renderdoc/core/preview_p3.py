# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def _diff_part0(artifacts, bundle_dir, outputs_a, outputs_b, warnings):
    for side, output_results in (("A", outputs_a), ("B", outputs_b)):
        for index, item in enumerate(output_results):
            if item.get("error") or not item.get("path") or not os.path.isfile(item["path"]):
                warnings.append(item.get("error", f"missing output target {side}{index}"))
                continue
            artifacts.append(
                artifact_record(
                    bundle_dir,
                    item["path"],
                    artifact_id=f"{side.lower()}_output_{index:02d}",
                    role="gallery",
                    kind="image",
                    label=f"{side} {item.get('label', f'Output {index}')}",
                )
            )
def _diff_part1(artifacts, bundle_dir, capture_path_a, thumb_a, thumb_a_result):
    if not thumb_a_result.get("error") and os.path.isfile(thumb_a):
        artifacts.append(
            artifact_record(
                bundle_dir,
                thumb_a,
                artifact_id="capture_a_thumb",
                role="gallery",
                kind="image",
                label=f"{os.path.basename(capture_path_a)} thumbnail",
            )
        )
def _diff_part2(artifacts, bundle_dir, capture_path_b, thumb_b, thumb_b_result):
    if not thumb_b_result.get("error") and os.path.isfile(thumb_b):
        artifacts.append(
            artifact_record(
                bundle_dir,
                thumb_b,
                artifact_id="capture_b_thumb",
                role="gallery",
                kind="image",
                label=f"{os.path.basename(capture_path_b)} thumbnail",
            )
        )
