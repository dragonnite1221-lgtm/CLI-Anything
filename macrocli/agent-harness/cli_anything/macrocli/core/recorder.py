# ruff: noqa: F403, F405, E501
from .recorder_base import *  # noqa: F403
from .recorder_c0 import MacroRecorderMixin0  # noqa: F401
from .recorder_c1 import MacroRecorderMixin1  # noqa: F401
from .recorder_c2 import MacroRecorderMixin2  # noqa: F401
from .recorder_c3 import MacroRecorderMixin3  # noqa: F401
from .recorder_c4 import MacroRecorderMixin4  # noqa: F401


class MacroRecorder(
    MacroRecorderMixin0,
    MacroRecorderMixin1,
    MacroRecorderMixin2,
    MacroRecorderMixin3,
    MacroRecorderMixin4,
):
    pass
