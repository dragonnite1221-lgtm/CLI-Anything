# ruff: noqa: F403, F405, E501
from .state_adapter_base import *  # noqa: F403

# fmt: off
from .state_adapter_p1 import _copy_dict, _copy_list, _normalize_card_reward, _normalize_card_select, _normalize_combat, _normalize_combat_rewards, _normalize_event, _normalize_hand_select, _normalize_map, _normalize_rest_site, _normalize_shop  # noqa: E402,E501
# fmt: on


def _normalize_relic_select(raw_state: JsonDict, context: JsonDict) -> JsonDict:
    relic_select = _copy_dict(raw_state.get("relic_select"))
    return {
        "type": "decision",
        "decision": "relic_select",
        "context": context,
        "run": _copy_dict(raw_state.get("run")),
        "prompt": relic_select.get("prompt"),
        "relics": _copy_list(relic_select.get("relics")),
        "player": _copy_dict(relic_select.get("player")),
        "can_skip": relic_select.get("can_skip", False),
        "relic_select": relic_select,
    }


def _normalize_treasure(raw_state: JsonDict, context: JsonDict) -> JsonDict:
    treasure = _copy_dict(raw_state.get("treasure"))
    return {
        "type": "decision",
        "decision": "treasure",
        "context": context,
        "run": _copy_dict(raw_state.get("run")),
        "relics": _copy_list(treasure.get("relics")),
        "player": _copy_dict(treasure.get("player")),
        "can_proceed": treasure.get("can_proceed", False),
        "message": treasure.get("message"),
        "treasure": treasure,
    }


def _normalize_game_over(raw_state: JsonDict, context: JsonDict) -> JsonDict:
    game_over = _copy_dict(raw_state.get("game_over"))
    return {
        "type": "decision",
        "decision": "game_over",
        "context": context,
        "run": _copy_dict(raw_state.get("run")),
        "player": _copy_dict(game_over.get("player")),
        "screen_type": game_over.get("screen_type"),
        "can_return_to_main_menu": game_over.get("can_return_to_main_menu", False),
        "can_continue": game_over.get("can_continue", False),
        "can_view_run": game_over.get("can_view_run", False),
        "options": _copy_list(game_over.get("options")),
        "game_over": game_over,
    }


def normalize_state(raw_state: JsonDict) -> JsonDict:
    state_type = str(raw_state.get("state_type") or "unknown")
    run = _copy_dict(raw_state.get("run"))
    context = {
        "act": run.get("act"),
        "floor": run.get("floor"),
        "ascension": run.get("ascension"),
    }

    if state_type in {"monster", "elite", "boss"}:
        return _normalize_combat(raw_state, state_type, context)
    if state_type == "hand_select":
        return _normalize_hand_select(raw_state, context)
    if state_type == "card_reward":
        return _normalize_card_reward(raw_state, context)
    if state_type == "combat_rewards":
        return _normalize_combat_rewards(raw_state, context)
    if state_type == "map":
        return _normalize_map(raw_state, context)
    if state_type == "event":
        return _normalize_event(raw_state, context)
    if state_type == "rest_site":
        return _normalize_rest_site(raw_state, context)
    if state_type == "shop":
        return _normalize_shop(raw_state, context)
    if state_type == "card_select":
        return _normalize_card_select(raw_state, context)
    if state_type == "relic_select":
        return _normalize_relic_select(raw_state, context)
    if state_type == "treasure":
        return _normalize_treasure(raw_state, context)
    if state_type == "game_over":
        return _normalize_game_over(raw_state, context)
    if state_type == "menu":
        menu = _copy_dict(raw_state.get("menu"))
        return {
            "type": "status",
            "decision": "menu",
            "context": context,
            "run": run,
            "message": raw_state.get("message"),
            "screen": menu.get("screen"),
            "can_continue_game": menu.get("can_continue_game", False),
            "can_start_new_game": menu.get("can_start_new_game", False),
            "can_abandon_game": menu.get("can_abandon_game", False),
            "characters": _copy_list(menu.get("characters")),
            "ascension": menu.get("ascension"),
            "menu": menu,
        }
    if state_type == "overlay":
        return {
            "type": "status",
            "decision": "overlay",
            "context": context,
            "run": run,
            "overlay": _copy_dict(raw_state.get("overlay")),
        }
    return {
        "type": "status",
        "decision": "unknown",
        "context": context,
        "run": run,
        "raw_state_type": state_type,
        "message": raw_state.get("message"),
        "raw": raw_state,
    }
