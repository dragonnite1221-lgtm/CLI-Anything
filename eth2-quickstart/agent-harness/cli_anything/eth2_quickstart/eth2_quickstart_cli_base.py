# ruff: noqa: E501
"""cli-anything-eth2-quickstart CLI."""

from __future__ import annotations

import json
import shlex
from typing import NoReturn

import click

from cli_anything.eth2_quickstart import __version__
from cli_anything.eth2_quickstart.core.commands import (
    VALID_CONSENSUS_CLIENTS,
    VALID_EXECUTION_CLIENTS,
    VALID_MEV_OPTIONS,
    VALID_NETWORKS,
)
from cli_anything.eth2_quickstart.core.install import install_clients, setup_node
from cli_anything.eth2_quickstart.core.rpc import start_rpc
from cli_anything.eth2_quickstart.core.status import health_check, status
from cli_anything.eth2_quickstart.core.validator import configure_validator
from cli_anything.eth2_quickstart.utils.eth2qs_backend import Eth2QuickStartBackend

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}
NETWORK_CHOICES = click.Choice(sorted(VALID_NETWORKS))
EXECUTION_CLIENT_CHOICES = click.Choice(sorted(VALID_EXECUTION_CLIENTS))
CONSENSUS_CLIENT_CHOICES = click.Choice(sorted(VALID_CONSENSUS_CLIENTS))
MEV_CHOICES = click.Choice(sorted(VALID_MEV_OPTIONS))

__all__ = [
    "CONSENSUS_CLIENT_CHOICES",
    "CONTEXT_SETTINGS",
    "EXECUTION_CLIENT_CHOICES",
    "Eth2QuickStartBackend",
    "MEV_CHOICES",
    "NETWORK_CHOICES",
    "NoReturn",
    "VALID_CONSENSUS_CLIENTS",
    "VALID_EXECUTION_CLIENTS",
    "VALID_MEV_OPTIONS",
    "VALID_NETWORKS",
    "__version__",
    "annotations",
    "click",
    "configure_validator",
    "health_check",
    "install_clients",
    "json",
    "setup_node",
    "shlex",
    "start_rpc",
    "status",
]
