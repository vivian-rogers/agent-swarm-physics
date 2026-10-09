"""H145 round 1 on #51 exploration data (non-reserved days 07-06 -> 09-04). Reads the frozen memeplexes.json; computes
P1-P6 by the card's rules as amended in Round 1 (A1-A5). Writes data/processed/H145-ideology-egregores-51/results/.

Usage: uv run python hypotheses/H145-ideology-egregores-51/analysis/run_real.py [--stage p1|tests|p6|all]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h145lib as L  # noqa: E402
import individuality as IND  # noqa: E402
import memeplex as MP  # noqa: E402
import build as B  # noqa: E402

RES = L.OUT / "results"
N_NULL_PIPE = 20
N_PSEUDO_P2 = 200
BC = dict(h=10, n_max=200, min_draws=30)
P2_RULE = "phi"            # Amendment A4 (fixed from the synthetic check before real data): host memory phi_K(5)
SEED = 20261009


def js(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def load_mem():
    return json.loads((L.OUT / "memeplexes.json").read_text())


def p1(rng):
    P = B.load_panel(120)
    disc = json.loads((L.OUT / "discovery.json").read_text())
    obs = disc["n_qualify_hub_free"]
    counts, counts_all = [], []
    for i in range(N_NULL_PIPE):
        pn = MP.rotate_elements(P, np.random.default_rng(int(rng.integers(1 << 31))), scope="agent")
        r = MP.discover(pn, B.GAMMA, m=B.M_HOST, W=MP.ppmi_graph(pn, 3, activity=B.ACTIVITY, fdr=B.FDR), seed=B.SEED)
        counts.append(int(r["n_qualify_hub_free"]))
        counts_all.append(int(r["n_qualify"]))
        L.log("P1 null", i, counts[-1])
    day = []
    for i in range(5):
        pn = MP.rotate_elements(P, np.random.default_rng(int(rng.integers(1 << 31))), scope="day")
        r = MP.discover(pn, B.GAMMA, m=B.M_HOST, W=MP.ppmi_graph(pn, 3, activity=B.ACTIVITY, fdr=B.FDR), seed=B.SEED)
        day.append(int(r["n_qualify_hub_free"]))
    q95 = float(np.quantile(counts, 0.95))
    out = {"obs_hub_free": obs, "obs_all": disc["n_qualify"], "null_counts": counts, "null_counts_all": counts_all,
           "null_q95": q95, "pass": bool(obs >= 3 and obs > q95), "null_counts_within_day_descriptive": day,
           "variants": disc["variants"]}
    return out


def p2_one(pn, K, es, rng, m=2):
    obs = L.renewal(pn, K, m)
    obs["phi"] = L.host_memory(pn, K, m)
    pools = L.matched_pool(es, K)
    null = []
    for _ in range(N_PSEUDO_P2):
        Pp = L.draw_pseudo(pools, rng)
        r = L.renewal(pn, Pp, m)
        r["phi"] = L.host_memory(pn, Pp, m)
        null.append(r)
    out = {"obs": obs}
    for key, side in (("diff", "greater"), ("D", "greater"), ("phi", "less")):
        v = np.array([x[key] for x in null], float)
        v = v[np.isfinite(v)]
        if side == "greater":
            thr = float(np.quantile(v, 0.95)) if len(v) else np.nan
            ok = bool(np.isfinite(obs[key]) and obs[key] > thr and (obs[key] > 0 if key == "diff" else True))
        else:
            thr = float(np.quantile(v, 0.05)) if len(v) else np.nan
            ok = bool(np.isfinite(obs[key]) and obs[key] < thr)
        out[key] = {"obs": obs[key], "thr": thr, "null_mean": float(v.mean()) if len(v) else np.nan, "pass": ok}
    out["pass"] = out[P2_RULE]["pass"]
    out["pass_as_written"] = out["diff"]["pass"]
    return out


def p3_one(pn, K, eb, es, rng, cross_day=False, with_delta=True):
    ks = L.krakauer_pattern(pn, K, eb, cross_day=cross_day, with_delta=with_delta)
    if ks is None:
        return {"ok": False}
    pools = L.matched_pool(es, K)
    draws = []

    def mk(stat):
        idx = {"i": 0}

        def f():
            i = idx["i"]
            idx["i"] += 1
            if i < len(draws):
                r = draws[i]
            else:
                r = L.krakauer_pattern(pn, L.draw_pseudo(pools, rng), eb, cross_day=cross_day, with_delta=with_delta)
                draws.append(r)
            return np.nan if r is None else getattr(r, stat)
        return f
    out = {"ok": True, "A": ks.A, "A_star": ks.A_star, "nC": ks.nC, "NTIC": ks.NTIC, "Delta": ks.Delta, "n": ks.n}
    for stat in (("A", "A_star", "Delta") if with_delta else ("A", "A_star")):
        r = IND.besag_clifford(getattr(ks, stat), mk(stat), **BC)
        out[f"{stat}_z"], out[f"{stat}_p"], out[f"{stat}_n"] = r["z"], r["p"], r["n"]
        out[f"{stat}_excess"] = getattr(ks, stat) - r["mu"]
    out["pass_A"] = bool(np.isfinite(out["A_z"]) and out["A_z"] >= 2)
    out["pass_Delta"] = bool(with_delta and np.isfinite(out.get("Delta_z", np.nan)) and out["Delta_z"] >= 2)
    return out


def tests(rng):
    mem = load_mem()
    P = B.load_panel(120)
    es = L.element_stats(P)
    eb = L.env_base_real(P)
    rows = []
    for k in mem["memeplexes"]:
        if not k["qualifies_hub_free"]:
            continue
        t = time.time()
        r = {"id": k["id"], "candidate": k["candidate"], "n_el": k["n_elements"], "h_K": k["h_K"],
             "field_seeded": k["field_seeded"], "P2": p2_one(P, k["elements"], es, rng),
             "P3": p3_one(P, k["elements"], eb, es, rng)}
        rows.append(r)
        L.log(k["id"], k["candidate"], f"P2 {r['P2']['pass']} P3 A_z {r['P3'].get('A_z')} D_z {r['P3'].get('Delta_z')}",
              f"{time.time() - t:.0f}s")
    hub = []
    for k in mem["memeplexes"]:
        if k["qualifies_hub_free"]:
            continue
        hub.append({"id": k["id"], "candidate": k["candidate"], "h_K": k["h_K"], "P2": p2_one(P, k["elements"], es, rng)})
    ctrl = []
    for rp in mem["role_patterns"]:
        r = {"id": rp["id"], "kind": rp["kind"], "P3": p3_one(P, rp["elements"], eb, es, rng, with_delta=False)}
        ps = MP.pattern_stats(P, rp["elements"], 2)
        r.update({"n_hosts": ps["n_hosts"], "lifetime_days": ps["lifetime_days"]})
        ctrl.append(r)
        L.log("control", rp["id"], r["P3"].get("A_star_z"), r["P3"].get("A_z"))
    return {"memeplexes": rows, "hub_memeplexes": hub, "role_patterns": ctrl}


def p6(rng, ids):
    mem = {k["id"]: k for k in load_mem()["memeplexes"]}
    out = {}
    for w in (30, 120, 1440):
        P = B.load_panel(w)
        es = L.element_stats(P)
        eb = L.env_base_real(P)
        for i in ids:
            r = p3_one(P, mem[i]["elements"], eb, es, rng, cross_day=(w == 1440), with_delta=False)
            out.setdefault(i, {})[w] = {k: r.get(k) for k in ("A", "A_star", "A_z", "A_excess", "A_star_z", "n")}
            L.log("P6", i, w, r.get("A_z"))
    return out


def main():
    a = sys.argv
    stage = a[a.index("--stage") + 1] if "--stage" in a else "all"
    RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    if stage in ("p1", "all"):
        (RES / "p1.json").write_text(json.dumps(p1(rng), indent=1, default=js))
    if stage in ("tests", "all"):
        (RES / "tests.json").write_text(json.dumps(tests(rng), indent=1, default=js))
    if stage in ("p6", "all"):
        t = json.loads((RES / "tests.json").read_text())
        ids = [r["id"] for r in t["memeplexes"] if r["P2"]["pass"]]
        (RES / "p6.json").write_text(json.dumps({"ids": ids, "res": p6(rng, ids)}, indent=1, default=js))


if __name__ == "__main__":
    main()
