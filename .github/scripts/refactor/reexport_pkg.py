#!/usr/bin/env python3
"""Make a package façade entrypoint re-export every name defined in its split
parts via relative imports, so `from pkg.x import Name` keeps working.

Usage: python3 /tmp/reexport_pkg.py <entrypoint.py>
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path


def toplevel_defs(path: Path) -> list[str]:
    t = ast.parse(path.read_text())
    out = []
    for n in t.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.append(n.name)
        elif isinstance(n, ast.Assign):
            for tg in n.targets:
                if isinstance(tg, ast.Name):
                    out.append(tg.id)
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            out.append(n.target.id)
    return out


def entry_bound(path: Path) -> set[str]:
    t = ast.parse(path.read_text())
    out = set()
    for n in t.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(n.name)
        elif isinstance(n, ast.ImportFrom):
            for a in n.names:
                if a.name != "*":
                    out.add(a.asname or a.name)
        elif isinstance(n, ast.Import):
            for a in n.names:
                out.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, ast.Assign):
            for tg in n.targets:
                if isinstance(tg, ast.Name):
                    out.add(tg.id)
    return out


def main() -> int:
    entry = Path(sys.argv[1])
    stem = entry.stem
    parts = sorted(entry.parent.glob(f"{stem}_p*.py"))
    bound = entry_bound(entry)
    blocks = []
    for p in parts:
        names = [n for n in toplevel_defs(p) if n not in bound]
        if not names:
            continue
        bound.update(names)
        blocks.append(f"from .{p.stem} import {', '.join(names)}  # noqa: F401,E501")
    if not blocks:
        print("nothing to re-export")
        return 0
    text = "\n# fmt: off\n# re-export full surface\n" + "\n".join(blocks) + "\n# fmt: on\n"
    with entry.open("a") as fh:
        fh.write(text)
    print(f"re-exported {sum(len(b.split('import')[1].split(',')) for b in blocks)} names")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
