# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import TestServerPrefix, TestSubscriberHash  # noqa: F401,E501
from ._test_core_p1 import TestMailchimpClient  # noqa: F401,E501
from ._test_core_p2 import TestOutput, TestPagination  # noqa: F401,E501
from ._test_core_c0 import _TestGeneratedCommandsImportMixin0  # noqa: F401
from ._test_core_c1 import _TestGeneratedCommandsImportMixin1  # noqa: F401
from ._test_core_c2 import _TestGeneratedCommandsImportMixin2  # noqa: F401


class TestGeneratedCommandsImport(_TestGeneratedCommandsImportMixin0, _TestGeneratedCommandsImportMixin1, _TestGeneratedCommandsImportMixin2, unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
