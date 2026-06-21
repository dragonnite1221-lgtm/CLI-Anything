# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import _project_has_draw_ops  # noqa: E402,E501
from .export_p5 import _render_via_pillow  # noqa: E402,E501
# fmt: on


def render(
    project: Dict[str, Any],
    output_path: str,
    preset: str = "png",
    overwrite: bool = False,
    quality: Optional[int] = None,
    format_override: Optional[str] = None,
) -> Dict[str, Any]:
    """Render the project: flatten layers, apply filters, export.

    Tries the GIMP Script-Fu backend first (native image processing via
    ``gimp -i -b``).  Falls back to Pillow when GIMP is not installed.
    """
    # --- GIMP-native rendering (preferred) ---
    try:
        from cli_anything.gimp.utils.gimp_backend import is_available, render_project

        if is_available() and not _project_has_draw_ops(project):
            return render_project(
                project,
                output_path,
                preset=preset,
                overwrite=overwrite,
                quality=quality,
                format_override=format_override,
            )
    except Exception:
        pass  # fall through to Pillow

    # --- Pillow fallback ---
    return _render_via_pillow(
        project,
        output_path,
        preset=preset,
        overwrite=overwrite,
        quality=quality,
        format_override=format_override,
    )
