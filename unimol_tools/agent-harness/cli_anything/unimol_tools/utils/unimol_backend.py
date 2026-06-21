# ruff: noqa: F403, F405, E501
from .unimol_backend_base import *  # noqa: F403
from .unimol_backend_c0 import UniMolBackendMixin0  # noqa: F401
from .unimol_backend_c1 import UniMolBackendMixin1  # noqa: F401
from .unimol_backend_c2 import UniMolBackendMixin2  # noqa: F401
from .unimol_backend_c3 import UniMolBackendMixin3  # noqa: F401


class UniMolBackend(
    UniMolBackendMixin0, UniMolBackendMixin1, UniMolBackendMixin2, UniMolBackendMixin3
):
    pass
