# ruff: noqa: F403, F405, E501
from .slay_the_spire_ii_cli_base import *  # noqa: F403
from .slay_the_spire_ii_cli_p3 import main  # noqa: F401


if __name__ == "__main__":
    raise SystemExit(main())

# fmt: off
# re-export full surface
from .slay_the_spire_ii_cli_p1 import CliRuntime, _get_runtime, cli, repl, _repl_commands, _print_json, _run_json, _coerce_value, _parse_kv_pairs  # noqa: F401,E501
from .slay_the_spire_ii_cli_p2 import action, _run_post, raw_state, state, continue_game, abandon_game, return_to_main_menu, start_game, play_card, use_potion, end_turn, choose_map, claim_reward, pick_card_reward, skip_card_reward, proceed  # noqa: F401,E501
from .slay_the_spire_ii_cli_p3 import event, advance_dialogue, rest, shop_buy, select_card, confirm_selection, cancel_selection, combat_select_card, combat_confirm_selection, select_relic, skip_relic_selection, claim_treasure_relic  # noqa: F401,E501
# fmt: on
