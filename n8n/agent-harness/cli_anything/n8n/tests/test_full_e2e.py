# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import TestCredentialsE2E, TestTagsE2E, TestVariablesE2E, TestWorkflowsE2E, _resolve_cli, _skip_if_no_n8n  # noqa: F401,E501
from ._test_full_e2e_c0 import _TestCLISubprocessMixin0  # noqa: F401
from ._test_full_e2e_c1 import _TestCLISubprocessMixin1  # noqa: F401


class TestCLISubprocess(_TestCLISubprocessMixin0, _TestCLISubprocessMixin1):
    pass
