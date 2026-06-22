#!/usr/bin/env python3
"""Split a giant `NAME = f'''...'''` assignment (one JoinedStr) inside a function
into helper functions each returning a slice of the f-string, concatenated. Each
helper takes the local names its substitutions reference as parameters.

Behavior-identical: concatenation of f-string slices == original f-string, and
the flattened JoinedStr value sequence is verified equal to the original.

Usage: python3 split_fstring.py <file.py> <func> [max_lines=120]
"""
import ast
import sys
from pathlib import Path


def func_locals(fn):
    out = set()
    for a in list(fn.args.args) + list(fn.args.posonlyargs) + list(fn.args.kwonlyargs):
        out.add(a.arg)
    if fn.args.vararg:
        out.add(fn.args.vararg.arg)
    if fn.args.kwarg:
        out.add(fn.args.kwarg.arg)
    for n in ast.walk(fn):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
            out.add(n.id)
    return out


def main():
    path = Path(sys.argv[1]); func = sys.argv[2]
    max_lines = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    src = path.read_text()
    lines = src.splitlines(keepends=True)
    tree = ast.parse(src)
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == func), None)
    if fn is None:
        print("no func"); return 1
    asn = None
    for s in fn.body:
        if isinstance(s, (ast.Assign, ast.AnnAssign)) and isinstance(s.value, ast.JoinedStr):
            if (s.value.end_lineno - s.value.lineno + 1) > max_lines:
                asn = s; break
    if asn is None:
        print("no big f-string"); return 1
    js = asn.value
    target = asn.targets[0].id if isinstance(asn, ast.Assign) else asn.target.id
    locs = func_locals(fn)

    # the raw inner text between the f-string quotes
    open_line = lines[js.lineno - 1]
    # locate prefix quote
    q = None
    for cand in ('f"""', "f'''", 'rf"""', "rf'''", 'fr"""', "fr'''"):
        idx = open_line.find(cand, js.col_offset)
        if idx != -1 and idx <= js.col_offset + 2:
            q = cand; qcol = idx; break
    if q is None:
        print("not a triple-quoted f-string"); return 1
    quote = q[-3:]
    full = "".join(lines[js.lineno - 1: js.end_lineno])
    start = full.find(q) + len(q)
    end = full.rfind(quote)
    inner = full[start:end]

    # split inner at depth-0 newlines into ~equal chunks
    depth = 0
    safe_nl = []  # indices in inner where a newline at brace depth 0 occurs
    i = 0
    while i < len(inner):
        c = inner[i]
        if c == "{" and i + 1 < len(inner) and inner[i + 1] == "{":
            i += 2; continue
        if c == "}" and i + 1 < len(inner) and inner[i + 1] == "}":
            i += 2; continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif c == "\n" and depth == 0:
            safe_nl.append(i)
        i += 1
    total_lines = inner.count("\n")
    if total_lines < max_lines or len(safe_nl) < 2:
        print("not enough safe split points"); return 1
    # choose cut points ~ every max_lines lines
    cuts = []
    line_count = 0
    for idx in safe_nl:
        line_count = inner[:idx].count("\n")
        if line_count >= (len(cuts) + 1) * max_lines:
            cuts.append(idx + 1)
    pieces = []
    prev = 0
    for cidx in cuts:
        pieces.append(inner[prev:cidx]); prev = cidx
    pieces.append(inner[prev:])
    pieces = [p for p in pieces if p != ""]
    if len(pieces) < 2:
        print("single piece"); return 1

    def free_params(piece_text):
        try:
            pjs = ast.parse(f"f'''{piece_text}'''").body[0].value
        except SyntaxError:
            return None
        names = set()
        for v in getattr(pjs, "values", []):
            if isinstance(v, ast.FormattedValue):
                names |= {n.id for n in ast.walk(v) if isinstance(n, ast.Name)}
        return sorted(names & locs)

    helpers = ""
    calls = []
    base = f"_{func}_fs"
    existing = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    k0 = 0
    while any(f"{base}{k0}_{j}" in existing for j in range(len(pieces))):
        k0 += 1
    for pi, piece in enumerate(pieces):
        params = free_params(piece)
        if params is None:
            print(f"piece {pi} not a valid f-string slice"); return 1
        hn = f"{base}{k0}_{pi}"
        helpers += f"def {hn}({', '.join(params)}):\n    return f{quote}{piece}{quote}\n\n\n"
        calls.append(f"{hn}({', '.join(params)})")
    indent = open_line[:len(open_line) - len(open_line.lstrip())]
    repl = f"{indent}{target} = " + " + ".join(calls) + "\n"

    new = lines[:]
    new[asn.lineno - 1: asn.end_lineno] = [repl]
    fstart = min([d.lineno for d in getattr(fn, "decorator_list", [])], default=fn.lineno) - 1
    new[fstart:fstart] = [helpers]
    out = "".join(new)
    ast.parse(out)
    path.write_text(out)
    print(f"split f-string in {func} into {len(pieces)} pieces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
