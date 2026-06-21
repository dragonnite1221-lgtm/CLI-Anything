# ruff: noqa: F403, F405, E501
from .parameterize_base import *  # noqa: F403

# fmt: off
from .parameterize_p1 import _valid_param_name  # noqa: E402,E501
# fmt: on


def llm_suggest_parameters(
    type_steps: list[tuple[int, object]],
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
) -> dict[int, str]:
    """Use a vision model to suggest which type_text steps should be parameterized
    and what to name the parameters.

    Args:
        type_steps: Same format as interactive_parameterize input.
        api_key: API key. Falls back to MACROCLI_API_KEY env var.
        model: Model name. Falls back to MACROCLI_MODEL env var.
        base_url: Base URL for non-OpenAI providers. Falls back to
                  MACROCLI_BASE_URL env var.

    Returns:
        {list_index: suggested_param_name} — same shape as interactive output.
        The caller can pass this directly to recorder.apply_parameterization()
        or show it to the user for confirmation first.
    """
    import json
    import os

    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "openai required for auto-parameterization.\n  pip install openai"
        )

    resolved_model = model or os.environ.get("MACROCLI_MODEL", "")
    key = api_key or os.environ.get("MACROCLI_API_KEY", "")
    resolved_base_url = base_url or os.environ.get("MACROCLI_BASE_URL", "")

    if not resolved_model:
        raise ValueError("Model required. Set MACROCLI_MODEL env var or pass --model.")
    if not key:
        raise ValueError("API key required. Pass --api-key or set MACROCLI_API_KEY.")

    client_kwargs = {"api_key": key}
    if resolved_base_url:
        client_kwargs["base_url"] = resolved_base_url
    client = OpenAI(**client_kwargs)

    _SYSTEM = """\
You are a macro parameterization assistant. Given a list of text values
that a user typed during a GUI recording session, decide which ones should
become CLI parameters (so the macro can be reused with different values)
and suggest a snake_case parameter name for each.

Rules:
- File paths, URLs, usernames, numeric sizes/counts → ALWAYS parameterize
- Generic user content (e.g. document body text) → parameterize if variable
- Fixed UI inputs that never change (e.g. "OK", "yes", "1") → do NOT parameterize
- Parameter names: lowercase, snake_case, descriptive (e.g. output_path, width)

Output ONLY a JSON object mapping the step index (as a string) to the
parameter name, for steps that SHOULD be parameterized.
Steps that should NOT be parameterized must be omitted entirely.
Example: {"0": "output_path", "2": "export_width"}
"""

    items = "\n".join(
        f"  index {idx}: {step.text!r}"  # type: ignore[attr-defined]
        for idx, step in type_steps
    )
    prompt = f"Typed values from the recording:\n{items}\n\nOutput JSON only."

    response = client.chat.completions.create(
        model=resolved_model,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1024,
    )
    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = "\n".join(
            line for line in raw.split("\n") if not line.startswith("```")
        ).strip()

    try:
        raw_dict: dict = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model returned invalid JSON: {e}\nRaw: {raw[:300]}")

    # Convert string keys to int, validate names
    result: dict[int, str] = {}
    for k, v in raw_dict.items():
        try:
            idx = int(k)
        except ValueError:
            continue
        if not isinstance(v, str) or not _valid_param_name(v):
            continue
        # Check the index is actually in the provided steps
        if any(i == idx for i, _ in type_steps):
            result[idx] = v

    return result
