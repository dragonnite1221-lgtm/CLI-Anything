#!/usr/bin/env python3
"""Split a package module whose oversized node is a single big class.

The giant class C(<bases>) is split into mixin classes carrying disjoint method
subsets; the façade declares `class C(CMixin0, CMixin1, ..., <bases>): pass` so
C exposes every method via MRO. Class-level attributes/docstring go in CMixin0.
Other top-level items (imports, constants, small funcs/classes) are handled like
split_pkg: imports->_base, others distributed.

Produces _base + _pN (other items) + _cN (class mixins) + façade, relative
imports, each <=~190 body lines.

Usage: python3 /tmp/split_pkgclass.py <file.py> [max_body=150]
"""
from __future__ import annotations

import ast
from collections import defaultdict
import sys
from pathlib import Path


def span(lines, n):
    s = min([d.lineno for d in getattr(n, "decorator_list", [])], default=n.lineno)
    return "".join(lines[s - 1 : n.end_lineno])


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
    max_body = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    gthresh = int(sys.argv[3]) if len(sys.argv) > 3 else 190
    src = path.read_text()
    lines = src.splitlines(keepends=True)
    tree = ast.parse(src)
    stem = path.stem
    # For pytest test modules, sibling files and mixin classes must be invisible
    # to collection: underscore-prefix sibling module stems and mixin class names
    # so pytest (test_*.py / Test* class) skips them; only the façade is collected.
    is_test = stem.startswith("test_") or stem.endswith("_test")
    sib = ("_" + stem) if is_test else stem
    mpfx = "_" if is_test else ""

    giant = None
    for n in tree.body:
        if isinstance(n, ast.ClassDef) and (n.end_lineno - n.lineno + 1) >= gthresh:
            giant = n
            break
    if giant is None:
        print("no giant class")
        return 1

    # constants/data stay in base (mixins see them via star-import); standalone
    # funcs/classes are distributed into _pN parts to keep base small.
    header_parts, const_others, func_others, guard = [], [], [], None
    base_names = set()
    for n in tree.body:
        if n is giant:
            continue
        if isinstance(n, ast.If) and "__main__" in ast.dump(n.test):
            guard = n
        elif isinstance(n, (ast.Import, ast.ImportFrom)) or (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)):
            header_parts.append(span(lines, n))
            base_names |= names_of(n)
        elif isinstance(n, (ast.Assign, ast.AnnAssign)):
            const_others.append(n)
            base_names |= names_of(n)
        else:
            func_others.append(n)

    # base module: header imports + module-level constants verbatim
    base_src = "# ruff: noqa: F403, F405, E501\n" + "".join(header_parts).rstrip() + "\n"
    for n in const_others:
        base_src += "\n\n" + span(lines, n).rstrip() + "\n"
    base_src += "\n\n# fmt: off\n__all__ = [" + ", ".join(repr(x) for x in sorted(base_names)) + "]  # noqa: E501\n# fmt: on\n"
    (path.with_name(sib + "_base.py")).write_text(base_src)

    def refs(n):
        return {s.id for s in ast.walk(n) if isinstance(s, ast.Name)}

    # distribute standalone funcs/classes into _pN parts (each star-imports base)
    part_chunks, pl = [[]], 0
    for n in func_others:
        nl = n.end_lineno - n.lineno + 1
        if part_chunks[-1] and pl + nl > max_body:
            part_chunks.append([]); pl = 0
        part_chunks[-1].append(n); pl += nl
    part_chunks = [c for c in part_chunks if c]
    # name -> owning part index, for cross-imports
    name2part = {}
    for pi, ch in enumerate(part_chunks):
        for n in ch:
            for nm in names_of(n):
                name2part[nm] = pi

    def cross_imports(nodes, self_pi=None):
        used = set().union(*[refs(n) for n in nodes]) if nodes else set()
        need = defaultdict(set)
        for nm in used:
            pj = name2part.get(nm)
            if pj is not None and pj != self_pi:
                need[pj].add(nm)
        return "".join(
            f"from .{sib}_p{pj} import {', '.join(sorted(need[pj]))}  # noqa: F401,E501\n"
            for pj in sorted(need)
        )

    part_exports = []
    for pi, ch in enumerate(part_chunks):
        body = "".join("\n\n" + span(lines, n).rstrip() + "\n" for n in ch)
        ci_txt = cross_imports(ch, self_pi=pi)
        content = ("# ruff: noqa: F403, F405, E501\n"
                   f"from .{sib}_base import *  # noqa: F403\n" + ci_txt + body)
        (path.with_name(f"{sib}_p{pi}.py")).write_text(content)
        part_exports.append((pi, sorted(set().union(*[names_of(n) for n in ch]))))

    # split the giant class
    cls_attrs = [m for m in giant.body if not isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
    methods = [m for m in giant.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
    chunks, cur, cl = [[]], 0, 0
    for m in methods:
        nl = m.end_lineno - m.lineno + 1
        if chunks[-1] and cl + nl > max_body:
            chunks.append([]); cl = 0
        chunks[-1].append(m); cl += nl

    mixins = []
    for ci, ch in enumerate(chunks):
        mixin = f"{mpfx}{giant.name}Mixin{ci}"
        mixins.append(mixin)
        body = ""
        if ci == 0 and cls_attrs:
            for a in cls_attrs:
                body += span(lines, a)
        for m in ch:
            body += span(lines, m)
        if not body.strip():
            body = "    pass\n"
        ci_txt = cross_imports(ch + cls_attrs if ci == 0 else ch)
        content = (
            "# ruff: noqa: F403, F405, E501\n"
            f"from .{sib}_base import *  # noqa: F403\n" + ci_txt + "\n\n"
            f"class {mixin}:\n{body}"
        )
        (path.with_name(f"{sib}_c{ci}.py")).write_text(content)

    bases = [ast.unparse(b) for b in giant.bases]
    mixin_imports = "".join(f"from .{sib}_c{ci} import {mixins[ci]}  # noqa: F401\n" for ci in range(len(mixins)))
    part_imports = "".join(
        f"from .{sib}_p{pi} import {', '.join(names)}  # noqa: F401,E501\n"
        for pi, names in part_exports if names
    )
    base_list = ", ".join(mixins + bases)
    kw = "".join(f", {ast.unparse(k)}" for k in giant.keywords)
    facade = (
        "# ruff: noqa: F403, F405, E501\n"
        f"from .{sib}_base import *  # noqa: F403\n"
        f"{part_imports}"
        f"{mixin_imports}\n\n"
        f"class {giant.name}({base_list}{kw}):\n    pass\n"
    )
    if guard is not None:
        facade += "\n\n" + span(lines, guard)
    path.write_text(facade)
    print(f"split class {giant.name} into {len(mixins)} mixins + base for {stem}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
