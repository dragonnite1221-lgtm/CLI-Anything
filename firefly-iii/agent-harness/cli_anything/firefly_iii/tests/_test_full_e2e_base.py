# ruff: noqa: F403, F405, E501
r"""
End-to-end tests

Test interaction with real Firefly III instance
"""
import pytest
import os
import subprocess
import json


skip_e2e = pytest.mark.skipif(
    not os.environ.get('FIREFLY_III_BASE_URL') or not os.environ.get('FIREFLY_III_PAT'),
    reason="Requires FIREFLY_III_BASE_URL and FIREFLY_III_PAT environment variables"
)


# fmt: off
__all__ = ['json', 'os', 'pytest', 'skip_e2e', 'subprocess']  # noqa: E501
# fmt: on
