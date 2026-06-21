# ruff: noqa: F403, F405, E501
from .transitions_base import *  # noqa: F403

# fmt: off
from .transitions_p4 import _get_user_transitions  # noqa: E402,E501
# fmt: on


def set_transition_param(
    session: Session, transition_index: int, param_name: str, param_value: str
) -> dict:
    """Set a parameter on a transition."""
    session.checkpoint()
    transitions = _get_user_transitions(session.root)

    if transition_index < 0 or transition_index >= len(transitions):
        raise IndexError(f"Transition index {transition_index} out of range")

    trans = transitions[transition_index]
    target = None
    for t in trans.findall("transition"):
        svc = mlt_xml.get_property(t, "mlt_service", "")
        if svc != "mix":
            target = t
            break
    if target is None:
        children = trans.findall("transition")
        if not children:
            raise RuntimeError("No editable transition found")
        target = children[0]

    old_value = mlt_xml.get_property(target, param_name)
    mlt_xml.set_property(target, param_name, param_value)

    return {
        "action": "set_transition_param",
        "transition_index": transition_index,
        "param": param_name,
        "old_value": old_value,
        "new_value": param_value,
    }


def list_transitions(session: Session) -> list[dict]:
    """List all transitions on the timeline."""
    transitions = _get_user_transitions(session.root)
    result = []
    for i, trans in enumerate(transitions):
        service = ""
        mix_service = ""
        props = {}
        for t in trans.findall("transition"):
            svc = mlt_xml.get_property(t, "mlt_service", "")
            if svc == "mix":
                if not mix_service:
                    mix_service = svc
            else:
                if not service:
                    service = svc
            for prop in t.findall("property"):
                name = prop.get("name", "")
                if name and name not in ("mlt_service", "a_track", "b_track"):
                    props[name] = prop.text or ""
        if not service:
            service = mix_service

        track_ids = [tr.get("producer", "") for tr in trans.findall("track")]

        result.append(
            {
                "index": i,
                "id": trans.get("id"),
                "service": service,
                "track_producers": track_ids,
                "in": trans.get("in"),
                "out": trans.get("out"),
                "params": props,
            }
        )
    return result


def _find_transitions_for_producer(
    root: ET.Element, producer_id: str
) -> list[ET.Element]:
    """Find all sub-tractor transitions that reference a producer."""
    result = []
    for trans in _get_user_transitions(root):
        for track in trans.findall("track"):
            if track.get("producer") == producer_id:
                result.append(trans)
                break
    return result
