# ruff: noqa: F403, F405, E501
from .prompt_base import *  # noqa: F403


async def wait_for_command_end(
    connection,
    session_id: str,
    timeout: float = 30.0,
) -> Dict:
    """Wait for the current command to finish executing.

    Monitors for a COMMAND_END event. When a COMMAND_END fires, the
    associated value is the integer exit status of the completed command.

    Args:
        session_id: The iTerm2 session ID to monitor.
        timeout: Maximum seconds to wait. Default 30.

    Returns:
        Dict with 'exit_status' (int or None) and 'timed_out' (bool).
    """
    import iterm2

    result: Dict = {
        "session_id": session_id,
        "timed_out": False,
        "exit_status": None,
    }

    async def _wait(conn):
        async with iterm2.PromptMonitor(
            conn,
            session_id,
            modes=[iterm2.PromptMonitor.Mode.COMMAND_END],
        ) as mon:
            mode, value = await mon.async_get()
            result["mode"] = mode.name if mode is not None else None
            result["exit_status"] = value  # int exit code for COMMAND_END

    try:
        await asyncio.wait_for(_wait(connection), timeout=timeout)
    except asyncio.TimeoutError:
        result["timed_out"] = True

    return result


async def watch_prompt(
    connection,
    session_id: str,
    count: int = 1,
) -> Dict:
    """Watch for N prompt events and return them.

    Collects up to `count` events of any prompt type (PROMPT, COMMAND_START,
    COMMAND_END) and returns them. Useful for monitoring a full command
    lifecycle: COMMAND_START fires when the user hits Enter, COMMAND_END fires
    when the command exits, and PROMPT fires when the shell re-displays its
    prompt.

    Args:
        session_id: The iTerm2 session ID to monitor.
        count: Number of events to collect before returning. Default 1.

    Returns:
        Dict with 'events': list of dicts, each containing 'mode' and 'value'.
    """
    import iterm2

    events: List[Dict] = []

    async with iterm2.PromptMonitor(
        connection,
        session_id,
        modes=[
            iterm2.PromptMonitor.Mode.PROMPT,
            iterm2.PromptMonitor.Mode.COMMAND_START,
            iterm2.PromptMonitor.Mode.COMMAND_END,
        ],
    ) as mon:
        for _ in range(count):
            mode, value = await mon.async_get()
            events.append(
                {
                    "mode": mode.name if mode is not None else None,
                    "value": value,
                }
            )

    return {
        "session_id": session_id,
        "events": events,
        "event_count": len(events),
    }
