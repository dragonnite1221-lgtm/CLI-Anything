# ruff: noqa: F403, F405, E501
from .pipeline_base import *  # noqa: F403


def _extract_debug_source(refl, enc_str: str):
    """Try to extract embedded debug source from ShaderReflection.

    Returns ``(source_text, extension)`` or ``(None, None)``.
    """
    if not refl.debugInfo or not refl.debugInfo.files:
        return None, None

    for f in refl.debugInfo.files:
        contents = str(f.contents)
        if not contents:
            continue

        # Determine file extension from debug encoding
        ext = None
        if hasattr(refl.debugInfo, "encoding"):
            dbg_enc = str(refl.debugInfo.encoding)
            if "HLSL" in dbg_enc:
                ext = ".hlsl"
            elif "GLSL" in dbg_enc:
                ext = ".glsl"

        if ext is None:
            # Guess from filename
            fname = str(f.filename)
            if fname.endswith(".hlsl"):
                ext = ".hlsl"
            elif fname.endswith(".glsl"):
                ext = ".glsl"

        if ext is None:
            # Guess from shader encoding: SPIR-V → GLSL, DXBC/DXIL → HLSL
            if enc_str in ("SPIRV", "OpenGLSPIRV"):
                ext = ".glsl"
            else:
                ext = ".hlsl"

        return contents, ext

    return None, None
