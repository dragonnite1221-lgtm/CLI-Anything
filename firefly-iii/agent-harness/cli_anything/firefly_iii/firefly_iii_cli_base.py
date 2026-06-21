# ruff: noqa: E501
#!/usr/bin/env python3
r"""
Firefly III CLI - Personal finance management via CLI-Anything

Firefly III command-line interface based on CLI-Anything spec,
converted from MCP mode to stateless CLI mode to avoid Node residual process issues.
"""

import click
import json
import os
import shlex
import sys
from typing import Dict, Any, Optional

from .utils.firefly_iii_backend import FireflyIIIBackend
from .utils.repl_skin import ReplSkin

# Global state
_json_output = False
_backend = None
_repl_skin = None
from .core.accounts import accounts
from .core.transactions import transactions
from .core.budgets import budgets
from .core.categories import categories
from .core.tags import tags
from .core.bills import bills
from .core.piggy_banks import piggy_banks
from .core.insights import insights
from .core.search import search
from .core.export import export
from .core.info import info
from .core.autocomplete import autocomplete
from .core.currencies import currencies
from .core.recurrences import recurrences
from .core.rules import rules
from .core.rule_groups import rule_groups
from .core.summary import summary
from .core.webhooks import webhooks

__all__ = [
    "Any",
    "Dict",
    "FireflyIIIBackend",
    "Optional",
    "ReplSkin",
    "_backend",
    "_json_output",
    "_repl_skin",
    "accounts",
    "autocomplete",
    "bills",
    "budgets",
    "categories",
    "click",
    "currencies",
    "export",
    "info",
    "insights",
    "json",
    "os",
    "piggy_banks",
    "recurrences",
    "rule_groups",
    "rules",
    "search",
    "shlex",
    "summary",
    "sys",
    "tags",
    "transactions",
    "webhooks",
]
