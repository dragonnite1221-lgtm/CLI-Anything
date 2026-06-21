# ruff: noqa: F403, F405, E501
from .slay_the_spire_ii_cli_base import *  # noqa: F403

# fmt: off
from .slay_the_spire_ii_cli_p1 import _get_runtime, _parse_kv_pairs, _run_json, cli  # noqa: E402,E501
# fmt: on


@cli.command("action")
@click.argument("name")
@click.option("--kv", multiple=True, help="Extra payload in key=value form")
@click.pass_context
def action(ctx: click.Context, name: str, kv: tuple[str, ...]) -> None:
    """Send a raw action by name."""
    runtime = _get_runtime(ctx)
    _run_json(lambda: runtime.client.post_action(name, **_parse_kv_pairs(list(kv))))


def _run_post(client: Sts2RawClient, payload: dict[str, object]) -> None:
    action = str(payload.pop("action"))
    _run_json(lambda: client.post_action(action, **payload))


@cli.command("raw-state")
@click.pass_context
def raw_state(ctx: click.Context) -> None:
    """Print the raw bridge-plugin JSON state."""
    runtime = _get_runtime(ctx)
    _run_json(lambda: runtime.client.get_state(format="json"))


@cli.command("state")
@click.pass_context
def state(ctx: click.Context) -> None:
    """Print the normalized CLI-style state."""
    runtime = _get_runtime(ctx)
    _run_json(lambda: normalize_state(runtime.client.get_state(format="json")))


@cli.command("continue-game")
@click.pass_context
def continue_game(ctx: click.Context) -> None:
    """Continue a saved run from the main menu."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.continue_game())


@cli.command("abandon-game")
@click.pass_context
def abandon_game(ctx: click.Context) -> None:
    """Abandon the saved run from the main menu."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.abandon_game())


@cli.command("return-to-main-menu")
@click.pass_context
def return_to_main_menu(ctx: click.Context) -> None:
    """Return to the main menu from an active run."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.return_to_main_menu())


@cli.command("start-game")
@click.option("--character", default="IRONCLAD", show_default=True)
@click.option("--ascension", type=int, default=0, show_default=True)
@click.pass_context
def start_game(ctx: click.Context, character: str, ascension: int) -> None:
    """Start a new singleplayer run from the main menu."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.start_new_game(character, ascension))


@cli.command("play-card")
@click.argument("card_index", type=int)
@click.option("--target")
@click.pass_context
def play_card(ctx: click.Context, card_index: int, target: str | None) -> None:
    """Play a card by hand index."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.play_card(card_index, target=target))


@cli.command("use-potion")
@click.argument("slot", type=int)
@click.option("--target")
@click.pass_context
def use_potion(ctx: click.Context, slot: int, target: str | None) -> None:
    """Use a potion by slot index."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.use_potion(slot, target=target))


@cli.command("end-turn")
@click.pass_context
def end_turn(ctx: click.Context) -> None:
    """End turn."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.end_turn())


@cli.command("choose-map")
@click.argument("index", type=int)
@click.pass_context
def choose_map(ctx: click.Context, index: int) -> None:
    """Choose a map node by normalized index."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.choose_map_node(index))


@cli.command("claim-reward")
@click.argument("index", type=int)
@click.pass_context
def claim_reward(ctx: click.Context, index: int) -> None:
    """Claim a combat reward by index."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.claim_reward(index))


@cli.command("pick-card-reward")
@click.argument("index", type=int)
@click.pass_context
def pick_card_reward(ctx: click.Context, index: int) -> None:
    """Pick a card reward by index."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.select_card_reward(index))


@cli.command("skip-card-reward")
@click.pass_context
def skip_card_reward(ctx: click.Context) -> None:
    """Skip a card reward."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.skip_card_reward())


@cli.command("proceed")
@click.pass_context
def proceed(ctx: click.Context) -> None:
    """Proceed/leave current room when supported."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.proceed())
