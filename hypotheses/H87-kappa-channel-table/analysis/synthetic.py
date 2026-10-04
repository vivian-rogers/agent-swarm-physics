"""H87 synthetic validation at real counts (axis F), run before any new-row outcome statistic.

Skeleton: the real NE41 F/P population (agents, strata, clusters, scramble flags, the real open flags of A, M, G, Q,
V_pre, pointers S_*). Replaced: X (allocation) and V (output).
  X: -1 w.p. 0.55; else A_prev w.p. 0.5, else a uniform draw from the agent's repo pool; at placebo events X = S_C
     w.p. 0.2 extra (the context holds allocation bits that the erasure removes).
  V ~ Poisson(exp(u_stratum - 0.5 scramble + 0.3 log1p V_pre + sum_c [log 1.3 open_c + b_c open_c scramble])),
     u_stratum ~ N(log 0.8, 0.5).
Worlds: W1 b_A = log 1.5, b_G = log 1.2, b_M = b_Q = 0 (artifact and chat have value; memory and search none);
        W0 (R2) all b_c = 0 (reading raises V x1.3 in both arms).
Checks: bias and 95% coverage of dV_rel per row; W0 size of any ordering claim P(kappa_i > kappa_j) >= 0.9 among
A, M, G; W1 power of P(kappa_A > kappa_M) >= 0.9; recovery of the context cost (1 - e^-0.5 = 0.39).
Output: data/processed/H87-kappa-channel-table/synthetic/synthetic.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h87lib as L  # noqa: E402

REPS, B = 25, 50


def synth(f0: dict, b: dict, rng) -> dict:
    f = dict(f0)
    n = len(f0["X"])
    ag = np.array([s.split("|")[0] for s in f0["stratum"]])
    pools = {a: np.unique(f0["S_A"][ag == a]) for a in np.unique(ag)}
    X = np.full(n, -1)
    has = rng.random(n) > 0.55
    own = rng.random(n) < 0.5
    for i in np.flatnonzero(has):
        X[i] = f0["S_A"][i] if own[i] else rng.choice(pools[ag[i]])
    ctx = (~f0["scramble"]) & has & (rng.random(n) < 0.2) & (f0["S_C"] >= 0)
    X[ctx] = f0["S_C"][ctx]
    stc = L.K._codes(f0["stratum"])
    u = rng.normal(np.log(0.8), 0.5, stc.max() + 1)[stc]
    sc = f0["scramble"].astype(float)
    lam = u - 0.5 * sc + 0.3 * np.log1p(f0["V_pre"])
    for c in ("A", "M", "G", "Q"):
        o = f0[f"open{c}"].astype(float)
        lam = lam + np.log(1.3) * o + b.get(c, 0.0) * o * sc
    f["X"] = X
    f["V"] = rng.poisson(np.exp(lam)).astype(float)
    f["V40"] = f["V"]
    return f


def main():
    ev = L.load()
    f0 = L.call_frame(ev)
    rng = np.random.default_rng(87)
    worlds = {"W1": {"A": np.log(1.5), "G": np.log(1.2)}, "W0": {}}
    out = {"reps": REPS, "B": B, "worlds": {}}
    for w, b in worlds.items():
        recs = []
        for r in range(REPS):
            t0 = time.time()
            f = synth(f0, b, rng)
            t = L.paired_table(f, B=B, n_perm=30, n_perm_boot=4, seed=r, rows=("A", "M", "G", "Q"), variants=False)
            rec = {c: {"rel": t["rows"][c]["dV_rel"], "rel_ci": t["rows"][c]["dV_rel_ci"], "I": t["rows"][c]["I"],
                       "I_ci": t["rows"][c]["I_ci"], "dV_ci": t["rows"][c]["dV_ci"],
                       "identified": bool(t["rows"][c]["I_ci"][0] is not None and t["rows"][c]["I_ci"][0] > L.MIN_I)}
                   for c in ("A", "M", "G", "Q", "C")}
            rec["paired"] = {k: t["paired"][k]["p"] for k in ("A>M", "M>A", "A>G", "G>A", "G>M", "M>G", "C>A", "A>C", "C>M", "M>C", "C>G", "G>C")}
            recs.append(rec)
            print(w, r, f"{time.time() - t0:.0f}s", {c: round(rec[c]["rel"], 3) for c in ("A", "M", "G", "C")},
                  rec["paired"], flush=True)
        summ = {}
        for c in ("A", "M", "G", "Q"):
            truth = float(np.exp(b.get(c, 0.0)) - 1)
            rel = np.array([x[c]["rel"] for x in recs])
            cov = np.mean([x[c]["rel_ci"][0] is not None and x[c]["rel_ci"][0] <= truth <= x[c]["rel_ci"][1]
                           for x in recs])
            summ[c] = {"truth_rel": truth, "mean_rel": float(np.nanmean(rel)), "bias": float(np.nanmean(rel) - truth),
                       "coverage": float(cov), "mean_I": float(np.mean([x[c]["I"] for x in recs]))}
        summ["C"] = {"truth_cost_rel": float(1 - np.exp(-0.5)),
                     "mean_cost_rel": float(np.mean([x["C"]["rel"] for x in recs])),
                     "mean_I": float(np.mean([x["C"]["I"] for x in recs]))}
        claims = ("A>M", "M>A", "A>G", "G>A", "G>M", "M>G")
        summ["any_claim_rate"] = float(np.mean([any((x["paired"][k] or 0) >= 0.9 for k in claims) for x in recs]))
        summ["claim_rate"] = {k: float(np.mean([(x["paired"][k] or 0) >= 0.9 for x in recs])) for k in claims}
        # amended rule (A1): ordering claims only between identified rows (I CI lower bound > MIN_I)
        def idclaims(x):
            return {k: (x["paired"][k] or 0) >= 0.9 for k in x["paired"]
                    if x[k.split(">")[0]]["identified"] and x[k.split(">")[1]]["identified"]}
        ic = [idclaims(x) for x in recs]
        keys = sorted({k for d in ic for k in d})
        summ["identified_rate"] = {c: float(np.mean([x[c]["identified"] for x in recs])) for c in ("A", "M", "G", "Q", "C")}
        summ["identified_claim_rate"] = {k: float(np.mean([d.get(k, False) for d in ic])) for k in keys}
        out["worlds"][w] = {"planted": {k: float(v) for k, v in b.items()}, "summary": summ, "reps_detail": recs}
    p = L.DATA / "synthetic"
    p.mkdir(parents=True, exist_ok=True)
    (p / "synthetic.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({w: out["worlds"][w]["summary"] for w in out["worlds"]}, indent=1, default=str))


if __name__ == "__main__":
    main()
