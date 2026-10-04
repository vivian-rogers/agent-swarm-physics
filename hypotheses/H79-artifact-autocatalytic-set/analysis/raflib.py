"""H79 RAF library: reactions from events, maxRAF (Hordijk-Steel pruning; background or strict reactants), temporal
maxCAF, irrRAF structure via catalytic cycles, rewired and time-reversed nulls.

Reaction r = (X, Y): product X written while catalyst Y's code runs (Y = X: self-catalysis). Agents are never catalysts.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

from collections import defaultdict  # noqa: E402

import numpy as np  # noqa: E402


def reactions_from(events: list[dict], catkey: str = "cat") -> dict:
    """events: dicts with eid, product, cat (list), reads (list), n_commits, t_first, kind.
    Returns {(X, Y): {"eids": [...], "commits": n, "t": first time, "reads": reads of the first event}}."""
    R: dict = {}
    for e in sorted(events, key=lambda e: e["t_first"]):
        for y in set(e.get(catkey) or []):
            k = (e["product"], y)
            if k not in R:
                R[k] = {"eids": [], "commits": 0, "t": e["t_first"], "reads": set(e.get("reads") or []) - {e["product"], y}}
            R[k]["eids"].append(e["eid"])
            R[k]["commits"] += e["n_commits"]
    return R


def closure(R: set, reads: dict, food: set, background: set | None = None) -> set:
    """cl_R(F): smallest W >= F such that every r in R with reactants in W adds its product (catalysis ignored).
    background: products of uncatalysed (agent) events, always available as reactants."""
    W = set(food) | (background or set())
    changed = True
    while changed:
        changed = False
        for (x, y) in R:
            if x not in W and reads[(x, y)] <= W:
                W.add(x)
                changed = True
    return W


def max_raf(R: dict, food: set, strict: bool = False, background: set | None = None) -> set:
    """Unique maximal RAF. Non-strict (default, amendment A1): reactants never bind (agent work is the
    uncatalysed background); a reaction needs a catalyst in F or among the products of the current set.
    Strict: reactants must be in cl_R'(F) (no background) and the catalyst too."""
    cur = set(R)
    reads = {k: v["reads"] for k, v in R.items()}
    while True:
        if strict:
            W = closure(cur, reads, food, background)
            keep = {r for r in cur if reads[r] <= W and r[1] in W}
        else:
            P = {x for (x, _y) in cur} | set(food)
            keep = {r for r in cur if r[1] in P}
        if keep == cur:
            return cur
        cur = keep


def max_caf_events(events: list[dict], food: set, catkey: str = "cat") -> set:
    """Temporal maxCAF: in event-time order, an event fires if one of its catalysts is food or was produced by an
    earlier CAF event; its product then becomes available. Returns the CAF event ids."""
    avail = set(food)
    out = set()
    for e in sorted(events, key=lambda e: e["t_first"]):
        cats = set(e.get(catkey) or [])
        if cats and (cats & avail):
            out.add(e["eid"])
            avail.add(e["product"])
    return out


def catalytic_graph(raf: set, food: set, R: dict | None = None, min_support: int = 1) -> dict:
    """Y -> X edges among non-food artifacts, Y != X (the only place a multi-reaction irrRAF can live).
    min_support: keep only reactions backed by >= this many events (amendment A2)."""
    G = defaultdict(set)
    for (x, y) in raf:
        if R is not None and len(R[(x, y)]["eids"]) < min_support:
            continue
        if x != y and x not in food and y not in food:
            G[y].add(x)
    return G


def sccs(G: dict) -> list[list]:
    """Tarjan (iterative)."""
    index, low, on, st, out = {}, {}, set(), [], []
    nodes = set(G) | {v for vs in G.values() for v in vs}
    c = [0]
    for s in nodes:
        if s in index:
            continue
        stack = [(s, iter(G.get(s, ())))]
        index[s] = low[s] = c[0]
        c[0] += 1
        st.append(s)
        on.add(s)
        while stack:
            v, it = stack[-1]
            nxt = next(it, None)
            if nxt is not None:
                if nxt not in index:
                    index[nxt] = low[nxt] = c[0]
                    c[0] += 1
                    st.append(nxt)
                    on.add(nxt)
                    stack.append((nxt, iter(G.get(nxt, ()))))
                elif nxt in on:
                    low[v] = min(low[v], index[nxt])
            else:
                stack.pop()
                if stack:
                    low[stack[-1][0]] = min(low[stack[-1][0]], low[v])
                if low[v] == index[v]:
                    comp = []
                    while True:
                        w = st.pop()
                        on.discard(w)
                        comp.append(w)
                        if w == v:
                            break
                    out.append(comp)
    return out


def cycle_stats(G: dict, max_len: int = 6, cap: int = 2000) -> dict:
    """Simple directed cycles (length 2..max_len) inside non-trivial SCCs. Each simple cycle is an irrRAF."""
    lengths = defaultdict(int)
    nodes_in = set()
    n_found = 0
    for comp in sccs(G):
        if len(comp) < 2:
            continue
        cs = set(comp)
        nodes_in |= cs
        order = {v: i for i, v in enumerate(sorted(comp))}
        for s in sorted(comp):
            # cycles whose smallest node (by order) is s
            stack = [(s, [s])]
            while stack and n_found < cap:
                v, path = stack.pop()
                for w in G.get(v, ()):
                    if w not in cs or order[w] < order[s]:
                        continue
                    if w == s and len(path) >= 2:
                        lengths[len(path)] += 1
                        n_found += 1
                    elif w not in path and len(path) < max_len:
                        stack.append((w, path + [w]))
    return {"n_cycles": int(sum(lengths.values())), "by_len": {int(k): int(v) for k, v in sorted(lengths.items())},
            "max_len": int(max(lengths) if lengths else 0), "S2": int(bool(lengths)),
            "S3": int(any(k >= 3 for k in lengths)), "n_nodes_in_scc": len(nodes_in), "truncated": n_found >= cap}


def rewire(events: list[dict], rng, catkey: str = "cat", skip_kind: str = "auto") -> list[dict]:
    """Degree-preserving rewiring of cross-catalysis (amendment A2): permute the catalyst column of the
    (event, catalyst) edges with catalyst != product, for agent events. Self-catalysis edges and automated
    self-reactions stay fixed. Each event keeps its number of cross edges; each catalyst its number of uses."""
    edges = [(i, y) for i, e in enumerate(events) if e.get("kind") != skip_kind
             for y in (e.get(catkey) or []) if y != e["product"]]
    if not edges:
        return events
    ys = [y for _, y in edges]
    rng.shuffle(ys)
    new = defaultdict(list)
    for (i, _), y in zip(edges, ys):
        new[i].append(y)
    out = []
    for i, e in enumerate(events):
        if e.get("kind") == skip_kind:
            out.append(e)
            continue
        d = dict(e)
        keep_self = [y for y in (e.get(catkey) or []) if y == e["product"]]
        d[catkey] = list(set(keep_self + new.get(i, [])))
        out.append(d)
    return out


def summarize(events: list[dict], food: set, catkey: str = "cat", strict: bool = False, created: dict | None = None):
    """Per-period statistics. created: artifact -> first_t (to classify in-period tools)."""
    R = reactions_from(events, catkey)
    bg = {e["product"] for e in events if not (e.get(catkey))}
    raf = max_raf(R, food, strict=strict, background=bg)
    raf_eids = set()
    for r in raf:
        raf_eids.update(R[r]["eids"])
    caf = max_caf_events(events, food, catkey)
    ag = [e for e in events if e.get("kind") != "auto"]
    au = [e for e in events if e.get("kind") == "auto"]
    W = sum(e["n_commits"] for e in ag)
    Wa = sum(e["n_commits"] for e in au)
    cov = sum(e["n_commits"] for e in ag if e["eid"] in raf_eids)
    cov_all = cov + sum(e["n_commits"] for e in au if e["eid"] in raf_eids)
    catal = sum(e["n_commits"] for e in ag if e.get(catkey))
    caf_c = sum(e["n_commits"] for e in events if e["eid"] in caf and e["eid"] in raf_eids)
    raf_c = sum(e["n_commits"] for e in events if e["eid"] in raf_eids)
    # catalyst classes (non-exclusive) among RAF reactions, for agent events
    self_c = food_c = new_c = 0
    self_all = 0
    rset = raf
    for e in events:
        if e["eid"] not in raf_eids:
            continue
        ys = [y for y in (e.get(catkey) or []) if (e["product"], y) in rset]
        is_self = e["product"] in ys
        if is_self:
            self_all += e["n_commits"]
        if e.get("kind") == "auto":
            continue
        self_c += e["n_commits"] * is_self
        food_c += e["n_commits"] * any(y in food and y != e["product"] for y in ys)
        new_c += e["n_commits"] * any(y not in food and y != e["product"] for y in ys)
    cyc = cycle_stats(catalytic_graph(raf, food))
    cyc3 = cycle_stats(catalytic_graph(raf, food, R, 3))
    return {"n_events_agent": len(ag), "n_events_auto": len(au), "work_commits": W, "auto_commits": Wa,
            "n_reactions": len(R), "n_raf_reactions": len(raf),
            "catalysed_share": catal / W if W else float("nan"),
            "coverage": cov / W if W else float("nan"),
            "coverage_all_identity": cov_all / (W + Wa) if (W + Wa) else float("nan"),
            "self_share_of_raf_commits_all": self_all / raf_c if raf_c else float("nan"),
            "self_share_work": self_c / W if W else float("nan"),
            "food_tool_share_work": food_c / W if W else float("nan"),
            "inperiod_tool_share_work": new_c / W if W else float("nan"),
            "caf_over_raf_commits": caf_c / raf_c if raf_c else float("nan"),
            "cycles": cyc, "cycles_support3": cyc3, "_raf": raf, "_R": R}
