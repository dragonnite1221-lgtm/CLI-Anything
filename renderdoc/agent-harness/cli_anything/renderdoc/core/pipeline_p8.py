# ruff: noqa: F403, F405, E501
from .pipeline_base import *  # noqa: F403

# fmt: off
from .pipeline_p4 import _get_encoding_str  # noqa: E402,E501
from .pipeline_p7 import _serialize_cbuffer_var, _serialize_sig  # noqa: E402,E501
# fmt: on


def dump_shader_reflection(
    refl, include_file_contents: bool = False
) -> Optional[Dict[str, Any]]:
    """Serialize a ShaderReflection object to a JSON-friendly dict.

    Maps all fields from the RenderDoc Python API ShaderReflection class.

    Parameters
    ----------
    include_file_contents : bool
        If False (default), debugInfo.files[].contents is replaced with
        ``contents_length`` to avoid multi-MB JSON blobs.
        If True, the full source text is included (for disk export).
    """
    if refl is None:
        return None

    enc_str = _get_encoding_str(refl)
    raw = bytes(refl.rawBytes) if refl.rawBytes else b""

    result = {
        "resourceId": str(refl.resourceId),
        "entryPoint": str(refl.entryPoint),
        "encoding": enc_str,
        "stage": str(refl.stage) if hasattr(refl, "stage") else None,
        "rawBytes_size": len(raw),
    }

    # outputTopology / dispatchThreadsDimension
    if hasattr(refl, "outputTopology"):
        result["outputTopology"] = str(refl.outputTopology)
    if hasattr(refl, "dispatchThreadsDimension"):
        dim = refl.dispatchThreadsDimension
        result["dispatchThreadsDimension"] = [dim[0], dim[1], dim[2]]

    # constantBlocks
    cblocks = []
    for cb in refl.constantBlocks:
        entry = {
            "name": str(cb.name),
            "byteSize": cb.byteSize,
        }
        if hasattr(cb, "bindPoint"):
            entry["bindPoint"] = cb.bindPoint
        if hasattr(cb, "fixedBindNumber"):
            entry["fixedBindNumber"] = cb.fixedBindNumber
            entry["fixedBindSetOrSpace"] = cb.fixedBindSetOrSpace
        if cb.variables:
            entry["variables"] = [_serialize_cbuffer_var(v) for v in cb.variables]
        cblocks.append(entry)
    result["constantBlocks"] = cblocks

    # readOnlyResources
    def _serialize_resource(r):
        d = {"name": str(r.name)}
        if hasattr(r, "resType"):
            d["resType"] = str(r.resType)
        if hasattr(r, "textureType"):
            d["textureType"] = str(r.textureType)
        if hasattr(r, "fixedBindSetOrSpace"):
            d["fixedBindSetOrSpace"] = r.fixedBindSetOrSpace
            d["fixedBindNumber"] = r.fixedBindNumber
        if hasattr(r, "isTexture"):
            d["isTexture"] = r.isTexture
        if hasattr(r, "isReadOnly"):
            d["isReadOnly"] = r.isReadOnly
        return d

    result["readOnlyResources"] = [
        _serialize_resource(r) for r in refl.readOnlyResources
    ]
    result["readWriteResources"] = [
        _serialize_resource(r) for r in refl.readWriteResources
    ]

    # samplers
    samps = []
    for s in refl.samplers:
        d = {"name": str(s.name)}
        if hasattr(s, "fixedBindSetOrSpace"):
            d["fixedBindSetOrSpace"] = s.fixedBindSetOrSpace
            d["fixedBindNumber"] = s.fixedBindNumber
        samps.append(d)
    result["samplers"] = samps

    # signatures
    result["inputSignature"] = [_serialize_sig(s) for s in refl.inputSignature]
    result["outputSignature"] = [_serialize_sig(s) for s in refl.outputSignature]

    # interfaces
    if hasattr(refl, "interfaces"):
        result["interfaces"] = [str(i) for i in refl.interfaces]

    # debugInfo
    if refl.debugInfo:
        dbg = refl.debugInfo
        debug = {
            "debuggable": dbg.debuggable,
        }
        if hasattr(dbg, "compiler"):
            debug["compiler"] = str(dbg.compiler)
        if hasattr(dbg, "encoding"):
            debug["encoding"] = str(dbg.encoding)
        if hasattr(dbg, "debugStatus"):
            debug["debugStatus"] = str(dbg.debugStatus)
        if hasattr(dbg, "entrySourceName"):
            debug["entrySourceName"] = str(dbg.entrySourceName)
        try:
            flags = dbg.compileFlags
            if flags and hasattr(flags, "flags"):
                debug["compileFlags"] = [
                    {"name": str(f.name), "value": str(f.value)} for f in flags.flags
                ]
        except Exception as e:
            click.echo(f"Warning: failed to get compileFlags: {e}", err=True)
            debug["compileFlags"] = None
        try:
            if dbg.files:
                if include_file_contents:
                    debug["files"] = [
                        {
                            "filename": str(f.filename),
                            "contents": str(f.contents),
                        }
                        for f in dbg.files
                    ]
                else:
                    debug["files"] = [
                        {
                            "filename": str(f.filename),
                            "contents_length": len(str(f.contents)),
                        }
                        for f in dbg.files
                    ]
        except Exception as e:
            click.echo(f"Warning: failed to get files: {e}", err=True)
            debug["files"] = []
        result["debugInfo"] = debug
    else:
        result["debugInfo"] = None

    return result
