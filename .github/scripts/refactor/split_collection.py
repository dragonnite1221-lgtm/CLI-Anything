#!/usr/bin/env python3
"""Split a large List or Dict literal (in a return/assign, at module scope or in
a function) that makes its enclosing def/file exceed the gate. List -> helpers
returning slices, concatenated. Dict -> helpers returning sub-dicts, merged with
{**_g0(), ...}. Behavior-identical (order/keys preserved; literal keys unique).

Processes one collection per pass, re-parsing until none remain over `target`.

Usage: python3 split_collection.py <file.py> [target=185] [max_body=120]
"""
import ast
import sys
from pathlib import Path


def pick(path, target):
    src = Path(path).read_text()
    t = ast.parse(src)
    cands = []
    for node in ast.walk(t):
        if not isinstance(node, (ast.List, ast.Dict)):
            continue
        n = len(node.elts) if isinstance(node, ast.List) else len([k for k in node.keys if k is not None])
        sz = node.end_lineno - node.lineno + 1
        if n >= 4 and sz > 150:
            cands.append((t, node, sz))
    cands.sort(key=lambda c: c[2], reverse=True)
    return src, (cands[0] if cands else None)


def main():
    path = sys.argv[1]
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 185
    max_body = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    did = 0
    for _ in range(200):
        src, best = pick(path, target)
        if best is None:
            print(f"done ({did} split)"); return 0 if did else 1
        parent, node, _ = best
        lines = src.splitlines(keepends=True)

        def seg(a, b, c, d):
            if a == c:
                return lines[a - 1][b:d]
            return lines[a - 1][b:] + "".join(lines[a: c - 1]) + lines[c - 1][:d]

        is_list = isinstance(node, ast.List)
        items = node.elts if is_list else list(zip(node.keys, node.values))
        groups, cl = [[]], 0
        for it in items:
            end = it.end_lineno if is_list else it[1].end_lineno
            start = it.lineno if is_list else it[0].lineno
            ln = end - start + 1
            if groups[-1] and cl + ln > max_body:
                groups.append([]); cl = 0
            groups[-1].append(it); cl += ln
        groups = [g for g in groups if g]
        if len(groups) < 2:
            print("single group; cannot split"); return 1 if not did else 0

        pname = parent.name if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)) else "mod"
        existing = {n.name for n in ast.walk(ast.parse(src)) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        base = f"_{pname}_cg"
        k0 = 0
        while any(f"{base}{k0}_{j}" in existing for j in range(len(groups))):
            k0 += 1
        helpers, names = "", []
        for gi, g in enumerate(groups):
            hn = f"{base}{k0}_{gi}"; names.append(hn)
            if is_list:
                inner = "".join("        " + seg(e.lineno, e.col_offset, e.end_lineno, e.end_col_offset).rstrip().rstrip(",") + ",\n" for e in g)
                helpers += f"def {hn}():\n    return [\n{inner}    ]\n\n\n"
            else:
                inner = "".join("        " + seg(k.lineno, k.col_offset, v.end_lineno, v.end_col_offset).rstrip().rstrip(",") + ",\n" for k, v in g)
                helpers += f"def {hn}():\n    return {{\n{inner}    }}\n\n\n"
        if is_list:
            combo = "(" + " + ".join(f"{nm}()" for nm in names) + ")"
        else:
            combo = "{" + ", ".join(f"**{nm}()" for nm in names) + "}"

        new = lines[:]
        sl, sc, el, ec = node.lineno, node.col_offset, node.end_lineno, node.end_col_offset
        if sl == el:
            new[sl - 1] = new[sl - 1][:sc] + combo + new[sl - 1][ec:]
        else:
            new[sl - 1: el] = [new[sl - 1][:sc] + combo + new[el - 1][ec:]]
        ins = min([d.lineno for d in getattr(parent, "decorator_list", [])], default=parent.lineno) - 1 if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)) else (node.lineno - 1)
        # for module scope, insert helpers just above the statement's line start
        if isinstance(parent, ast.Module):
            # find the top-level statement containing the node
            stmt = next(s for s in parent.body if s.lineno <= node.lineno <= s.end_lineno)
            ins = stmt.lineno - 1
        new[ins:ins] = [helpers]
        out = "".join(new)
        ast.parse(out)
        Path(path).write_text(out)
        did += 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
