"""H81 round 2 synthetic validation (axis F) on the real panels, before any round-2 statistic on real data.

  --part r1   S0, S_ex (calendar OU drift, share 0.5, tau 28 d; no reading effect) and S_rec (planted record carriage,
              lam 0.5 / 1 / 2): C_R1, mediation M_R, M_U, D_adjg. Regime I (placebo U_act) and regime III (U_ledger, U_act).
  --part r2a  S0 and S_ex under the R2a projector (operator beyond centroid) and under placebo projectors: D_adjg
              calibration and the retention expected for a mode unrelated to operator directions.
  --part r2c  clock identifiability: OU planted on the calendar, documented-hours and goal-count clocks (share 0.5);
              which clock gets the lowest weighted SSE.
  --part r4   one OU mode (S_ex) through both pipelines (H81 block pairs, H82 boundary regression for every centroid):
              tau_81, tau_82, dtau, shared-tau LR, goal-jackknife z of dtau.
Scales (agent, goal, block covariances, residual noise) are sampling facts from the real projected vectors (round 1).
Output: data/processed/H81-culture-beyond-composition/round2/synthetic_<part>_<model>.json (+ replicate parquet)
Usage: uv run python hypotheses/H81-culture-beyond-composition/analysis/r2_synthetic.py --part r1 [--reps 100]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import zlib
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h81lib as L  # noqa: E402
import r2lib as Q  # noqa: E402


def seed(*a):
    return zlib.crc32("|".join(map(str, a)).encode())


def summarize(df: pl.DataFrame, keys, null="S_ex"):
    out = {}
    for sc in df["scenario"].unique().sort().to_list():
        d = df.filter(pl.col("scenario") == sc)
        out[sc] = {"n": d.height}
        for k in keys:
            x = d[k].to_numpy().astype(float)
            out[sc][k] = {"mean": float(np.nanmean(x)), "sd": float(np.nanstd(x)), "q05": float(np.nanquantile(x, 0.05)),
                          "q95": float(np.nanquantile(x, 0.95))}
    if null in out:
        for sc in out:
            d = df.filter(pl.col("scenario") == sc)
            for k in keys:
                thr = out[null][k]["q95"]
                out[sc][k]["pass_vs_" + null] = float(np.nanmean(d[k].to_numpy().astype(float) > thr))
    return out


# ----------------------------------------------------------------------------------------------------------- R1
def part_r1(model, reps):
    res, rows = {}, []
    for regime, placebos in (("I", ["U_act"]), ("III", ["U_ledger", "U_act"])):
        c = Q.load(model, regime)
        sc = L.variance_scales(c.pan, c.X)
        for plc in placebos:
            st = Q.r1_struct(c, plc)
            scen = [("S0", {}, reps), ("S_ex", {"share": 0.5}, 2 * reps)] + \
                   [(f"S_rec_{lam}", {"lam": lam}, reps) for lam in (0.5, 1.0, 2.0)]
            for name, kw, n in scen:
                t0 = time.time(); rng = np.random.default_rng(seed(model, regime, plc, name))
                for r in range(n):
                    if "lam" in kw:
                        Xs = Q.simulate_rec(c, sc, rng, st, kw["lam"])
                    else:
                        Xs = L.simulate(c.pan, sc, rng, share=kw.get("share", 0.0), tau=28.0)
                    o = Q.r1_stats(c, Xs, st)
                    rows.append({"regime": regime, "placebo": plc, "scenario": name, "rep": r,
                                 **{k: o[k] for k in ("C_R1", "M_R", "M_U", "M_diff", "D_adjg", "n_agent_blocks_both", "n_goals")}})
                print(model, regime, plc, name, n, f"{time.time() - t0:.0f}s", flush=True)
    df = pl.DataFrame(rows)
    df.write_parquet(Q.R2 / f"synthetic_r1_{model}.parquet")
    for regime in ("I", "III"):
        for plc in df.filter(pl.col("regime") == regime)["placebo"].unique().sort().to_list():
            d = df.filter((pl.col("regime") == regime) & (pl.col("placebo") == plc))
            res[f"{regime}/{plc}"] = summarize(d, ["C_R1", "M_R", "M_U", "M_diff", "D_adjg"])
            res[f"{regime}/{plc}"]["n_agent_blocks_both"] = int(d["n_agent_blocks_both"].median())
            res[f"{regime}/{plc}"]["n_goals"] = int(d["n_goals"].median())
    return res


# ----------------------------------------------------------------------------------------------------------- R2a
def part_r2a(model, reps):
    res = {}
    for regime in ("I", "III"):
        c0 = Q.load(model, regime)
        sc = L.variance_scales(c0.pan, c0.X)
        rng = np.random.default_rng(seed(model, regime, "r2a"))
        ex_real = Q.r2a_extra(c0)
        c_real = Q.load(model, regime, extra=ex_real)
        c_pl = [Q.load(model, regime, extra=Q.r2a_extra(c0, rng, placebo=True)) for _ in range(5)]
        out = {"n_extra_dirs_median": float(np.median([len(v) for v in ex_real.values()]))}
        for name, share, n in (("S0", 0.0, reps), ("S_ex", 0.5, reps)):
            vals = []
            for _ in range(n):
                Xs = L.simulate(c0.pan, sc, rng, share=share, tau=28.0)
                base = Q.slow(c0.pan, *Q.residuals(c0.pan, Xs)[:3], c0.kick)[0]["D_adjg"]
                real = Q.slow(c_real.pan, *Q.residuals(c_real.pan, Xs)[:3], c_real.kick)[0]["D_adjg"]
                cp = c_pl[rng.integers(len(c_pl))]
                plac = Q.slow(cp.pan, *Q.residuals(cp.pan, Xs)[:3], cp.kick)[0]["D_adjg"]
                vals.append((base, real, plac))
            v = np.array(vals)
            out[name] = {"D_base_mean": float(v[:, 0].mean()), "D_real_mean": float(v[:, 1].mean()),
                         "D_real_q95": float(np.quantile(v[:, 1], 0.95)), "D_plac_mean": float(v[:, 2].mean()),
                         "D_plac_q95": float(np.quantile(v[:, 2], 0.95)),
                         "retention_real": float(v[:, 1].mean() / v[:, 0].mean()) if name == "S_ex" else None,
                         "retention_plac": float(v[:, 2].mean() / v[:, 0].mean()) if name == "S_ex" else None}
            print(model, regime, name, json.dumps(out[name]), flush=True)
        res[regime] = out
    return res


# ----------------------------------------------------------------------------------------------------------- R2c
def part_r2c(model, reps):
    c = Q.load(model, "I")
    sc = L.variance_scales(c.pan, c.X)
    clocks = Q.block_clocks(c)
    scales = Q.clock_scales(c, clocks)
    res = {"scales": scales, "planted": {}}
    for planted in clocks:
        rng = np.random.default_rng(seed(model, "r2c", planted))
        best, taus, sses = [], [], []
        for _ in range(reps):
            Xs = Q.simulate_clock(c, sc, rng, 0.5, clocks[planted], scales[planted])
            o = Q.r2c_stats(c, Xs, clocks, scales)
            best.append(o["best"]); taus.append({k: o[k]["tau"] for k in clocks}); sses.append({k: o[k]["sse"] for k in clocks})
        pair = {f"{planted}>{k}": float(np.mean([s[planted] < s[k] for s in sses])) for k in clocks if k != planted}
        res["planted"][planted] = {"frac_best": {k: float(np.mean([b == k for b in best])) for k in clocks},
                                   "pairwise_accuracy": pair,
                                   "tau_median": {k: float(np.nanmedian([t[k] for t in taus])) for k in clocks}}
        print(model, "planted", planted, res["planted"][planted], flush=True)
    return res


# ----------------------------------------------------------------------------------------------------------- R4
def jackknife_dtau(T, block_goal, G, prev_of):
    goals = sorted(set(block_goal.tolist()))
    vals = []
    for g in goals:
        mT = (block_goal[T[:, 0].astype(int)] != g) & (block_goal[T[:, 1].astype(int)] != g)
        mG = (G[:, 0] != g) & (G[:, 2] != g) & (np.array([prev_of.get(int(p)) for p in G[:, 0]]) != g)
        f1 = Q.ou_fit(T[mT, 2], T[mT, 5], T[mT, 7], 28.0)
        f2 = Q.ou_fit(np.abs(G[mG, 3]), G[mG, 4], Q.h82_weights(G[mG]), 28.0)
        vals.append(f2["tau"] - f1["tau"])
    v = np.array(vals); v = v[np.isfinite(v)]; n = len(v)
    return float(np.sqrt((n - 1) / n * ((v - v.mean()) ** 2).sum())) if n > 2 else np.nan


def r4_once(c, arm, X, Xunit):
    A, B, R, _, _ = Q.residuals(c.pan, X)
    st, T, U, members, cen = Q.slow(c.pan, A, B, R, c.kick)
    arm.set_X(Xunit)
    G = arm.gammas()
    jf = Q.joint_fit(T[:, 2], T[:, 5], T[:, 7], np.abs(G[:, 3]), G[:, 4], Q.h82_weights(G))
    prev_of = {b["P"]: b["prev"] for b in arm.bd}
    se = jackknife_dtau(T, c.pan.block_goal, G, prev_of)
    return jf, se, T, G


def part_r4(model, reps):
    c = Q.load(model, "I")
    sc = L.variance_scales(c.pan, c.X)
    arm = Q.H82Arm(model, "I")
    rng = np.random.default_rng(seed(model, "r4"))
    rows = []
    for r in range(reps):
        t0 = time.time()
        Xs = L.simulate(c.pan, sc, rng, share=0.5, tau=28.0)
        Xu = Xs / np.linalg.norm(Xs, axis=1, keepdims=True)
        jf, se, _, _ = r4_once(c, arm, Xs, Xu)
        rows.append({"rep": r, "tau81": jf["sep81"]["tau"], "tau82": jf["sep82"]["tau"], "dtau": jf["dtau"],
                     "tau_joint": jf["joint"]["tau"], "LR": jf["joint"]["LR"], "se_jk": se,
                     "z": jf["dtau"] / se if se and np.isfinite(se) else np.nan,
                     "A81": jf["sep81"]["A"], "A82": jf["sep82"]["A"]})
        if r % 10 == 0:
            print(model, "r4 rep", r, {k: round(v, 3) for k, v in rows[-1].items()}, f"{time.time() - t0:.1f}s", flush=True)
    df = pl.DataFrame(rows); df.write_parquet(Q.R2 / f"synthetic_r4_{model}.parquet")
    q = lambda k, p: float(np.nanquantile(df[k].to_numpy(), p))  # noqa: E731
    return {"n": df.height, "tau81_median": q("tau81", 0.5), "tau82_median": q("tau82", 0.5),
            "dtau_q05": q("dtau", 0.05), "dtau_q95": q("dtau", 0.95), "dtau_median": q("dtau", 0.5),
            "LR_q95": q("LR", 0.95), "LR_median": q("LR", 0.5), "absz_gt_1.96": float(np.nanmean(np.abs(df["z"].to_numpy()) > 1.96)),
            "tau_joint_median": q("tau_joint", 0.5)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True, choices=["r1", "r2a", "r2c", "r4"])
    ap.add_argument("--reps", type=int, default=100)
    ap.add_argument("--models", default="bge_small,gte_modernbert")
    a = ap.parse_args()
    for m in a.models.split(","):
        t0 = time.time()
        res = {"r1": part_r1, "r2a": part_r2a, "r2c": part_r2c, "r4": part_r4}[a.part](m, a.reps)
        res["runtime_s"] = time.time() - t0
        (Q.R2 / f"synthetic_{a.part}_{m}.json").write_text(json.dumps(res, indent=1, default=float))
        print(json.dumps(res, indent=1, default=float)[:3000], flush=True)


if __name__ == "__main__":
    main()
