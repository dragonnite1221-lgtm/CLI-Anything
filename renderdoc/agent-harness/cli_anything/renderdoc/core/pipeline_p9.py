# ruff: noqa: F403, F405, E501
from .pipeline_base import *  # noqa: F403


def _serialize_used_descriptor(idx, used) -> Dict[str, Any]:
    """Serialize a UsedDescriptor to dict."""
    desc = used.descriptor
    entry_d = {"index": idx, "resource": str(desc.resource)}
    if hasattr(desc, "type"):
        entry_d["type"] = str(desc.type)
    if hasattr(desc, "textureType"):
        entry_d["textureType"] = str(desc.textureType)
    if hasattr(desc, "byteOffset"):
        entry_d["byteOffset"] = desc.byteOffset
    if hasattr(desc, "byteSize") and desc.byteSize:
        entry_d["byteSize"] = desc.byteSize
    return entry_d


def dump_stage_bindings(controller, pipe, pso, stage, refl) -> Dict[str, Any]:
    """Serialize GPU runtime bindings for a shader stage.

    Returns the actual resources bound at capture time:
    constant buffers, textures, UAVs, samplers.

    Note: GetConstantBlock(stage, idx, 0) is per-index.
    GetReadOnlyResources(stage), GetReadWriteResources(stage),
    GetSamplers(stage) return full lists.
    """
    bindings = {}

    # Constant block bindings (per-index API)
    cb_bindings = []
    for idx in range(len(refl.constantBlocks)):
        try:
            cb = pipe.GetConstantBlock(stage, idx, 0)
            desc = cb.descriptor
            cb_bindings.append(
                {
                    "index": idx,
                    "resource": str(desc.resource),
                    "byteOffset": desc.byteOffset,
                    "byteSize": desc.byteSize,
                }
            )
        except Exception as e:
            click.echo(f"Warning: failed to read constant block {idx}: {e}", err=True)
            cb_bindings.append(
                {
                    "index": idx,
                    "error": "failed to read",
                }
            )
    bindings["constantBlocks"] = cb_bindings

    # Read-only resource bindings (list API)
    try:
        ro_list = pipe.GetReadOnlyResources(stage)
        bindings["readOnlyResources"] = [
            _serialize_used_descriptor(i, used) for i, used in enumerate(ro_list)
        ]
    except Exception as e:
        click.echo(f"Warning: failed to get readOnlyResources: {e}", err=True)
        bindings["readOnlyResources"] = []

    # Read-write resource bindings (list API)
    try:
        rw_list = pipe.GetReadWriteResources(stage)
        bindings["readWriteResources"] = [
            _serialize_used_descriptor(i, used) for i, used in enumerate(rw_list)
        ]
    except Exception as e:
        click.echo(f"Warning: failed to get readWriteResources: {e}", err=True)
        bindings["readWriteResources"] = []

    # Sampler bindings (list API)
    try:
        sam_list = pipe.GetSamplers(stage)
        bindings["samplers"] = [
            _serialize_used_descriptor(i, used) for i, used in enumerate(sam_list)
        ]
    except Exception as e:
        click.echo(f"Warning: failed to get samplers: {e}", err=True)
        bindings["samplers"] = []

    return bindings
