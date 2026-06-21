# ruff: noqa: F403, F405, E501
from .native_api_base import *  # noqa: F403
from .native_api_c0 import NativeAPIBackendMixin0  # noqa: F401
from .native_api_c1 import NativeAPIBackendMixin1  # noqa: F401


class NativeAPIBackend(NativeAPIBackendMixin0, NativeAPIBackendMixin1, Backend):
    pass
