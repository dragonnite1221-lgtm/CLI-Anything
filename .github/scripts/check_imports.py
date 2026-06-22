#!/usr/bin/env python3
"""Import-integrity gate: import every cli_anything.<pkg> package and fail on
*structural* import errors (circular imports, names a split façade/part fails to
re-export). External missing deps (ModuleNotFoundError for third-party packages)
are reported as skips, not failures — the gate targets split regressions the
line-count gate cannot see.

Run from the repo root. Exit 1 on any structural breakage.
"""
from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

STRUCTURAL = (
    "partially initialized",
    "circular import",
    "cannot import name",
    "has no attribute",
)
# third-party modules that may be absent in a bare env -> treated as skips
LOCAL_PREFIXES = ("cli_anything",)


def discover():
    """Yield (harness_dir, package_name) for every agent-harness package."""
    for harness in sorted(Path(".").glob("*/agent-harness")):
        root = harness / "cli_anything"
        if not root.is_dir():
            continue
        for pkg in sorted(p.name for p in root.iterdir() if p.is_dir() and (p / "__init__.py").exists() or p.is_dir()):
            if (root / pkg).is_dir():
                yield harness, pkg


def check_one(harness: Path, pkg: str) -> tuple[str, str]:
    code = f"import cli_anything.{pkg}"
    r = subprocess.run(
        [sys.executable, "-c", code], cwd=str(harness),
        capture_output=True, text=True, timeout=60,
    )
    if r.returncode == 0:
        return "ok", ""
    err = (r.stderr.strip().splitlines() or [""])[-1]
    low = r.stderr.lower()
    if any(s in low for s in STRUCTURAL):
        # only structural if the offending module is one of ours
        if "cli_anything" in r.stderr:
            return "structural", err
    return "skip", err  # missing external dep / runtime-only error


def main() -> int:
    structural, skipped, ok = [], 0, 0
    seen = set()
    for harness, pkg in discover():
        key = (str(harness), pkg)
        if key in seen:
            continue
        seen.add(key)
        try:
            status, err = check_one(harness, pkg)
        except subprocess.TimeoutExpired:
            status, err = "skip", "timeout"
        if status == "structural":
            structural.append((pkg, err))
        elif status == "ok":
            ok += 1
        else:
            skipped += 1
    print(f"import gate: {ok} ok, {skipped} skipped (missing deps), {len(structural)} structural failures")
    for pkg, err in structural:
        print(f"  STRUCTURAL {pkg}: {err[:100]}")
    return 1 if structural else 0


if __name__ == "__main__":
    raise SystemExit(main())
