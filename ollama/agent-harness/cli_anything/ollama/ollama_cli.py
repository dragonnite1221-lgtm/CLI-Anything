# ruff: noqa: F403, F405, E501
from .ollama_cli_base import *  # noqa: F403
from .ollama_cli_p5 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .ollama_cli_p1 import _print_dict, _print_list, output, handle_error, cli  # noqa: F401,E501
from .ollama_cli_p2 import repl, model, _format_size, model_list, model_show  # noqa: F401,E501
from .ollama_cli_p3 import model_pull, model_rm, model_copy, model_ps, generate, generate_text  # noqa: F401,E501
from .ollama_cli_p4 import generate_chat, embed, embed_text, server, server_status, server_version  # noqa: F401,E501
from .ollama_cli_p5 import session, session_status, session_history  # noqa: F401,E501
# fmt: on
