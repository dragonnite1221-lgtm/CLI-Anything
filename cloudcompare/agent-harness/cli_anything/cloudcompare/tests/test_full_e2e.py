# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import TestBackendAvailability, TestFormatConversion, _make_xyz_cloud, _resolve_cli, cloud_xyz, noisy_cloud_xyz, project_json, tmp_dir  # noqa: F401,E501
from ._test_full_e2e_p1 import TestSORFilter, TestSubsampling  # noqa: F401,E501
from ._test_full_e2e_p2 import TestCSFFilter  # noqa: F401,E501
from ._test_full_e2e_p3 import TestDelaunayMesh, TestNoisePCLFilter, TestNormalsOps, TestSFColorOps  # noqa: F401,E501
from ._test_full_e2e_p4 import TestApplyTransform, TestSegmentCC  # noqa: F401,E501
from ._test_full_e2e_p5 import TestExportPipeline, TestProjectWorkflow  # noqa: F401,E501
from ._test_full_e2e_c0 import _TestCLISubprocessMixin0  # noqa: F401
from ._test_full_e2e_c1 import _TestCLISubprocessMixin1  # noqa: F401
from ._test_full_e2e_c2 import _TestCLISubprocessMixin2  # noqa: F401


class TestCLISubprocess(_TestCLISubprocessMixin0, _TestCLISubprocessMixin1, _TestCLISubprocessMixin2):
    pass
