# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import TestTimecode, TestMltXml  # noqa: F401,E501
from ._test_core_p1 import TestProject  # noqa: F401,E501
from ._test_core_p2 import TestFilters  # noqa: F401,E501
from ._test_core_p3 import TestMedia  # noqa: F401,E501
from ._test_core_p4 import TestExport  # noqa: F401,E501
from ._test_core_p5 import TestIntegration  # noqa: F401,E501
from ._test_core_p6 import TestTimelineEdgeCases  # noqa: F401,E501
from ._test_core_p7 import TestCompositing  # noqa: F401,E501
from ._test_core_g0_c0 import _TestSessionMixin0  # noqa: F401
from ._test_core_g0_c1 import _TestSessionMixin1  # noqa: F401
from ._test_core_g1_c0 import _TestPreviewMixin0  # noqa: F401
from ._test_core_g1_c1 import _TestPreviewMixin1  # noqa: F401
from ._test_core_g1_c2 import _TestPreviewMixin2  # noqa: F401
from ._test_core_g2_c0 import _TestTimelineMixin0  # noqa: F401
from ._test_core_g2_c1 import _TestTimelineMixin1  # noqa: F401
from ._test_core_g2_c2 import _TestTimelineMixin2  # noqa: F401
from ._test_core_g3_c0 import _TestTransitionsMixin0  # noqa: F401
from ._test_core_g3_c1 import _TestTransitionsMixin1  # noqa: F401
from ._test_core_g3_c2 import _TestTransitionsMixin2  # noqa: F401


class TestSession(_TestSessionMixin0, _TestSessionMixin1):
    pass


class TestPreview(_TestPreviewMixin0, _TestPreviewMixin1, _TestPreviewMixin2):
    pass


class TestTimeline(_TestTimelineMixin0, _TestTimelineMixin1, _TestTimelineMixin2):
    pass


class TestTransitions(_TestTransitionsMixin0, _TestTransitionsMixin1, _TestTransitionsMixin2):
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
