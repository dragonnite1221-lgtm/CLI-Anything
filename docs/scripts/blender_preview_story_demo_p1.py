# ruff: noqa: F403, F405, E501
from .blender_preview_story_demo_base import *  # noqa: F403


REPO_ROOT = Path(__file__).resolve().parents[2]
FREECAD_DEMO_SCRIPT = Path(__file__).with_name("freecad_live_preview_demo.py")
def _load_style_module():
    spec = importlib.util.spec_from_file_location("freecad_live_preview_demo", FREECAD_DEMO_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
STYLE = _load_style_module()
VIDEO_W = STYLE.VIDEO_W
VIDEO_H = STYLE.VIDEO_H
LEFT_W = STYLE.LEFT_W
FPS = STYLE.FPS
COLORS = STYLE.COLORS
HOLD_TAIL_S = 1.4
BASELINE_START_S = 0.55
PREVIEW_SWITCH_LATENCY_S = 0.0
FINAL_STILL_STEP_S = 0.85
TURNTABLE_STEP_S = 0.7
DISPLAY_FONT_PATH = STYLE.DISPLAY_FONT_PATH
SANS_FONT_PATH = STYLE.SANS_FONT_PATH
MONO_FONT_PATH = STYLE.MONO_FONT_PATH
MONO_BOLD_FONT_PATH = STYLE.MONO_BOLD_FONT_PATH
def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
def write_json(path: Path, payload: Dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
def _stage_title(stage: Dict[str, Any]) -> str:
    stage_id = str(stage.get("stage") or "stage").strip()
    label = str(stage.get("label") or stage_id.replace("_", " ")).strip()
    prefix = stage_id.split("_", 1)[0]
    if prefix.isdigit():
        return f"Stage {prefix} · {label}"
    return label
def _stage_story(stage: Dict[str, Any]) -> str:
    return str(stage.get("story") or stage.get("label") or stage.get("stage") or "Build stage").strip()
def _stage_display_cmd(stage: Dict[str, Any]) -> str:
    return str(stage.get("display_cmd") or f"publish {stage.get('stage') or 'stage'}").strip()
