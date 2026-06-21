# ruff: noqa: F403, F405, E501
from ._test_cli_entrypoint_base import *  # noqa: F403
from ._test_cli_entrypoint_p0 import resolve_cli, uses_module_fallback  # noqa: F401,E501
from ._test_cli_entrypoint_c0 import _CliEntrypointTestsMixin0  # noqa: F401
from ._test_cli_entrypoint_c1 import _CliEntrypointTestsMixin1  # noqa: F401
from ._test_cli_entrypoint_c2 import _CliEntrypointTestsMixin2  # noqa: F401
from ._test_cli_entrypoint_c3 import _CliEntrypointTestsMixin3  # noqa: F401
from ._test_cli_entrypoint_c4 import _CliEntrypointTestsMixin4  # noqa: F401


class CliEntrypointTests(_CliEntrypointTestsMixin0, _CliEntrypointTestsMixin1, _CliEntrypointTestsMixin2, _CliEntrypointTestsMixin3, _CliEntrypointTestsMixin4, unittest.TestCase):
    pass
