# ruff: noqa: F403, F405, E501
from .novita_backend_base import *  # noqa: F403

# fmt: off
from .novita_backend_p1 import chat_completion, chat_completion_stream, format_message  # noqa: E402,E501
# fmt: on


def run_full_workflow(
    api_key: Optional[str] = None,
    model: str = "deepseek/deepseek-v3.2",
    prompt: str = "",
    system_message: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    on_chunk=None,
) -> dict:
    messages = []
    if system_message:
        messages.append(format_message("system", system_message))
    messages.append(format_message("user", prompt))
    if on_chunk:
        response = chat_completion_stream(
            api_key=api_key,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            on_chunk=on_chunk,
        )
        return {"content": response}
    else:
        result = chat_completion(
            api_key=api_key,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choices = result.get("choices", [])
        if choices:
            return {
                "content": choices[0].get("message", {}).get("content", ""),
                "prompt_tokens": result.get("usage", {}).get("prompt_tokens", 0),
                "completion_tokens": result.get("usage", {}).get(
                    "completion_tokens", 0
                ),
                "total_tokens": result.get("usage", {}).get("total_tokens", 0),
            }
        return {"content": ""}
