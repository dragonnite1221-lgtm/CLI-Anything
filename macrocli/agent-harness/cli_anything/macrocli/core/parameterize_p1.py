# ruff: noqa: F403, F405, E501
from .parameterize_base import *  # noqa: F403


def _valid_param_name(name: str) -> bool:
    return bool(_PARAM_NAME_RE.match(name))


def _prompt_param_name(prompt: str) -> Optional[str]:
    """Prompt user for a parameter name. Return None if skipped (empty input)."""
    while True:
        try:
            raw = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

        if not raw:
            return None  # skip

        if _valid_param_name(raw):
            return raw

        print(
            f"  ✗ '{raw}' is not valid. Use lowercase letters, digits, "
            f"underscores only (must start with a letter). "
            f"Press Enter to skip."
        )


def interactive_parameterize(
    type_steps: list[tuple[int, object]],
    existing_params: Optional[set[str]] = None,
) -> dict[int, str]:
    """Interactively ask the user which type_text steps to parameterize.

    Args:
        type_steps: List of (list_index, RecordedStep) from recorder.get_type_steps().
        existing_params: Already-used parameter names (to avoid duplicates).

    Returns:
        {list_index: param_name} — only for steps the user chose to parameterize.
    """
    if not type_steps:
        print("  No type_text steps found to parameterize.")
        return {}

    used_names: set[str] = set(existing_params or [])
    assignments: dict[int, str] = {}

    print()
    print("─" * 60)
    print("  Parameterization — press Enter to keep a value hardcoded,")
    print("  or type a parameter name (e.g. output_path) to make it dynamic.")
    print("─" * 60)

    for n, (idx, step) in enumerate(type_steps, 1):
        value = step.text  # type: ignore[attr-defined]
        # Truncate long values for display
        display = value if len(value) <= 50 else value[:47] + "..."

        print(f"\n  [{n}/{len(type_steps)}] step typed: {display!r}")

        while True:
            name = _prompt_param_name("  → Parameter name (Enter to skip): ")
            if name is None:
                break  # skip
            if name in used_names:
                print(f"  ✗ '{name}' already used. Choose a different name.")
                continue
            used_names.add(name)
            assignments[idx] = name
            print(f"  ✓ Will become: ${{{{name}}}}")
            break

    print()
    if assignments:
        print(
            f"  Parameterized {len(assignments)} step(s): "
            f"{', '.join(assignments.values())}"
        )
    else:
        print("  No steps parameterized — macro will use hardcoded values.")
    print("─" * 60)

    return assignments


class _YamlTypeStep:
    """Lightweight wrapper for a type_text step found inside a YAML dict."""

    def __init__(self, step_idx: int, step_dict: dict):
        self.list_index = step_idx
        self._step = step_dict
        self.text: str = step_dict["params"]["text"]

    def apply(self, param_name: str) -> None:
        self._step["params"]["text"] = f"${{{param_name}}}"
