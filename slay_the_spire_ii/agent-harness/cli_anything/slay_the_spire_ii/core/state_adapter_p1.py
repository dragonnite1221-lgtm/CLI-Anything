# ruff: noqa: F403, F405, E501
from .state_adapter_base import *  # noqa: F403


def _copy_dict(value: Any) -> JsonDict:
    return dict(value) if isinstance(value, dict) else {}


def _copy_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _normalize_combat(
    raw_state: JsonDict, state_type: str, context: JsonDict
) -> JsonDict:
    battle = _copy_dict(raw_state.get("battle"))
    player = _copy_dict(battle.get("player"))
    return {
        "type": "decision",
        "decision": "combat_play",
        "room_type": state_type,
        "context": context,
        "run": _copy_dict(raw_state.get("run")),
        "round": battle.get("round"),
        "turn": battle.get("turn"),
        "is_play_phase": battle.get("is_play_phase"),
        "energy": player.get("energy", 0),
        "max_energy": player.get("max_energy", 0),
        "hand": _copy_list(player.get("hand")),
        "enemies": _copy_list(battle.get("enemies")),
        "player": player,
        "draw_pile_count": player.get("draw_pile_count", 0),
        "discard_pile_count": player.get("discard_pile_count", 0),
        "exhaust_pile_count": player.get("exhaust_pile_count", 0),
        "battle": battle,
    }


def _normalize_hand_select(raw_state: JsonDict, context: JsonDict) -> JsonDict:
    hand_select = _copy_dict(raw_state.get("hand_select"))
    battle = _copy_dict(raw_state.get("battle"))
    player = _copy_dict(battle.get("player"))
    return {
        "type": "decision",
        "decision": "hand_select",
        "context": context,
        "run": _copy_dict(raw_state.get("run")),
        "mode": hand_select.get("mode"),
        "prompt": hand_select.get("prompt"),
        "cards": _copy_list(hand_select.get("cards")),
        "selected_cards": _copy_list(hand_select.get("selected_cards")),
        "can_confirm": hand_select.get("can_confirm", False),
        "player": player,
        "battle": battle,
        "hand_select": hand_select,
    }


def _normalize_card_reward(raw_state: JsonDict, context: JsonDict) -> JsonDict:
    reward = _copy_dict(raw_state.get("card_reward"))
    return {
        "type": "decision",
        "decision": "card_reward",
        "context": context,
        "run": _copy_dict(raw_state.get("run")),
        "cards": _copy_list(reward.get("cards")),
        "can_skip": reward.get("can_skip", False),
        "player": _copy_dict(reward.get("player")),
        "card_reward": reward,
    }


def _normalize_combat_rewards(raw_state: JsonDict, context: JsonDict) -> JsonDict:
    rewards = _copy_dict(raw_state.get("rewards"))
    return {
        "type": "decision",
        "decision": "combat_rewards",
        "context": context,
        "run": _copy_dict(raw_state.get("run")),
        "items": _copy_list(rewards.get("items")),
        "can_proceed": rewards.get("can_proceed", False),
        "player": _copy_dict(rewards.get("player")),
        "rewards": rewards,
    }


def _normalize_map(raw_state: JsonDict, context: JsonDict) -> JsonDict:
    map_state = _copy_dict(raw_state.get("map"))
    return {
        "type": "decision",
        "decision": "map_select",
        "context": context,
        "run": _copy_dict(raw_state.get("run")),
        "choices": _copy_list(map_state.get("next_options")),
        "player": _copy_dict(map_state.get("player")),
        "current_position": _copy_dict(map_state.get("current_position")),
        "visited": _copy_list(map_state.get("visited")),
        "nodes": _copy_list(map_state.get("nodes")),
        "boss": _copy_dict(map_state.get("boss")),
        "map": map_state,
    }


def _normalize_event(raw_state: JsonDict, context: JsonDict) -> JsonDict:
    event = _copy_dict(raw_state.get("event"))
    return {
        "type": "decision",
        "decision": "event_choice",
        "context": context,
        "run": _copy_dict(raw_state.get("run")),
        "event_name": event.get("event_name"),
        "event_id": event.get("event_id"),
        "description": event.get("body"),
        "options": _copy_list(event.get("options")),
        "player": _copy_dict(event.get("player")),
        "in_dialogue": event.get("in_dialogue", False),
        "is_ancient": event.get("is_ancient", False),
        "event": event,
    }


def _normalize_rest_site(raw_state: JsonDict, context: JsonDict) -> JsonDict:
    rest = _copy_dict(raw_state.get("rest_site"))
    return {
        "type": "decision",
        "decision": "rest_site",
        "context": context,
        "run": _copy_dict(raw_state.get("run")),
        "options": _copy_list(rest.get("options")),
        "player": _copy_dict(rest.get("player")),
        "can_proceed": rest.get("can_proceed", False),
        "rest_site": rest,
    }


def _normalize_shop(raw_state: JsonDict, context: JsonDict) -> JsonDict:
    shop = _copy_dict(raw_state.get("shop"))
    items = _copy_list(shop.get("items"))
    return {
        "type": "decision",
        "decision": "shop",
        "context": context,
        "run": _copy_dict(raw_state.get("run")),
        "items": items,
        "cards": [item for item in items if item.get("category") == "card"],
        "relics": [item for item in items if item.get("category") == "relic"],
        "potions": [item for item in items if item.get("category") == "potion"],
        "card_removal": next(
            (item for item in items if item.get("category") == "card_removal"), None
        ),
        "player": _copy_dict(shop.get("player")),
        "can_proceed": shop.get("can_proceed", False),
        "shop": shop,
    }


def _normalize_card_select(raw_state: JsonDict, context: JsonDict) -> JsonDict:
    card_select = _copy_dict(raw_state.get("card_select"))
    return {
        "type": "decision",
        "decision": "card_select",
        "context": context,
        "run": _copy_dict(raw_state.get("run")),
        "screen_type": card_select.get("screen_type"),
        "prompt": card_select.get("prompt"),
        "cards": _copy_list(card_select.get("cards")),
        "player": _copy_dict(card_select.get("player")),
        "preview_showing": card_select.get("preview_showing", False),
        "can_skip": card_select.get("can_skip", False),
        "can_confirm": card_select.get("can_confirm", False),
        "can_cancel": card_select.get("can_cancel", False),
        "card_select": card_select,
    }
