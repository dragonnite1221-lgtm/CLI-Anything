# ruff: noqa: F403, F405, E501
from .repl_skin_base import *  # noqa: F403
from .repl_skin_c0 import ReplSkinMixin0  # noqa: F401
from .repl_skin_c1 import ReplSkinMixin1  # noqa: F401
from .repl_skin_c2 import ReplSkinMixin2  # noqa: F401
from .repl_skin_c3 import ReplSkinMixin3  # noqa: F401
from .repl_skin_c4 import ReplSkinMixin4  # noqa: F401


class ReplSkin(
    ReplSkinMixin0, ReplSkinMixin1, ReplSkinMixin2, ReplSkinMixin3, ReplSkinMixin4
):
    pass
