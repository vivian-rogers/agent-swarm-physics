"""H148 round 1 on #51 exploration data (07-06 -> 09-04; 51m reserved and masked; #45-#50 not read).

Runs the amended search (card, Round 1: A1-A7) on the atom panel and computes the pre-registered predictions:
  P1 agents are individuals (single-atom test on both halves) or sit in a discovered agent + own-artifact system;
  P2 the smallest discovered system containing an agent with an own repo is agent + own repo (agents' worth 1);
  P3 a discovered system with >= 3 agents' worth of atoms;
  P4 a discovered memeplex nested over individual agents (element level only);
  P5 no discovered role-text or operator-topic system (element level only);
  P6 kappa > 0 for a multi-agent or memeplex individual (only if one is discovered);
  P7 calibration: multi-atom discoveries on within-day-rotated data / on real data.
Writes data/processed/H148-agent-discovery-51/results/<level>_w<width>.json, individuals_<level>.json and
search/<level>_w<width>.json (per-half terminals, local maxima, out-of-sample scores).

Usage: uv run python hypotheses/H148-agent-discovery-51/analysis/run.py --level agents [--width 30] [--shuffle-reps 2]
       (--level all adds the element atoms written by analysis/elements.py)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h148lib as L  # noqa: E402
import individuality as IND  # noqa: E402

RES = L.OUT / "results"
SEARCH = L.OUT / "search"


def describe(P, ev, res, singles_tab):
    D = res["discovered"]
    bank = None
    out = []
    for k, d in enumerate(D):
        X = tuple(d["atoms"])
        sc = ev.score([X], 0, hes=(1,))
        row = {"id": k, "atoms": list(X), "names": [P.names[a] for a in X], "kinds": [str(P.kind[a]) for a in X],
               "scale": L.scale_of(P, X), "agents_worth": L.agents_worth(P, X), "jaccard": d["jaccard"],
               "atoms_h0": d["atoms_h0"], "atoms_h1": d["atoms_h1"],
               "A_h0": float(sc[0]["A"][0]), "A_h1": float(sc[1]["A"][0]), "nC_h0": float(sc[0]["nC"][0]),
               "nC_h1": float(sc[1]["nC"][0]), "Astar_h0": float(sc[0]["Astar"][0]),
               "Astar_h1": float(sc[1]["Astar"][0]), "z_oos_h0": d["h0"]["z_oos"], "z_oos_h1": d["h1"]["z_oos"],
               "cohesion_oos_h0": d["h0"]["cohesion_oos"], "cohesion_oos_h1": d["h1"]["cohesion_oos"]}
        # integration over its own atoms (held-out ridge logit, individuality.delta_integration), search half 0
        try:
            dl = L.integration(ev, X, 0, 1)
            row["Delta_h1"] = float(dl["Delta"])
        except Exception as exc:     # noqa: BLE001
            row["Delta_h1"] = None
            row["Delta_err"] = str(exc)[:120]
        # partition contrast (STANDARDS 3): each member's coupling to the rest vs every same-kind outside atom as
        # the partner of the same rest, on the other half (search-half-0 codebook); share of peers below the member
        if len(X) >= 2:
            cp = res["cp"]
            ranks = []
            for bm in X:
                rest = tuple(a for a in X if a != bm)
                peers = [a for a in range(P.nA) if P.kind[a] == P.kind[bm] and a not in X and cp.dp.eligible(a, 1)]
                inc = cp.increments(rest, [bm] + peers, 0, hes=(1,), nnull=20)[1]["z"]
                ranks.append(float(np.mean(inc[1:] < inc[0])) if len(peers) else None)
            row["peer_rank_h1"] = ranks
        # the card's matched random systems (secondary, A1): z of A against same-kind, same-A-tercile systems
        if bank is None:
            bank = L.NullBank(ev, 0, "A")
        sq = bank.sequential(bank.signature(X, 0), 0, float(sc[1]["A"][0]), he=1)
        row["z_matched_random_h1"] = sq["z"]
        row["p_matched_random_h1"] = sq["p"]
        out.append(row)
    return out


def nesting_graph(P, indiv, singles_tab):
    nodes = [{"node": f"S{r['atom']}", "atoms": [r["atom"]], "kind": str(P.kind[r["atom"]]),
              "name": P.names[r["atom"]]} for r in singles_tab if r["individual"]]
    nodes += [{"node": f"D{d['id']}", "atoms": d["atoms"], "kind": d["scale"], "name": " + ".join(d["names"])}
              for d in indiv]
    edges = [(nodes[i]["node"], nodes[j]["node"]) for i, j in L.nesting(nodes)]
    return {"nodes": nodes, "edges": edges}


def predictions(P, singles_tab, indiv, present_days, own_rows):
    si = {r["atom"]: r["individual"] for r in singles_tab}
    agents = [int(a) for a in P.agent_rows if present_days[int(a)] >= 10]
    ok1 = []
    for a in agents:
        in_own = any(a in d["atoms"] and d["scale"] == "agent + artifact" for d in indiv)
        ok1.append(bool(si.get(a, False) or in_own))
    p1 = float(np.mean(ok1)) if ok1 else float("nan")
    n_own, n_p2 = 0, 0
    closes_bare = 0
    for a in agents:
        own = own_rows.get(a, [])
        if not own:
            continue
        n_own += 1
        cont = [d for d in indiv if a in d["atoms"]]
        if cont:
            sm = min(cont, key=lambda d: len(d["atoms"]))
            n_p2 += bool(set(sm["atoms"]) & set(own)) and sm["agents_worth"] == 1
        else:
            closes_bare += 1
    p2 = n_p2 / n_own if n_own else float("nan")
    p3 = [d for d in indiv if d["agents_worth"] >= 3]
    return {"P1": {"share": p1, "n_agents": len(agents), "verdict": "supported" if p1 >= 0.9 else
                   ("failed" if p1 < 0.5 else "mixed")},
            "P2": {"share": p2, "n_with_own": n_own, "closes_at_bare_agent": closes_bare},
            "P3": {"n": len(p3), "ids": [d["id"] for d in p3]}}


def element_predictions(P, indiv, ag_ind, ag_ind_ph, width) -> dict:
    """P4 (memeplex individuals over changing hosts, nested over individual agents) and P5 (no role-text or
    operator-topic system), for discovered systems with element atoms (rules: analysis/elements.py, A7)."""
    import polars as pl
    meta = P.meta["element_meta"]
    e0 = int(np.flatnonzero(P.kind == "element")[0])
    H145 = L.ROOT / "data/processed/H145-ideology-egregores-51"
    ex = pl.read_parquet(H145 / f"expr/w{width}.parquet")
    agents_h145 = json.loads((H145 / "expr/agents.json").read_text())["agents"]
    row_of_agent = {int(a): int(np.flatnonzero(P.agent_of == a)[0]) for a in agents_h145 if (P.agent_of == a).any()}
    mps = {K["id"]: set(K["elements"]) for K in json.loads((H145 / "memeplexes.json").read_text())["memeplexes"]}
    p4, p5 = [], []
    for d in indiv:
        X = d["atoms"]
        el = [a for a in X if P.kind[a] == "element"]
        if not el:
            continue
        eids = [meta["eids"][a - e0] for a in el]
        role = [meta["role_like"][a - e0] for a in el]
        oper = [meta["oper_like"][a - e0] for a in el]
        cls = {"id": d["id"], "n_elements": len(el), "role_text_system": bool(sum(role) >= len(el) / 2),
               "operator_topic_system": bool(sum(oper) >= len(el) / 2),
               "role_patterns": sorted({r for a in el for r in meta["role_of"][a - e0]})}
        p5.append(cls)
        if d["scale"] != "memeplex" or len(el) < 2:
            continue
        sub = ex.filter(pl.col("eid").is_in(eids) & (pl.col("count") > 0)).select("agent_row", "bin").unique()
        hb = sub.group_by("agent_row").len()
        hosts = {int(agents_h145[r]): int(n) for r, n in hb.iter_rows()}
        tot = sum(hosts.values())
        h_K = max(hosts.values()) / tot if tot else float("nan")
        n_hosts2 = sum(1 for n in hosts.values() if n >= 2)
        ind_hosts = [a for a in hosts if a in row_of_agent and ag_ind.get(row_of_agent[a], False)]
        ind_hosts_ph = [a for a in hosts if a in row_of_agent and ag_ind_ph.get(row_of_agent[a], False)]
        overlap = {k: len(set(eids) & v) / len(set(eids)) for k, v in mps.items() if set(eids) & v}
        p4.append({"id": d["id"], "n_elements": len(el), "n_hosts_2bins": n_hosts2, "h_K": h_K,
                   "changing_hosts": bool(n_hosts2 >= 3 and h_K < 0.8),
                   "n_individual_hosts": len(ind_hosts), "n_individual_hosts_posthoc": len(ind_hosts_ph),
                   "nested_over_individual_agents": bool(len(ind_hosts) >= 2),
                   "share_in_h145_memeplex": overlap})
    ok4 = [x for x in p4 if x["changing_hosts"] and x["nested_over_individual_agents"]]
    bad5 = [x for x in p5 if x["role_text_system"] or x["operator_topic_system"]]
    return {"P4": {"n_memeplex_individuals": len(p4), "n_meeting_P4": len(ok4), "detail": p4},
            "P5": {"n_element_systems": len(p5), "n_field_systems": len(bad5), "detail": p5,
                   "verdict": "failed" if bad5 else "supported"}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", default="agents", choices=["agents", "elements", "all"])
    ap.add_argument("--width", type=int, default=30)
    ap.add_argument("--shuffle-reps", type=int, default=2)
    ap.add_argument("--z-add", type=float, default=L.Z_ADD)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    SEARCH.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    P = L.load_panel(args.width, with_elements=(args.level != "agents"))
    if args.level == "elements":     # A10: element atoms only, cap 8, z_add 3.2
        kw = dict(cap=L.CAP_EL, z_add=L.Z_ADD_EL, atoms=[a for a in range(P.nA) if P.kind[a] == "element"])
    else:
        kw = dict(z_add=args.z_add)
    ev = L.Evaluator(P)
    at = P.meta["atom_table"]
    own_rows = {}
    for r in at.iter_rows(named=True):
        if r["kind"] == "artifact":
            for o in json.loads(r["own_of"]):
                arow = int(np.flatnonzero(P.agent_of == o)[0])
                own_rows.setdefault(arow, []).append(int(r["atom"]))
    present_days = {int(a): int(np.unique(P.day[P.present[i]]).size) for i, a in enumerate(P.agent_rows)}
    print(f"panel: {P.nA} atoms, {P.nB} bins, transitions {ev.tr[0].size}/{ev.tr[1].size}", flush=True)
    sing = L.singles(ev, list(range(P.nA)), seed=0)
    # post hoc (2026-10-09, after the pre-registered single-atom result): permutation across the half's days within
    # E cells, so day-level state counts as the atom's own
    sing_ph = L.singles(ev, list(range(P.nA)), seed=0, scope="half")
    ag_res = RES / f"agents_w{args.width}.json"
    if args.level != "agents" and ag_res.exists():   # agent single-atom flags from the agent-level run (P4 nesting)
        prev = json.loads(ag_res.read_text())
        ag_ind = {r["atom"]: r["individual"] for r in prev["singles"] if r["kind"] == "agent"}
        ag_ind_ph = {r["atom"]: r["individual"] for r in prev["singles_posthoc_crossday"] if r["kind"] == "agent"}
    else:
        ag_ind = {r["atom"]: r["individual"] for r in sing if str(P.kind[r["atom"]]) == "agent"}
        ag_ind_ph = {r["atom"]: r["individual"] for r in sing_ph if str(P.kind[r["atom"]]) == "agent"}
    print(f"singles done {time.time() - t0:.0f} s", flush=True)
    res = L.discover(P, seed=0, log_every=20, **kw)
    print(f"discover done {time.time() - t0:.0f} s; discovered {len(res['discovered'])}", flush=True)
    indiv = describe(P, ev, res, sing)
    multi_real = sum(1 for d in indiv if len(d["atoms"]) >= 2)
    shuf = []
    for r in range(args.shuffle_reps):
        rng = np.random.default_rng(500 + r)
        Q = P.with_S(IND.rotate_within_day(P.S, P.day, rng))
        rs = L.discover(Q, seed=100 + r, **kw)
        shuf.append({"rep": r, "n_disc": len(rs["discovered"]),
                     "n_multi": sum(1 for d in rs["discovered"] if len(d["atoms"]) >= 2),
                     "n_maxima": sum(len(rs["per_half"][h]["maxima"]) for h in (0, 1)),
                     "n_maxima_held": sum(m["holds"] for h in (0, 1) for m in rs["per_half"][h]["maxima"]),
                     "discovered": [d["atoms"] for d in rs["discovered"]]})
        print(f"shuffle {r}: {shuf[-1]['n_multi']} multi-atom discoveries ({time.time() - t0:.0f} s)", flush=True)
    pred = predictions(P, sing, indiv, present_days, own_rows)
    ph = predictions(P, sing_ph, indiv, present_days, own_rows)["P1"]
    pred["P1_posthoc_crossday"] = {**ph, "verdict": "post hoc (not a test of P1)"}
    ms = float(np.mean([s["n_multi"] for s in shuf])) if shuf else float("nan")
    ratio = ms / multi_real if multi_real else (float("inf") if ms > 0 else float("nan"))
    # P7 as written: multi-atom local maxima (per-half searches, both halves) on rotated vs real data
    lm_real = sum(len(res["per_half"][h]["maxima"]) for h in (0, 1))
    lm_shuf = float(np.mean([s["n_maxima"] for s in shuf])) if shuf else float("nan")
    r_lm = lm_shuf / lm_real if lm_real else float("nan")
    pred["P7"] = {"real_local_maxima": lm_real, "rotated_local_maxima_mean": lm_shuf, "ratio_local_maxima": r_lm,
                  "real_held_maxima": sum(m["holds"] for h in (0, 1) for m in res["per_half"][h]["maxima"]),
                  "rotated_held_maxima_mean": float(np.mean([s["n_maxima_held"] for s in shuf])) if shuf else None,
                  "real_multi_discovered": multi_real, "rotated_multi_discovered_mean": ms, "ratio_discovered": ratio,
                  "verdict": "supported" if r_lm <= 0.1 else "failed" if r_lm >= 0.5 else "mixed"}
    if args.level != "agents":
        pred.update(element_predictions(P, indiv, ag_ind, ag_ind_ph, args.width))
    graph = nesting_graph(P, indiv, sing)
    per_agent = {}
    for i, a in enumerate(P.agent_rows):
        cont = [n for n in graph["nodes"] if int(a) in n["atoms"]]
        if cont:
            per_agent[P.names[a]] = {"smallest": min(cont, key=lambda n: len(n["atoms"]))["name"],
                                     "largest": max(cont, key=lambda n: len(n["atoms"]))["name"]}
    lvl = f"{args.level}_w{args.width}{args.tag}"
    out = {"level": args.level, "width": args.width, "n_atoms": P.nA, "z_add": args.z_add,
           "transitions": [int(ev.tr[0].size), int(ev.tr[1].size)],
           "singles": [{**r, "name": P.names[r["atom"]], "kind": str(P.kind[r["atom"]])} for r in sing],
           "singles_posthoc_crossday": [{**r, "name": P.names[r["atom"]], "kind": str(P.kind[r["atom"]])}
                                        for r in sing_ph],
           "discovered": indiv, "n_exact_agreement": res["n_exact"], "nesting": graph, "per_agent": per_agent,
           "shuffle": shuf, "predictions": pred, "secs": round(time.time() - t0, 1), "n_evals": res["n_evals"]}
    (RES / f"{lvl}.json").write_text(json.dumps(out, indent=1, default=float))
    (L.OUT / f"individuals_{args.level}.json").write_text(json.dumps({"discovered": indiv, "nesting": graph},
                                                                       indent=1, default=float))
    (SEARCH / f"{lvl}.json").write_text(json.dumps(res["per_half"], default=float))
    print(json.dumps(pred, indent=1, default=float))


if __name__ == "__main__":
    main()
