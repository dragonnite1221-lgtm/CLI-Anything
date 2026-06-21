# ruff: noqa: F403, F405, E501
from .firefly_iii_backend_base import *  # noqa: F403
from .firefly_iii_backend_c0 import FireflyIIIBackendMixin0  # noqa: F401
from .firefly_iii_backend_c1 import FireflyIIIBackendMixin1  # noqa: F401
from .firefly_iii_backend_c2 import FireflyIIIBackendMixin2  # noqa: F401
from .firefly_iii_backend_c3 import FireflyIIIBackendMixin3  # noqa: F401
from .firefly_iii_backend_c4 import FireflyIIIBackendMixin4  # noqa: F401


class FireflyIIIBackend(
    FireflyIIIBackendMixin0,
    FireflyIIIBackendMixin1,
    FireflyIIIBackendMixin2,
    FireflyIIIBackendMixin3,
    FireflyIIIBackendMixin4,
):
    pass
