# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import choose_collection, choose_item_with_attachment, choose_item_with_note, choose_regular_item, choose_tag_name, resolve_cli, uses_module_fallback  # noqa: F401,E501
from ._test_full_e2e_c0 import _ZoteroFullE2EMixin0  # noqa: F401
from ._test_full_e2e_c1 import _ZoteroFullE2EMixin1  # noqa: F401


class ZoteroFullE2E(_ZoteroFullE2EMixin0, _ZoteroFullE2EMixin1, unittest.TestCase):
    pass
