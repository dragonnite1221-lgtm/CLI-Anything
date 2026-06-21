# ruff: noqa: F403, F405, E501
from .slay_the_spire_ii_cli_base import *  # noqa: F403

# fmt: off
from .slay_the_spire_ii_cli_p1 import _get_runtime, cli  # noqa: E402,E501
from .slay_the_spire_ii_cli_p2 import _run_post  # noqa: E402,E501
# fmt: on


@cli.command("event")
@click.argument("index", type=int)
@click.pass_context
def event(ctx: click.Context, index: int) -> None:
    """Choose an event option by index."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.choose_event_option(index))


@cli.command("advance-dialogue")
@click.pass_context
def advance_dialogue(ctx: click.Context) -> None:
    """Advance ancient event dialogue."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.advance_dialogue())


@cli.command("rest")
@click.argument("index", type=int)
@click.pass_context
def rest(ctx: click.Context, index: int) -> None:
    """Choose a rest site option by index."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.choose_rest_option(index))


@cli.command("shop-buy")
@click.argument("index", type=int)
@click.pass_context
def shop_buy(ctx: click.Context, index: int) -> None:
    """Purchase a shop item by raw item index."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.shop_purchase(index))


@cli.command("select-card")
@click.argument("index", type=int)
@click.pass_context
def select_card(ctx: click.Context, index: int) -> None:
    """Select a card in an overlay by index."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.select_card(index))


@cli.command("confirm-selection")
@click.pass_context
def confirm_selection(ctx: click.Context) -> None:
    """Confirm the current card selection."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.confirm_selection())


@cli.command("cancel-selection")
@click.pass_context
def cancel_selection(ctx: click.Context) -> None:
    """Cancel/skip the current card selection."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.cancel_selection())


@cli.command("combat-select-card")
@click.argument("card_index", type=int)
@click.pass_context
def combat_select_card(ctx: click.Context, card_index: int) -> None:
    """Select a combat hand card during hand_select."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.combat_select_card(card_index))


@cli.command("combat-confirm-selection")
@click.pass_context
def combat_confirm_selection(ctx: click.Context) -> None:
    """Confirm an in-combat card selection."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.combat_confirm_selection())


@cli.command("select-relic")
@click.argument("index", type=int)
@click.pass_context
def select_relic(ctx: click.Context, index: int) -> None:
    """Select a relic by index."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.select_relic(index))


@cli.command("skip-relic-selection")
@click.pass_context
def skip_relic_selection(ctx: click.Context) -> None:
    """Skip relic selection."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.skip_relic_selection())


@cli.command("claim-treasure-relic")
@click.argument("index", type=int)
@click.pass_context
def claim_treasure_relic(ctx: click.Context, index: int) -> None:
    """Claim a treasure room relic by index."""
    runtime = _get_runtime(ctx)
    _run_post(runtime.client, actions.claim_treasure_relic(index))


def main(argv: list[str] | None = None) -> int:
    try:
        cli.main(args=argv, prog_name="cli-anything-sts2", standalone_mode=False)
        return 0
    except click.ClickException as exc:
        exc.show(file=sys.stderr)
        return exc.exit_code
    except click.exceptions.Exit as exc:
        return exc.exit_code
    except click.Abort:
        click.echo("Aborted!", err=True)
        return 1
