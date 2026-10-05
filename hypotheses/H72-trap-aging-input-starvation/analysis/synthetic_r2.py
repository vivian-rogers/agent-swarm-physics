"""H72 round 2 synthetic validation on the real wake skeletons (axis F). Run before any round-2 outcome statistic.

Outcomes are simulated sequentially within traps (stop at the first escape, censor at the real trap end; H16 round 2).
Agent intercepts SD 0.5; covariates centred at their medians so the mean escape is near 0.5. No real outcome is read.
Worlds (card, "Round 2", Nulls and validation plan):
  W0 null; W1a intrinsic -0.6 ln k; W1b intrinsic -1.2 ln k; W1c intrinsic -0.5 ln a; W2 urn +1.0 ln(1 - f_call);
  W3 chatter -0.25 ln(1 + U5); W4 starvation -0.4 ln s_dir; W5 per-trap frailty SD 1.5; W6 W1(-0.3 ln k) + W2 + W3;
  W7 W3 + 0.25 ln(1 + U5) x directed read at the wake.
Parts: --part main (G51, G38: all R1 and reconcile statistics), --part power (W3 power for beta_C on every period).
Output: data/processed/H72-trap-aging-input-starvation/r2/synthetic/{main,power}.json
Usage: uv run python hypotheses/H72-trap-aging-input-starvation/analysis/synthetic_r2.py --part main --reps 20
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as R  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

OUT = R.R2 / "synthetic"
WORLDS = ("W0", "W1a", "W1b", "W1c", "W2", "W3", "W4", "W5", "W6", "W7")
CV_WORLDS = ("W0", "W1a", "W1b", "W1c", "W2", "W3", "W4", "W5", "W6")


def cen(x):
    return x - np.median(x)


def world_eta(name, P, rng):
    ua = np.unique(P["agent"])
    al = dict(zip(ua, 0.5 * rng.standard_normal(len(ua))))
    eta = np.array([al[a] for a in P["agent"]])
    lk, la = cen(P["A"]["ln_k"]), cen(P["A"]["ln_a"])
    lu = cen(P["C"]["ln_dose"])
    lq = cen(P["F"]["lnq"]) if P["F"] else 0.0
    ls = cen(P["S"]["ln_s"])
    if name == "W1a":
        eta = eta - 0.6 * lk
    elif name == "W1b":
        eta = eta - 1.2 * lk
    elif name == "W1c":
        eta = eta - 0.5 * la
    elif name == "W2":
        eta = eta + 1.0 * lq
    elif name == "W3":
        eta = eta - 0.25 * lu
    elif name == "W4":
        eta = eta - 0.4 * ls
    elif name == "W5":
        z = 1.5 * rng.standard_normal(P["trap"].max() + 1)
        eta = eta + z[P["trap"]]
    elif name == "W6":
        eta = eta - 0.3 * lk + 1.0 * lq - 0.25 * lu
    elif name == "W7":
        eta = eta - 0.25 * lu + 0.25 * P["C"]["ln_dose"] * P["dir_wake"]
    return eta


def day_dummies(P):
    d = P["day"]
    lev = np.unique(d)
    return {f"day_{int(x)}": (d == x).astype(float) for x in lev[1:]}


def r1_stats(P, y, full_fam):
    """R1 statistics on outcome y (rows of P). Values: (estimate, Wald SE)."""
    o = {}
    f1 = R.fit(P, "B+A+C", y=y)
    o["bC"] = R.b(f1, "ln_dose")
    f2 = R.fit(P, full_fam, y=y)
    o["bC_full"] = R.b(f2, "ln_dose")
    k1 = P["k"] == 1
    if k1.sum() > 200:
        Q = R.subset(P, k1)
        f3 = R.fit(Q, "B+A+C", y=y[k1])
        o["bC_k1"] = R.b(f3, "ln_dose")
        f3b = R.fit(Q, full_fam, y=y[k1])
        o["bC_k1_full"] = R.b(f3b, "ln_dose")
    f4 = R.fit(P, full_fam, y=y, extra=day_dummies(P))
    o["bC_dayfe"] = R.b(f4, "ln_dose")
    f5 = R.fit(P, "B+A+C", y=y, extra={"int": P["C"]["ln_dose"] * P["dir_wake"]})
    o["b_int"] = R.b(f5, "int")
    f5b = R.fit(P, full_fam, y=y, extra={"int": P["C"]["ln_dose"] * P["dir_wake"]})
    o["b_int_full"] = R.b(f5b, "int")
    m = np.isfinite(P["ln_rate"])
    Q = R.subset(P, m)
    f6 = R.fit(Q, "B+A", y=y[m], extra={"ln_rate": Q["ln_rate"]})
    o["b_rate"] = R.b(f6, "ln_rate")
    fa = R.fit(P, "B+A", y=y)
    o["b_k"] = R.b(fa, "ln_k"); o["b_a"] = R.b(fa, "ln_a")
    return o


def run_main(reps):
    rng = np.random.default_rng(R.SEED + 11)
    res = {}
    for goal, nrep in ((51, reps), (38, reps * 2)):
        P0 = R.prep(R.load_wakes(goal))
        st, en = R.trap_index(P0)
        full = "B+S+C+F+A" if P0["F"] else "B+S+C+A"
        res[f"G{goal}"] = {"n_rows": P0["n"]}
        for w in WORLDS:
            rows, cvs = [], []
            t0 = time.time()
            for r in range(nrep):
                p = 1 / (1 + np.exp(-world_eta(w, P0, rng)))
                keep, y = R.simulate_traps(rng, p, st, en)
                P = R.subset(P0, keep)
                yk = y[keep].astype(float)
                try:
                    rows.append(R1_flat(r1_stats(P, yk, full)))
                    if w in CV_WORLDS and (goal == 51 or r < reps):
                        per = R.cv_per_day(P, y=yk)
                        cvs.append(R.cv_stats(per, P["n"], B=300, seed=r))
                except Exception as e:  # noqa: BLE001
                    print("fail", goal, w, e, flush=True)
            res[f"G{goal}"][w] = {"r1": summarize(rows), "cv": summarize_cv(cvs), "reps": len(rows)}
            s = res[f"G{goal}"][w]
            print(f"G{goal} {w} {len(rows)} reps {time.time() - t0:.0f}s bC {s['r1'].get('bC')} "
                  f"eps {{{', '.join(f'{k}: {v}' for k, v in s['cv'].items() if k.startswith('eps'))}}}", flush=True)
            R.jdump(res, OUT / "main.json")
    return res


def R1_flat(o):
    return {k: v for k, v in o.items()}


def summarize(rows):
    out = {}
    if not rows:
        return out
    keys = set().union(*[r.keys() for r in rows])
    for k in sorted(keys):
        v = np.array([r[k][0] for r in rows if k in r], float)
        se = np.array([r[k][1] for r in rows if k in r], float)
        z = v / se
        out[k] = {"mean": round(float(np.nanmean(v)), 3), "sd": round(float(np.nanstd(v)), 3),
                  "rej_neg": round(float(np.nanmean(z < -1.96)), 3), "rej_pos": round(float(np.nanmean(z > 1.96)), 3),
                  "n": int(np.isfinite(v).sum())}
    return out


def summarize_cv(cvs):
    out = {}
    if not cvs:
        return out
    for k in cvs[0]:
        v = np.array([c[k][0] for c in cvs], float)
        lo = np.array([c[k][1] for c in cvs], float)
        hi = np.array([c[k][2] for c in cvs], float)
        out[k] = {"mean": round(float(np.nanmean(v)), 3), "p2.5": round(float(np.nanpercentile(v, 2.5)), 3),
                  "p97.5": round(float(np.nanpercentile(v, 97.5)), 3), "ci_above0": round(float(np.mean(lo > 0)), 3),
                  "ci_below0": round(float(np.mean(hi < 0)), 3)}
    # hit rate: which mechanism has the largest eps
    E = np.array([[c.get(f"eps_{m}", [np.nan])[0] for m in ("S", "C", "F")] for c in cvs], float)
    if np.isfinite(E).any():
        win = np.nanargmax(np.where(np.isfinite(E), E, -np.inf), axis=1)
        out["largest_eps_share"] = {m: round(float(np.mean(win == i)), 3) for i, m in enumerate(("S", "C", "F"))}
    return out


def run_power(reps):
    rng = np.random.default_rng(R.SEED + 12)
    g = pl.read_parquet(R.R2 / "wakes_r2.parquet")
    goals = sorted(g["goal_no"].unique().to_list())
    res = {}
    for goal in goals:
        P0 = R.prep(R.load_wakes(goal))
        st, en = R.trap_index(P0)
        fam = "B+A+C+F" if P0["F"] else "B+A+C"
        nr = reps if goal != 51 else max(reps // 2, 10)
        rej, est, size = [], [], []
        t0 = time.time()
        for w, store in (("W3", rej), ("W0", size)):
            for _ in range(nr):
                p = 1 / (1 + np.exp(-world_eta(w, P0, rng)))
                keep, y = R.simulate_traps(rng, p, st, en)
                P = R.subset(P0, keep)
                yk = y[keep].astype(float)
                if yk.sum() < R.MIN_EVENTS or (len(yk) - yk.sum()) < R.MIN_EVENTS:
                    store.append(np.nan)
                    continue
                try:
                    f = R.fit(P, fam, y=yk)
                    bb, se = R.b(f, "ln_dose")
                    store.append(bb / se)
                    if w == "W3":
                        est.append(bb)
                except Exception:  # noqa: BLE001
                    store.append(np.nan)
        rej_a, size_a = np.array(rej, float), np.array(size, float)
        res[f"G{goal:02d}"] = {"n_rows": P0["n"], "power_bC_-0.25": float(np.nanmean(rej_a < -1.96)) if np.isfinite(rej_a).any() else None,
                               "size_bC": float(np.nanmean(np.abs(size_a) > 1.96)) if np.isfinite(size_a).any() else None,
                               "mean_bC_W3": float(np.nanmean(est)) if est else None, "reps": nr,
                               "sd_ln_dose": float(np.std(P0["C"]["ln_dose"]))}
        print(f"G{goal:02d}", res[f"G{goal:02d}"], f"{time.time() - t0:.0f}s", flush=True)
        R.jdump(res, OUT / "power.json")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", default="main")
    ap.add_argument("--reps", type=int, default=20)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.part == "main":
        run_main(a.reps)
    elif a.part == "power":
        run_power(a.reps)
    elif a.part == "time":
        P0 = R.prep(R.load_wakes(51))
        st, en = R.trap_index(P0)
        rng = np.random.default_rng(1)
        p = 1 / (1 + np.exp(-world_eta("W3", P0, rng)))
        keep, y = R.simulate_traps(rng, p, st, en)
        P = R.subset(P0, keep)
        t0 = time.time(); f = R.fit(P, "B+S+C+F+A", y=y[keep].astype(float)); print("one fit", time.time() - t0, R.b(f, "ln_dose"), f["converged"], P["n"])
        t0 = time.time(); per = R.cv_per_day(P, y=y[keep].astype(float)); print("cv", time.time() - t0)
        print(R.cv_stats(per, P["n"], B=300))


if __name__ == "__main__":
    main()
