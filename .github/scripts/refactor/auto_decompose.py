#!/usr/bin/env python3
"""Decompose every function > target lines in a file by repeatedly extracting
either the largest top-level compound statement or, failing that, a contiguous
window of top-level statements (via extract_block, which validates data flow and
refuses return/yield/escaping break/continue).

Usage: python3 auto_decompose.py <file.py> <target> <helper_prefix>
"""
import ast
import subprocess
import sys


def all_fns(path):
    t = ast.parse(open(path).read())
    return [n for n in ast.walk(t)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def try_extract(path, func, s_line, e_line, name):
    r = subprocess.run(
        ["python3", "/tmp/extract_block.py", path, func, str(s_line), str(e_line), name],
        capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.startswith("extracted")


def main():
    path, target, pfx = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    i = 0
    guard = 0
    while True:
        guard += 1
        if guard > 200:
            print("guard stop"); return 2
        fns = [n for n in all_fns(path) if (n.end_lineno - n.lineno + 1) > target]
        # innermost/leaf-ish first: skip funcs that contain another giant (decompose inner first)
        fns = [f for f in fns if not any(
            g is not f and g.lineno >= f.lineno and g.end_lineno <= f.end_lineno
            for g in fns)]
        if not fns:
            print("done"); return 0
        fn = fns[0]
        func = fn.name
        body = [s for s in fn.body if not isinstance(s, (ast.Return, ast.Raise))
                or s is not fn.body[-1]]
        # candidate 1: largest compound block
        comps = sorted(
            [s for s in fn.body if isinstance(s, (ast.For, ast.While, ast.If, ast.With,
                                                  ast.Try, ast.AsyncFor, ast.AsyncWith))],
            key=lambda s: (s.end_lineno - s.lineno + 1), reverse=True)
        progressed = False
        for s in comps:
            if (s.end_lineno - s.lineno + 1) < 12:
                break
            if try_extract(path, func, s.lineno, s.end_lineno, f"{pfx}{i}"):
                i += 1; progressed = True; break
        if progressed:
            continue
        # candidate 2: contiguous windows of top-level statements (skip trailing return)
        stmts = [s for s in fn.body if not isinstance(s, ast.Return)]
        n = len(stmts)
        best = None
        for a in range(n):
            for b in range(n, a, -1):
                span = stmts[b - 1].end_lineno - stmts[a].lineno + 1
                if span < 30 or span > 150:
                    continue
                best = (stmts[a].lineno, stmts[b - 1].end_lineno, span)
                break
            if best:
                break
        if best and try_extract(path, func, best[0], best[1], f"{pfx}{i}"):
            i += 1
            continue
        # candidate 3: try every window, largest-first, until one extracts
        done_one = False
        windows = []
        for a in range(n):
            for b in range(a + 1, n + 1):
                span = stmts[b - 1].end_lineno - stmts[a].lineno + 1
                if 20 <= span <= 150:
                    windows.append((span, stmts[a].lineno, stmts[b - 1].end_lineno))
        windows.sort(reverse=True)
        for span, sl, el in windows:
            if try_extract(path, func, sl, el, f"{pfx}{i}"):
                i += 1; done_one = True; break
        if not done_one:
            print(f"stuck on {func} size={fn.end_lineno - fn.lineno + 1}"); return 3


if __name__ == "__main__":
    raise SystemExit(main())
