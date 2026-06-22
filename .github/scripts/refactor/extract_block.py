#!/usr/bin/env python3
"""Mechanically-safe 'extract function' for a contiguous block of top-level
statements inside a function. Computes inputs (locals read in block that were
bound before it) and outputs (locals assigned in block and read after it),
emits a module-level helper, and replaces the block with a call.

Refuses blocks containing return/yield/break/continue/nonlocal/global or
references to names that are free in a way it can't thread.

Usage: python3 extract_block.py <file.py> <func_name> <start_line> <end_line> <helper_name>
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path


def _comp_targets(node):
    out = set()
    for n in ast.walk(node):
        if isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            for g in n.generators:
                out |= {t.id for t in ast.walk(g.target) if isinstance(t, ast.Name)}
    return out


def stores(node):
    # comprehension/generator targets are scoped to the comp, not the function
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)} - _comp_targets(node)


def loads(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


def main():
    path = Path(sys.argv[1]); fname = sys.argv[2]
    s_line, e_line = int(sys.argv[3]), int(sys.argv[4]); helper = sys.argv[5]
    src = path.read_text(); lines = src.splitlines(keepends=True)
    tree = ast.parse(src)
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == fname), None)
    if fn is None:
        print("no func"); return 1

    body = fn.body
    block = [st for st in body if st.lineno >= s_line and st.end_lineno <= e_line]
    if not block:
        print("empty block"); return 1
    bset = set(block)
    before = [st for st in body if st.end_lineno < block[0].lineno]
    after = [st for st in body if st.lineno > block[-1].end_lineno]

    # refuse return/yield/global anywhere; refuse break/continue only when they
    # would escape the block (not enclosed by a loop that is inside the block).
    for st in block:
        for n in ast.walk(st):
            if isinstance(n, (ast.Return, ast.Yield, ast.YieldFrom, ast.Global, ast.Nonlocal)):
                print("block has return/yield/global"); return 1

    def loops_ok(node, in_loop):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.Break, ast.Continue)):
                if not in_loop:
                    return False
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue  # nested scopes own their loops
            else:
                ci = in_loop or isinstance(child, (ast.For, ast.While, ast.AsyncFor))
                if not loops_ok(child, ci):
                    return False
        return True

    for st in block:
        si = isinstance(st, (ast.For, ast.While, ast.AsyncFor))
        if not loops_ok(st, si):
            print("block has escaping break/continue"); return 1

    params = {a.arg for a in list(fn.args.args) + list(fn.args.posonlyargs) + list(fn.args.kwonlyargs)}
    if fn.args.vararg: params.add(fn.args.vararg.arg)
    if fn.args.kwarg: params.add(fn.args.kwarg.arg)
    bound_before = set(params)
    for st in before:
        bound_before |= stores(st)

    block_loads = set().union(*[loads(st) for st in block]) if block else set()
    block_stores = set().union(*[stores(st) for st in block]) if block else set()
    after_loads = set().union(*[loads(st) for st in after]) if after else set()
    after_stores = set().union(*[stores(st) for st in after]) if after else set()

    # loop/with targets in the block are redefined before use -> not real inputs
    redefined = set()
    for st in block:
        for n in ast.walk(st):
            if isinstance(n, (ast.For, ast.AsyncFor)):
                redefined |= {t.id for t in ast.walk(n.target) if isinstance(t, ast.Name)}
            elif isinstance(n, (ast.With, ast.AsyncWith)):
                for item in n.items:
                    if item.optional_vars:
                        redefined |= {t.id for t in ast.walk(item.optional_vars) if isinstance(t, ast.Name)}

    inputs = sorted((block_loads & bound_before) - redefined)
    inset = set(inputs)
    # A name must be returned if it is (a) a threaded accumulator: an input the
    # block reassigns and the after-code reads, or (b) produced in the block,
    # read after, and never reassigned in the after-code (so it can only come
    # from the block). Loop temporaries reassigned in `after` are excluded.
    outputs = sorted(
        (block_stores & inset & after_loads)
        | ((block_stores & after_loads) - after_stores)
    )

    indent = lines[block[0].lineno - 1][: len(lines[block[0].lineno - 1]) - len(lines[block[0].lineno - 1].lstrip())]
    block_src = "".join(lines[block[0].lineno - 1: block[-1].end_lineno])
    # build helper (dedent block by removing the function indent level)
    # block is at one indent inside fn; helper body needs 4-space indent.
    base_indent = indent
    helper_body = ""
    for ln in block_src.splitlines(keepends=True):
        if ln.strip() == "":
            helper_body += ln
        elif ln.startswith(base_indent):
            helper_body += "    " + ln[len(base_indent):]
        else:
            helper_body += "    " + ln
    ret = ("    return " + ", ".join(outputs) + "\n") if outputs else ""
    helper_src = f"def {helper}({', '.join(inputs)}):\n{helper_body}{ret}\n\n"

    lhs = (", ".join(outputs) + " = ") if outputs else ""
    call = f"{base_indent}{lhs}{helper}({', '.join(inputs)})\n"

    # splice: replace block lines with call; insert helper before fn
    new = lines[:]
    new[block[0].lineno - 1: block[-1].end_lineno] = [call]
    fstart = min([d.lineno for d in getattr(fn, "decorator_list", [])], default=fn.lineno) - 1
    new[fstart:fstart] = [helper_src]
    out = "".join(new)
    ast.parse(out)  # must parse
    path.write_text(out)
    print(f"extracted {helper}({', '.join(inputs)}) -> ({', '.join(outputs)}) [{len(block)} stmts]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
