# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import reset_ids, tmp_dir  # noqa: F401,E501
from ._test_full_e2e_p1 import TestSVGValidity  # noqa: F401,E501
from ._test_full_e2e_p2 import TestDocumentLifecycle  # noqa: F401,E501
from ._test_full_e2e_p3 import TestExport  # noqa: F401,E501
from ._test_full_e2e_p4 import TestCLISubprocess, _resolve_cli  # noqa: F401,E501
from ._test_full_e2e_p5 import TestInkscapeBackend, TestInkscapeExportE2E  # noqa: F401,E501
from ._test_full_e2e_c0 import _TestWorkflowsMixin0  # noqa: F401
from ._test_full_e2e_c1 import _TestWorkflowsMixin1  # noqa: F401
from ._test_full_e2e_c2 import _TestWorkflowsMixin2  # noqa: F401


class TestWorkflows(_TestWorkflowsMixin0, _TestWorkflowsMixin1, _TestWorkflowsMixin2):
    pass
