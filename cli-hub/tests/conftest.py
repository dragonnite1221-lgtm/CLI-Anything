"""Shared pytest fixtures for the cli-hub suite.

Shell-operator installs (``curl … | bash``) now require explicit consent
(``CLI_HUB_ALLOW_SHELL_INSTALL=1`` or an interactive ``y``). The existing
install-flow tests exercise the *allowed* path, so grant the non-interactive
opt-in for the whole test session. Tests that assert the *refusal* path clear
this env var locally.
"""

import pytest


@pytest.fixture(autouse=True)
def _allow_shell_installs(monkeypatch):
    monkeypatch.setenv("CLI_HUB_ALLOW_SHELL_INSTALL", "1")
