# ruff: noqa: F403, F405, E501
from .prompt_base import *  # noqa: F403


def _prompt_to_dict(prompt) -> Dict:
    """Convert an iterm2.Prompt object to a plain dict.

    Returns a dict with all available prompt fields. If the prompt is None
    (Shell Integration not installed or no prompt yet), returns a dict with
    'available': False.
    """
    if prompt is None:
        return {"available": False}

    import iterm2

    return {
        "available": True,
        "unique_id": prompt.unique_id,
        "command": prompt.command,
        "working_directory": prompt.working_directory,
        "state": prompt.state.name if prompt.state is not None else None,
        "has_prompt_range": prompt.prompt_range is not None,
        "has_command_range": prompt.command_range is not None,
        "has_output_range": prompt.output_range is not None,
    }


async def get_last_prompt(connection, session_id: str) -> Dict:
    """Get info about the last shell prompt in a session.

    Requires Shell Integration. Returns a dict with command, working_directory,
    state (PromptState name), and range availability flags. If Shell Integration
    is not installed or no prompt has been recorded yet, returns a dict with
    'available': False.

    Args:
        session_id: The iTerm2 session ID to query.

    Returns:
        Dict with prompt info, or {'available': False} if not available.
    """
    import iterm2

    prompt = await iterm2.async_get_last_prompt(connection, session_id)
    return _prompt_to_dict(prompt)


async def list_prompts(connection, session_id: str) -> Dict:
    """List all recorded prompt IDs in a session.

    Requires Shell Integration. Each ID can be used to identify individual
    command executions within the session's history.

    Args:
        session_id: The iTerm2 session ID to query.

    Returns:
        Dict with 'session_id' and 'prompt_ids' (list of strings).
    """
    import iterm2

    prompt_ids = await iterm2.async_list_prompts(connection, session_id)
    return {
        "session_id": session_id,
        "prompt_ids": list(prompt_ids) if prompt_ids else [],
        "count": len(prompt_ids) if prompt_ids else 0,
    }


async def wait_for_prompt(
    connection,
    session_id: str,
    timeout: float = 30.0,
) -> Dict:
    """Wait for the next shell prompt to appear in a session.

    Useful for waiting until a command finishes before sending the next one.
    Monitors for a PROMPT event, which fires when the shell displays its
    next prompt (i.e. the previous command has completed).

    Args:
        session_id: The iTerm2 session ID to monitor.
        timeout: Maximum seconds to wait. Default 30.

    Returns:
        Dict with 'timed_out' (bool), and prompt info if available.
    """
    import iterm2

    result: Dict = {"session_id": session_id, "timed_out": False}

    async def _wait(conn):
        async with iterm2.PromptMonitor(
            conn,
            session_id,
            modes=[iterm2.PromptMonitor.Mode.PROMPT],
        ) as mon:
            mode, value = await mon.async_get()
            result["mode"] = mode.name if mode is not None else None
            result["value"] = value

    try:
        await asyncio.wait_for(_wait(connection), timeout=timeout)
    except asyncio.TimeoutError:
        result["timed_out"] = True

    # Attempt to attach the latest prompt info after the event
    if not result["timed_out"]:
        import iterm2 as _iterm2

        prompt = await _iterm2.async_get_last_prompt(connection, session_id)
        result.update(_prompt_to_dict(prompt))

    return result
