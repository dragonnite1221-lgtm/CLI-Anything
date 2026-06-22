#!/usr/bin/env python3
"""Package-aware topological splitter for the 200-line gate.

For a package submodule <stem>.py it produces sibling submodules:
  <stem>_base.py : docstring + imports (incl. relative `from ..x import y`) +
                   leading constants, with __all__ exporting every name.
  <stem>_pN.py   : groups of funcs/classes; each does `from .<stem>_base import *`
                   plus topological cross-imports `from .<stem>_pK import ...`.
  <stem>.py      : façade entrypoint re-exporting the full surface + guard.

Uses RELATIVE imports (leading dot) and no sys.path bootstrap. Post-first-def
imports are hoisted into base.

Usage: python3 /tmp/split_pkg.py <file.py> [max_body=150]
"""
from __future__ import annotations

import ast
import sys
from collections import defaultdict
from pathlib import Path


def is_def(n):
    return isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))


def node_start(n):
    if getattr(n, "decorator_list", None):
        return min(d.lineno for d in n.decorator_list)
    return n.lineno


def bound_names(n):
    out = set()
    if is_def(n):
        out.add(n.name)
    elif isinstance(n, ast.Assign):
        for t in n.targets:
            for s in ast.walk(t):
                if isinstance(s, ast.Name):
                    out.add(s.id)
    elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
        out.add(n.target.id)
    elif isinstance(n, ast.ImportFrom):
        for a in n.names:
            if a.name != "*":
                out.add(a.asname or a.name)
    elif isinstance(n, ast.Import):
        for a in n.names:
            out.add((a.asname or a.name).split(".")[0])
    return out


def refs(n):
    return {s.id for s in ast.walk(n) if isinstance(s, ast.Name)}


def main():
    path = Path(sys.argv[1])
    max_body = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    src = path.read_text()
    lines = src.splitlines(keepends=True)
    body = ast.parse(src).body
    # Header = leading imports + module docstring only. Leading constants become
    # distributable items so they don't bloat _base.
    def _is_header(n):
        return isinstance(n, (ast.Import, ast.ImportFrom)) or (
            isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
        )

    first = 0
    while first < len(body) and _is_header(body[first]):
        first += 1
    if first >= len(body):
        print("no splittable content")
        return 1

    header = "".join(lines[: node_start(body[first]) - 1]).rstrip() + "\n"
    base_names = set()
    for n in body[:first]:
        for sub in ast.walk(n):
            base_names |= bound_names(sub)

    items, guard, hoist = [], "", ""
    for n in body[first:]:
        s, e = node_start(n), n.end_lineno
        text = "".join(lines[s - 1 : e])
        if isinstance(n, ast.If) and "__main__" in ast.dump(n.test):
            guard = text
            continue
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            hoist += text.rstrip() + "\n"
            base_names |= bound_names(n)
            continue
        items.append({"t": text.rstrip() + "\n", "d": bound_names(n), "r": refs(n),
                      "n": e - s + 1, "main": is_def(n) and getattr(n, "name", "") == "main"})

    owner = {}
    for i, it in enumerate(items):
        for nm in it["d"]:
            owner[nm] = i
    deps = defaultdict(set)
    for i, it in enumerate(items):
        for nm in it["r"]:
            j = owner.get(nm)
            if j is not None and j != i:
                deps[i].add(j)

    idx, low, on, st, sccs, c = {}, {}, {}, [], [], [0]

    def sc(v):
        idx[v] = low[v] = c[0]; c[0] += 1; st.append(v); on[v] = True
        for w in deps[v]:
            if w not in idx:
                sc(w); low[v] = min(low[v], low[w])
            elif on.get(w):
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = st.pop(); on[w] = False; comp.append(w)
                if w == v:
                    break
            sccs.append(comp)

    sys.setrecursionlimit(10000)
    for v in range(len(items)):
        if v not in idx:
            sc(v)
    ordered = [i for comp in sccs for i in sorted(comp)]
    mi = next((i for i, it in enumerate(items) if it["main"]), None)
    if mi is not None:
        ordered = [i for i in ordered if i != mi] + [mi]

    mods, cur, cl = [], [], 0
    for i in ordered:
        if cur and cl + items[i]["n"] > max_body:
            mods.append(cur); cur = []; cl = 0
        cur.append(i); cl += items[i]["n"]
    if cur:
        mods.append(cur)
    if len(mods) == 1:
        print("fits in one module")
        return 1

    stem = path.stem
    nmods = len(mods)
    all_list = ", ".join(repr(x) for x in sorted(base_names))
    base_body = header.rstrip() + ("\n" + hoist.rstrip() if hoist else "")
    (path.with_name(stem + "_base.py")).write_text("# ruff: noqa: E501\n" + base_body + f"\n\n__all__ = [{all_list}]\n")

    names = [f"{stem}_p{k + 1}" for k in range(nmods)]
    nm2mod = {}
    for k, mod in enumerate(mods):
        for i in mod:
            for nm in items[i]["d"]:
                nm2mod[nm] = k

    for k, mod in enumerate(mods):
        need = defaultdict(set)
        for i in mod:
            for nm in items[i]["r"]:
                sm = nm2mod.get(nm)
                if sm is not None and sm != k:
                    need[sm].add(nm)
        cross = ""
        if need:
            cross = "# fmt: off\n"
            for sm in sorted(need):
                cross += f"from .{names[sm]} import {', '.join(sorted(need[sm]))}  # noqa: E402,E501\n"
            cross += "# fmt: on\n"
        bodytext = "\n".join(items[i]["t"].rstrip() for i in mod) + "\n"
        content = f"# ruff: noqa: F403, F405, E501\nfrom .{stem}_base import *  # noqa: F403\n{cross}\n\n{bodytext}"
        (path.with_name(names[k] + ".py")).write_text(content)

    facade = f"# ruff: noqa: F403, F405, E501\nfrom .{stem}_base import *  # noqa: F403\n"
    if mi is not None:
        facade += f"from .{names[nm2mod['main']]} import main  # noqa: F401\n"
    if guard:
        facade += "\n\n" + guard.rstrip() + "\n"
    path.write_text(facade)
    print(f"wrote base + {nmods} parts + facade for {stem}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
