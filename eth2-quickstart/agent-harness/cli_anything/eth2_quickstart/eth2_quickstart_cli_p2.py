# ruff: noqa: F403, F405, E501
from .eth2_quickstart_cli_base import *  # noqa: F403

# fmt: off
from .eth2_quickstart_cli_p1 import backend_from_context, cli, emit, handle_backend_result, require_confirm  # noqa: E402,E501
# fmt: on


@cli.command("setup-node")
@click.option(
    "--phase", type=click.Choice(["auto", "phase1", "phase2"]), default="auto"
)
@click.option("--network", type=NETWORK_CHOICES, default=None)
@click.option("--execution-client", type=EXECUTION_CLIENT_CHOICES, default=None)
@click.option("--consensus-client", type=CONSENSUS_CLIENT_CHOICES, default=None)
@click.option("--mev", type=MEV_CHOICES, default=None)
@click.option("--ethgas", is_flag=True, default=False)
@click.option("--skip-deps", is_flag=True, default=False)
@click.option(
    "--confirm", is_flag=True, default=False, help="Confirm mutating operations"
)
@click.pass_context
def setup_node_cmd(
    ctx,
    phase,
    network,
    execution_client,
    consensus_client,
    mev,
    ethgas,
    skip_deps,
    confirm,
):
    """Set up a node using phase1, phase2, or ensure-driven orchestration."""
    require_confirm(ctx, confirm)
    backend = backend_from_context(ctx)
    result = setup_node(
        backend,
        phase=phase,
        network=network,
        execution_client=execution_client,
        consensus_client=consensus_client,
        mev=mev,
        ethgas=ethgas,
        skip_deps=skip_deps,
    )
    handle_backend_result(result, ctx.obj["as_json"])


@cli.command("install-clients")
@click.option("--network", type=NETWORK_CHOICES, default=None)
@click.option("--execution-client", required=True, type=EXECUTION_CLIENT_CHOICES)
@click.option("--consensus-client", required=True, type=CONSENSUS_CLIENT_CHOICES)
@click.option("--mev", type=MEV_CHOICES, default="mev-boost")
@click.option("--ethgas", is_flag=True, default=False)
@click.option("--skip-deps", is_flag=True, default=False)
@click.option(
    "--confirm", is_flag=True, default=False, help="Confirm mutating operations"
)
@click.pass_context
def install_clients_cmd(
    ctx,
    network,
    execution_client,
    consensus_client,
    mev,
    ethgas,
    skip_deps,
    confirm,
):
    """Install execution, consensus, and MEV clients via phase2."""
    require_confirm(ctx, confirm)
    backend = backend_from_context(ctx)
    result = install_clients(
        backend,
        network=network,
        execution_client=execution_client,
        consensus_client=consensus_client,
        mev=mev,
        ethgas=ethgas,
        skip_deps=skip_deps,
    )
    handle_backend_result(result, ctx.obj["as_json"])


@cli.command("start-rpc")
@click.option("--web-stack", type=click.Choice(["nginx", "caddy"]), default="nginx")
@click.option("--server-name", default=None, help="Public hostname for RPC exposure")
@click.option("--ssl/--no-ssl", default=False)
@click.option(
    "--confirm", is_flag=True, default=False, help="Confirm mutating operations"
)
@click.pass_context
def start_rpc_cmd(ctx, web_stack, server_name, ssl, confirm):
    """Install and start RPC exposure via nginx or caddy."""
    require_confirm(ctx, confirm)
    backend = backend_from_context(ctx)
    result = start_rpc(
        backend,
        web_stack=web_stack,
        server_name=server_name,
        ssl=ssl,
    )
    handle_backend_result(result, ctx.obj["as_json"])


@cli.command("configure-validator")
@click.option("--consensus-client", required=True, type=CONSENSUS_CLIENT_CHOICES)
@click.option("--fee-recipient", default=None)
@click.option("--graffiti", default=None)
@click.option("--keys-dir", default=None)
@click.option("--secrets-dir", default=None)
@click.option("--wallet-password-file", default=None)
@click.pass_context
def configure_validator_cmd(
    ctx,
    consensus_client,
    fee_recipient,
    graffiti,
    keys_dir,
    secrets_dir,
    wallet_password_file,
):
    """Update validator metadata and return client-specific import guidance."""
    backend = backend_from_context(ctx)
    result = configure_validator(
        backend,
        consensus_client=consensus_client,
        fee_recipient=fee_recipient,
        graffiti=graffiti,
        keys_dir=keys_dir,
        secrets_dir=secrets_dir,
        wallet_password_file=wallet_password_file,
    )
    emit(result, ctx.obj["as_json"])


@cli.command("status")
@click.pass_context
def status_cmd(ctx):
    """Show aggregate node status."""
    backend = backend_from_context(ctx)
    result = status(backend)
    emit(result, ctx.obj["as_json"])


@cli.command("health-check")
@click.pass_context
def health_check_cmd(ctx):
    """Run the canonical doctor --json health check."""
    backend = backend_from_context(ctx)
    result = health_check(backend)
    emit(result, ctx.obj["as_json"])


def main():
    cli(obj={})
