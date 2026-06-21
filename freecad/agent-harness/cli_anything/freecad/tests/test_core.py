# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import TestDocument, _make_project, _make_wrapper_script  # noqa: F401,E501
from ._test_core_p1 import TestParts  # noqa: F401,E501
from ._test_core_p2 import TestSketch  # noqa: F401,E501
from ._test_core_p3 import TestBody  # noqa: F401,E501
from ._test_core_p4 import TestMaterials  # noqa: F401,E501
from ._test_core_p5 import TestSession  # noqa: F401,E501
from ._test_core_p6 import TestFreeCAD11Features  # noqa: F401,E501
from ._test_core_p7 import TestFreeCADBackend, TestMotion  # noqa: F401,E501
from ._test_core_c0 import _TestPreviewMixin0  # noqa: F401
from ._test_core_c1 import _TestPreviewMixin1  # noqa: F401
from ._test_core_c2 import _TestPreviewMixin2  # noqa: F401


class TestPreview(_TestPreviewMixin0, _TestPreviewMixin1, _TestPreviewMixin2):
    pass
