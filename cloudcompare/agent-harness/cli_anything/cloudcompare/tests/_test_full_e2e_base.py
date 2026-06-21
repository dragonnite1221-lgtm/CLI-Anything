# ruff: noqa: F403, F405, E501
"""E2E tests for cli-anything-cloudcompare.

These tests invoke the REAL CloudCompare binary (Flatpak or native).
CloudCompare MUST be installed — tests will fail, not skip, if absent.

Run with:
    python3 -m pytest cli_anything/cloudcompare/tests/test_full_e2e.py -v -s

Run against the installed CLI command:
    CLI_ANYTHING_FORCE_INSTALLED=1 python3 -m pytest cli_anything/cloudcompare/tests/test_full_e2e.py -v -s
"""
import json
import os
import subprocess
import sys
import tempfile
import pytest


# fmt: off
__all__ = ['json', 'os', 'pytest', 'subprocess', 'sys', 'tempfile']  # noqa: E501
# fmt: on
