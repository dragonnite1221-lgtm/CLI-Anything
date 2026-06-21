# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import TestOutputAndErrors  # noqa: F401,E501
from ._test_core_p1 import TestBackendDiscovery  # noqa: F401,E501
from ._test_core_p2 import TestHelpParsing, TestCLIHelp  # noqa: F401,E501
from ._test_core_p3 import TestCLISubprocess  # noqa: F401,E501
from ._test_core_g0_c0 import _TestCommandBuildersMixin0  # noqa: F401
from ._test_core_g0_c1 import _TestCommandBuildersMixin1  # noqa: F401
from ._test_core_g1_c0 import _TestCoreModulesMixin0  # noqa: F401
from ._test_core_g1_c1 import _TestCoreModulesMixin1  # noqa: F401
from ._test_core_g1_c2 import _TestCoreModulesMixin2  # noqa: F401
from ._test_core_g1_c3 import _TestCoreModulesMixin3  # noqa: F401
from ._test_core_g1_c4 import _TestCoreModulesMixin4  # noqa: F401
from ._test_core_g1_c5 import _TestCoreModulesMixin5  # noqa: F401
from ._test_core_g1_c6 import _TestCoreModulesMixin6  # noqa: F401


class TestCommandBuilders(_TestCommandBuildersMixin0, _TestCommandBuildersMixin1):
    pass


class TestCoreModules(_TestCoreModulesMixin0, _TestCoreModulesMixin1, _TestCoreModulesMixin2, _TestCoreModulesMixin3, _TestCoreModulesMixin4, _TestCoreModulesMixin5, _TestCoreModulesMixin6):
    pass
