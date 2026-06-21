# ruff: noqa: F403, F405, E501
from .llm_assist_base import *  # noqa: F403

# fmt: off
from .llm_assist_p1 import _load_image_bytes, _take_screenshot, _validate_steps  # noqa: E402,E501
from .llm_assist_p2 import _step_to_yaml_step  # noqa: E402,E501
# fmt: on


def generate_macro(
    goal: str,
    macro_name: str,
    screenshot_source: str = "current",  # "current" | path to image file
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    output_path: Optional[str] = None,
) -> dict:
    """Generate a macro YAML from a user goal and screenshot using a vision model.

    Args:
        goal: Natural language description of what the macro should do.
        macro_name: Name for the generated macro.
        screenshot_source: "current" to take a fresh screenshot, or a
                           file path to use an existing image.
        api_key: API key. Falls back to MACROCLI_API_KEY env var.
        model: Model name. Falls back to MACROCLI_MODEL env var.
        base_url: Base URL for non-OpenAI providers. Falls back to
                  MACROCLI_BASE_URL env var.
        output_path: Where to write the YAML file. Defaults to
                     <macro_name>.yaml in the current directory.

    Returns:
        dict with keys: yaml_path, steps_count, warnings, raw_steps
    """
    import base64

    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai is required for LLM assist.\n  pip install openai")

    # Resolve config
    resolved_model = model or os.environ.get("MACROCLI_MODEL", "")
    key = api_key or os.environ.get("MACROCLI_API_KEY", "")
    resolved_base_url = base_url or os.environ.get("MACROCLI_BASE_URL", "")

    if not resolved_model:
        raise ValueError("Model required. Pass --model or set MACROCLI_MODEL env var.")
    if not key:
        raise ValueError(
            "API key required. Pass --api-key or set MACROCLI_API_KEY env var."
        )

    client_kwargs = {"api_key": key}
    if resolved_base_url:
        client_kwargs["base_url"] = resolved_base_url
    client = OpenAI(**client_kwargs)

    # Get screenshot
    if screenshot_source == "current":
        image_bytes = _take_screenshot()
    else:
        if not Path(screenshot_source).is_file():
            raise FileNotFoundError(f"Screenshot not found: {screenshot_source}")
        image_bytes = _load_image_bytes(screenshot_source)

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Build prompt
    user_content = [
        {
            "type": "text",
            "text": (
                f"Goal: {goal}\n\n"
                "Generate the minimal sequence of steps to achieve this goal. "
                "Output ONLY the JSON array, nothing else."
            ),
        },
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{image_b64}"},
        },
    ]

    response = client.chat.completions.create(
        model=resolved_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        max_tokens=2048,
    )
    raw_text = response.choices[0].message.content.strip()

    # Strip markdown code fences if model added them despite instructions
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        raw_text = "\n".join(
            line for line in lines if not line.startswith("```")
        ).strip()

    # Parse JSON
    try:
        raw_steps = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model returned invalid JSON: {e}\n"
            f"Raw response (first 500 chars):\n{raw_text[:500]}"
        )

    if not isinstance(raw_steps, list):
        raise ValueError(
            f"Model returned non-array JSON (expected list): {type(raw_steps)}"
        )

    # Validate
    valid_steps, warnings = _validate_steps(raw_steps)

    # Convert to YAML step dicts
    yaml_steps = [_step_to_yaml_step(s, i + 1) for i, s in enumerate(valid_steps)]

    # Build macro dict
    macro = {
        "name": macro_name,
        "version": "1.0",
        "description": goal,
        "tags": ["generated", "llm-assist"],
        "parameters": {},
        "preconditions": [],
        "steps": yaml_steps,
        "postconditions": [],
        "outputs": [],
        "agent_hints": {
            "danger_level": "moderate",
            "side_effects": ["gui_interaction"],
            "reversible": False,
            "generated_by": "llm-assist",
            "model": resolved_model,
        },
    }

    # Add note about templates that need to be captured
    templates_needed = [
        {
            "step_id": s["id"],
            "template_path": s["params"].get("template", ""),
            "description": s.get("_model_description", ""),
        }
        for s in yaml_steps
        if s.get("params", {}).get("template") and s.get("_model_description")
    ]

    if templates_needed:
        macro["_templates_to_capture"] = templates_needed

    # Write YAML
    if output_path is None:
        output_path = f"{macro_name}.yaml"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(
        yaml.dump(macro, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )

    return {
        "yaml_path": str(Path(output_path).resolve()),
        "steps_count": len(yaml_steps),
        "warnings": warnings,
        "raw_steps": raw_steps,
        "templates_to_capture": templates_needed,
    }
