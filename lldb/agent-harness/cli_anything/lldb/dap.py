# ruff: noqa: F403, F405, E501
from .dap_base import *  # noqa: F403
from .dap_c0 import LLDBDebugAdapterMixin0  # noqa: F401
from .dap_c1 import LLDBDebugAdapterMixin1  # noqa: F401
from .dap_c2 import LLDBDebugAdapterMixin2  # noqa: F401
from .dap_c3 import LLDBDebugAdapterMixin3  # noqa: F401
from .dap_c4 import LLDBDebugAdapterMixin4  # noqa: F401
from .dap_c5 import LLDBDebugAdapterMixin5  # noqa: F401
from .dap_c6 import LLDBDebugAdapterMixin6  # noqa: F401
from .dap_c7 import LLDBDebugAdapterMixin7  # noqa: F401


class LLDBDebugAdapter(
    LLDBDebugAdapterMixin0,
    LLDBDebugAdapterMixin1,
    LLDBDebugAdapterMixin2,
    LLDBDebugAdapterMixin3,
    LLDBDebugAdapterMixin4,
    LLDBDebugAdapterMixin5,
    LLDBDebugAdapterMixin6,
    LLDBDebugAdapterMixin7,
):
    pass


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
