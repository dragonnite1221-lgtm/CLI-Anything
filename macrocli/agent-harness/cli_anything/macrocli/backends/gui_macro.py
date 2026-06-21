# ruff: noqa: F403, F405, E501
from .gui_macro_base import *  # noqa: F403
from .gui_macro_c0 import GUIMacroBackendMixin0  # noqa: F401
from .gui_macro_c1 import GUIMacroBackendMixin1  # noqa: F401


class GUIMacroBackend(GUIMacroBackendMixin0, GUIMacroBackendMixin1, Backend):
    pass
