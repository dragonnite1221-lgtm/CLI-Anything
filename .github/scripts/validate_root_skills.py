#!/usr/bin/env python3
"""Validate that deep harness SKILL.md files are mirrored in repo-root skills/."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_sync_helpers() -> ModuleType:
    sync_script = REPO_ROOT / ".github" / "scripts" / "sync_root_skills.py"
    spec = importlib.util.spec_from_file_location("sync_root_skills", sync_script)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {sync_script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    sync = _load_sync_helpers()
    discover_sources = sync._discover_sources
    canonical_skill_id = sync._canonical_skill_id
    rewrite_name_frontmatter = sync._rewrite_name_frontmatter
    root_skills_dir = sync.ROOT_SKILLS_DIR

    errors: list[str] = []
    for source in discover_sources():
        skill_id = canonical_skill_id(source)
        target = root_skills_dir / skill_id / "SKILL.md"
        if not target.is_file():
            errors.append(
                f"Missing root skill for {source.relative_to(REPO_ROOT)}: expected {target.relative_to(REPO_ROOT)}"
            )
            continue

        source_content = source.read_text(encoding="utf-8")
        expected = rewrite_name_frontmatter(source_content, skill_id)
        actual = target.read_text(encoding="utf-8")
        if actual != expected:
            errors.append(
                f"Out-of-sync root skill for {source.relative_to(REPO_ROOT)}: {target.relative_to(REPO_ROOT)}"
            )

    if errors:
        print("Root skills validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        print(
            "Run `python3 .github/scripts/sync_root_skills.py` and commit the updated root skills.",
            file=sys.stderr,
        )
        return 1

    print("Root skills validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
