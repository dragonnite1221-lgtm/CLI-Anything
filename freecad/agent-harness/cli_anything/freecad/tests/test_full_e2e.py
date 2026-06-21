# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import TestFreeCADBackend  # noqa: F401,E501
from ._test_full_e2e_g0_c0 import _TestIntermediateFilesMixin0  # noqa: F401
from ._test_full_e2e_g0_c1 import _TestIntermediateFilesMixin1  # noqa: F401
from ._test_full_e2e_g0_c2 import _TestIntermediateFilesMixin2  # noqa: F401
from ._test_full_e2e_g0_c3 import _TestIntermediateFilesMixin3  # noqa: F401
from ._test_full_e2e_g1_c0 import _TestCLISubprocessMixin0  # noqa: F401
from ._test_full_e2e_g1_c1 import _TestCLISubprocessMixin1  # noqa: F401
from ._test_full_e2e_g1_c2 import _TestCLISubprocessMixin2  # noqa: F401
from ._test_full_e2e_g1_c3 import _TestCLISubprocessMixin3  # noqa: F401
from ._test_full_e2e_g1_c4 import _TestCLISubprocessMixin4  # noqa: F401
from ._test_full_e2e_g1_c5 import _TestCLISubprocessMixin5  # noqa: F401


class TestIntermediateFiles(_TestIntermediateFilesMixin0, _TestIntermediateFilesMixin1, _TestIntermediateFilesMixin2, _TestIntermediateFilesMixin3):
    pass


class TestCLISubprocess(_TestCLISubprocessMixin0, _TestCLISubprocessMixin1, _TestCLISubprocessMixin2, _TestCLISubprocessMixin3, _TestCLISubprocessMixin4, _TestCLISubprocessMixin5):
    pass
