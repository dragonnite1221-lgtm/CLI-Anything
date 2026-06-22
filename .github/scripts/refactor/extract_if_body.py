#!/usr/bin/env python3
"""Extract the body of an always-returning if-branch into a module-level helper
and replace it with `return <helper>(args)`. For command-dispatch functions.

The if at <if_line> in <func> must have a body where every path ends in
return/raise. Helper params = names the body reads that are bound earlier in the
function. Verbatim body (returns preserved).

Usage: python3 extract_if_body.py <file.py> <func> <if_line> <helper>
"""
import ast
import sys
from pathlib import Path


def stores(node):
    comp = set()
    for n in ast.walk(node):
        if isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            for g in n.generators:
                comp |= {t.id for t in ast.walk(g.target) if isinstance(t, ast.Name)}
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)} - comp


def loads(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


def always_returns(stmts):
    for s in reversed(stmts):
        if isinstance(s, (ast.Return, ast.Raise)):
            return True
        if isinstance(s, ast.If) and s.orelse:
            return always_returns(s.body) and always_returns(s.orelse)
        if isinstance(s, (ast.With, ast.AsyncWith)):
            return always_returns(s.body)
        return False
    return False


def main():
    path = Path(sys.argv[1]); func = sys.argv[2]; if_line = int(sys.argv[3]); helper = sys.argv[4]
    src = path.read_text(); lines = src.splitlines(keepends=True)
    tree = ast.parse(src)
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == func), None)
    if fn is None:
        print("no func"); return 1
    node = next((s for s in fn.body if isinstance(s, ast.If) and s.lineno == if_line), None)
    if node is None:
        print("no if at line"); return 1
    if not always_returns(node.body):
        print("branch does not always return"); return 1

    params_av = {a.arg for a in list(fn.args.args) + list(fn.args.posonlyargs) + list(fn.args.kwonlyargs)}
    if fn.args.vararg:
        params_av.add(fn.args.vararg.arg)
    if fn.args.kwarg:
        params_av.add(fn.args.kwarg.arg)
    bound_before = set(params_av)
    for s in fn.body:
        if s is node:
            break
        bound_before |= stores(s)

    body_stmts = node.body
    body_loads = set().union(*[loads(s) for s in body_stmts]) if body_stmts else set()
    inputs = sorted(body_loads & bound_before)

    b0, b1 = body_stmts[0].lineno, body_stmts[-1].end_lineno
    body_src = "".join(lines[b0 - 1: b1])
    # de-indent body to 4 spaces
    base = lines[b0 - 1][:len(lines[b0 - 1]) - len(lines[b0 - 1].lstrip())]
    hbody = ""
    for ln in body_src.splitlines(keepends=True):
        if ln.strip() == "":
            hbody += ln
        elif ln.startswith(base):
            hbody += "    " + ln[len(base):]
        else:
            hbody += ln
    helper_src = f"def {helper}({', '.join(inputs)}):\n{hbody}\n\n"

    # replace the if-body lines with `return helper(...)` at body indent
    call = f"{base}return {helper}({', '.join(inputs)})\n"
    new = lines[:]
    new[b0 - 1: b1] = [call]
    fstart = min([d.lineno for d in getattr(fn, "decorator_list", [])], default=fn.lineno) - 1
    new[fstart:fstart] = [helper_src]
    out = "".join(new)
    ast.parse(out)
    path.write_text(out)
    print(f"extracted if-body -> {helper}({', '.join(inputs)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
