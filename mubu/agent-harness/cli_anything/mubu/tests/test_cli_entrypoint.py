# ruff: noqa: F403, F405, E501
from ._test_cli_entrypoint_base import *  # noqa: F403
from ._test_cli_entrypoint_p0 import detect_daily_folder_ref, resolve_cli  # noqa: F401,E501
from ._test_cli_entrypoint_c0 import _CliEntrypointTestsMixin0  # noqa: F401
from ._test_cli_entrypoint_c1 import _CliEntrypointTestsMixin1  # noqa: F401


class CliEntrypointTests(_CliEntrypointTestsMixin0, _CliEntrypointTestsMixin1, unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
