import ast, sys
from pathlib import Path
from collections import defaultdict

def analyze(pkgdir):
    d=Path(pkgdir)
    mods={f.stem:f for f in d.glob("*.py")}
    # top-level cross-part edges: stem -> {(imported_stem, [names])}
    edges=defaultdict(list)
    for stem,f in mods.items():
        for n in ast.parse(f.read_text()).body:  # TOP-LEVEL only
            if isinstance(n,ast.ImportFrom) and n.module:
                m=n.module.split(".")[-1]
                if m in mods and m!=stem:
                    edges[stem].append((m,[a.name for a in n.names]))
    # find cycles (SCC via simple DFS)
    adj={k:set(m for m,_ in v) for k,v in edges.items()}
    color=defaultdict(int); back=[]
    def dfs(u,stk):
        color[u]=1
        for v in adj.get(u,()):
            if color[v]==1:  # back-edge u->v closes a cycle
                back.append((u,v))
            elif color[v]==0:
                dfs(v,stk+[u])
        color[u]=2
    for s in mods:
        if color[s]==0: dfs(s,[])
    return edges, back

if __name__=="__main__":
    edges,back=analyze(sys.argv[1])
    print("BACK-EDGES (cycle closers):")
    for u,v in back:
        names=[nm for m,nm in edges[u] if m==v]
        print(f"  {u} -> {v}  imports {names}")
