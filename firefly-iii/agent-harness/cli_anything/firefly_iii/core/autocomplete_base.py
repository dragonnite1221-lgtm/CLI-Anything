# ruff: noqa: E501
r"""
Autocomplete command group

Provides quick autocomplete suggestions for various Firefly III entities.
"""

import click
from ..firefly_iii_cli import get_backend, output

__all__ = ["click", "get_backend", "output"]
