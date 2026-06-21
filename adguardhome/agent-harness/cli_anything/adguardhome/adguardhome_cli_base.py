# ruff: noqa: E501
"""cli-anything-adguardhome - CLI harness for AdGuardHome."""

import json
import shlex
import sys
from pathlib import Path

import click

from cli_anything.adguardhome.core import blocking as blocking_core
from cli_anything.adguardhome.core import clients as clients_core
from cli_anything.adguardhome.core import dhcp as dhcp_core
from cli_anything.adguardhome.core import filtering as filtering_core
from cli_anything.adguardhome.core import log as log_core
from cli_anything.adguardhome.core import project
from cli_anything.adguardhome.core import rewrite as rewrite_core
from cli_anything.adguardhome.core import server as server_core
from cli_anything.adguardhome.core import stats as stats_core
from cli_anything.adguardhome.utils.adguardhome_backend import AdGuardHomeClient
from cli_anything.adguardhome.utils.repl_skin import ReplSkin

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

__all__ = [
    "AdGuardHomeClient",
    "CONTEXT_SETTINGS",
    "Path",
    "ReplSkin",
    "blocking_core",
    "click",
    "clients_core",
    "dhcp_core",
    "filtering_core",
    "json",
    "log_core",
    "project",
    "rewrite_core",
    "server_core",
    "shlex",
    "stats_core",
    "sys",
]
