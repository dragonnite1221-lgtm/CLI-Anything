# ruff: noqa: F403, F405, E501
from ._test_cli_hub_base import *  # noqa: F403
from ._test_cli_hub_p0 import _make_preview_bundle  # noqa: F401,E501
from ._test_cli_hub_p1 import _make_preview_session  # noqa: F401,E501
from ._test_cli_hub_p2 import TestRegistry  # noqa: F401,E501
from ._test_cli_hub_p3 import TestPreviewBundle  # noqa: F401,E501
from ._test_cli_hub_p4 import TestInstaller  # noqa: F401,E501
from ._test_cli_hub_p5 import TestUvStrategy  # noqa: F401,E501
from ._test_cli_hub_p6 import TestScriptStrategy  # noqa: F401,E501
from ._test_cli_hub_p7 import TestCLI  # noqa: F401,E501
from ._test_cli_hub_c0 import _TestAnalyticsMixin0  # noqa: F401
from ._test_cli_hub_c1 import _TestAnalyticsMixin1  # noqa: F401


class TestAnalytics(_TestAnalyticsMixin0, _TestAnalyticsMixin1):
    pass
