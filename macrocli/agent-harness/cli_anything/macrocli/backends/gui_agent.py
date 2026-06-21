# ruff: noqa: F403, F405, E501
from .gui_agent_base import *  # noqa: F403
from .gui_agent_c0 import GUIAgentBackendMixin0  # noqa: F401
from .gui_agent_c1 import GUIAgentBackendMixin1  # noqa: F401
from .gui_agent_c2 import GUIAgentBackendMixin2  # noqa: F401


class GUIAgentBackend(GUIAgentBackendMixin0, GUIAgentBackendMixin1, GUIAgentBackendMixin2, Backend):
    pass
