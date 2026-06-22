import ast, sys
from pathlib import Path
from collections import defaultdict

def load(d):
    mods={f.stem:f for f in d.glob("*.py")}
    E=defaultdict(list)
    for stem,f in mods.items():
        for n in ast.parse(f.read_text()).body:
            if isinstance(n,ast.ImportFrom) and n.module:
                m=n.module.split(".")[-1]
                if m in mods and m!=stem: E[stem].append((m,n))
    return mods,E

def back_edges(mods,E):
    adj={k:set(m for m,_ in v) for k,v in E.items()}
    color=defaultdict(int); back=[]
    def dfs(u):
        color[u]=1
        for v in adj.get(u,()):
            if color[v]==1: back.append((u,v))
            elif color[v]==0: dfs(v)
        color[u]=2
    for s in sorted(mods):
        if color[s]==0: dfs(s)
    return back

def mod_level_names(tree):
    top=set()
    for n in tree.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            for d in n.decorator_list: top|={x.id for x in ast.walk(d) if isinstance(x,ast.Name)}
        elif not isinstance(n,(ast.Import,ast.ImportFrom)):
            top|={x.id for x in ast.walk(n) if isinstance(x,ast.Name)}
    return top

def move_import(mods, src_stem, tgt_stem, E):
    """Move src_stem's top-level `from tgt import ...` below defs, if not module-level used."""
    f=mods[src_stem]; src=f.read_text(); tree=ast.parse(src); lines=src.splitlines(keepends=True)
    mlevel=mod_level_names(tree)
    imps=[n for m,n in E[src_stem] if m==tgt_stem]
    movable=[i for i in imps if not ({a.asname or a.name for a in i.names} & mlevel)]
    if not movable: return None
    drop=set(); moved=""
    for i in movable:
        for ln in range(i.lineno,i.end_lineno+1): drop.add(ln)
        moved+="".join(lines[i.lineno-1:i.end_lineno])
    new=[l for k,l in enumerate(lines,1) if k not in drop]
    out="".join(new).rstrip()+"\n\n\n# deferred to break import cycle  # noqa: E402\n"+moved
    ast.parse(out); f.write_text(out)
    return [a.asname or a.name for i in movable for a in i.names]

def fix(d):
    d=Path(d); mods,E=load(d); bes=back_edges(mods,E)
    if not bes: return "no cycle"
    out=[]
    for u,v in bes:
        # try moving u's import of v, else v's import of u
        r=move_import(mods,u,v,E)
        if r: out.append(f"moved {r}: {u}<-{v}"); continue
        mods,E=load(d)  # reload after potential change
        r=move_import(mods,v,u,E)
        if r: out.append(f"moved {r}: {v}<-{u}")
        else: out.append(f"UNRESOLVED {u}<->{v}")
        mods,E=load(d)
    return "; ".join(out)

print(fix(sys.argv[1]))
