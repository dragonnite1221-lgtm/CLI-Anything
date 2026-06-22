#!/usr/bin/env python3
"""Split a pytest test module under the 200-line gate (underscore siblings so
pytest collects only the façade).

  _<stem>_base.py   : imports + module constants + module-level funcs/fixtures
  _<stem>_pN.py     : groups of small top-level classes (+ cross-imports)
  _<stem>_g{i}_cK.py: mixin chunks for an oversized class i
  <stem>.py         : façade — star base + import small classes + compose giants

Usage: python3 /tmp/split_testpkg.py <test_file.py> [max_body=120]
"""
from __future__ import annotations

import ast
import sys
from collections import defaultdict
from pathlib import Path

GIANT = 185  # a class this big can't fit in a <=200-line part; mixin-split it


def span(lines, n):
    s = min([d.lineno for d in getattr(n, "decorator_list", [])], default=n.lineno)
    return "".join(lines[s - 1: n.end_lineno])


def names_of(n):
    out = set()
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
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


def main():
    path = Path(sys.argv[1])
    max_body = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    src = path.read_text()
    lines = src.splitlines(keepends=True)
    tree = ast.parse(src)
    stem = path.stem
    sib = "_" + stem

    header, base_items, classes, guard = [], [], [], None
    base_names = set()
    for n in tree.body:
        if isinstance(n, ast.If) and "__main__" in ast.dump(n.test):
            guard = n
        elif isinstance(n, (ast.Import, ast.ImportFrom)) or (
            isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
        ):
            header.append(span(lines, n))
            base_names |= names_of(n)
        elif isinstance(n, ast.ClassDef):
            classes.append(n)
        else:
            base_items.append(n)
            base_names |= names_of(n)

    if not classes:
        print("no classes")
        return 1

    base_src = "# ruff: noqa: F403, F405, E501\n" + "".join(header).rstrip() + "\n"
    for n in base_items:
        base_src += "\n\n" + span(lines, n).rstrip() + "\n"
    base_src += "\n\n# fmt: off\n__all__ = [" + ", ".join(repr(x) for x in sorted(base_names)) + "]  # noqa: E501\n# fmt: on\n"
    (path.with_name(sib + "_base.py")).write_text(base_src)

    smalls = [c for c in classes if (c.end_lineno - c.lineno + 1) <= GIANT]
    giants = [c for c in classes if (c.end_lineno - c.lineno + 1) > GIANT]

    facade_imports = ""

    # small classes -> _pN parts
    chunks, cl = [[]], 0
    for n in smalls:
        nl = n.end_lineno - n.lineno + 1
        if chunks[-1] and cl + nl > max_body:
            chunks.append([]); cl = 0
        chunks[-1].append(n); cl += nl
    chunks = [c for c in chunks if c]
    for pi, ch in enumerate(chunks):
        body = "".join("\n\n" + span(lines, n).rstrip() + "\n" for n in ch)
        content = "# ruff: noqa: F403, F405, E501\n" + f"from .{sib}_base import *  # noqa: F403\n" + body
        (path.with_name(f"{sib}_p{pi}.py")).write_text(content)
        facade_imports += f"from .{sib}_p{pi} import {', '.join(n.name for n in ch)}  # noqa: F401,E501\n"

    # giant classes -> mixin chunks; façade composes
    facade_classes = ""
    for gi, g in enumerate(giants):
        cls_attrs = [m for m in g.body if not isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
        methods = [m for m in g.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
        mchunks, ml = [[]], 0
        for m in methods:
            nl = m.end_lineno - m.lineno + 1
            if mchunks[-1] and ml + nl > max_body:
                mchunks.append([]); ml = 0
            mchunks[-1].append(m); ml += nl
        mixins = []
        for ci, ch in enumerate(mchunks):
            mixin = f"_{g.name}Mixin{ci}"
            mixins.append(mixin)
            body = ""
            if ci == 0:
                for a in cls_attrs:
                    body += span(lines, a)
            for m in ch:
                body += span(lines, m)
            if not body.strip():
                body = "    pass\n"
            content = ("# ruff: noqa: F403, F405, E501\n"
                       f"from .{sib}_base import *  # noqa: F403\n\n\n"
                       f"class {mixin}:\n{body}")
            (path.with_name(f"{sib}_g{gi}_c{ci}.py")).write_text(content)
            facade_imports += f"from .{sib}_g{gi}_c{ci} import {mixin}  # noqa: F401\n"
        bases = [ast.unparse(b) for b in g.bases]
        kw = "".join(f", {ast.unparse(k)}" for k in g.keywords)
        facade_classes += f"\n\nclass {g.name}({', '.join(mixins + bases)}{kw}):\n    pass\n"

    facade = "# ruff: noqa: F403, F405, E501\n" + f"from .{sib}_base import *  # noqa: F403\n" + facade_imports + facade_classes
    if guard is not None:
        facade += "\n\n" + span(lines, guard)
    path.write_text(facade)
    print(f"split {len(smalls)} small + {len(giants)} giant classes for {stem}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
