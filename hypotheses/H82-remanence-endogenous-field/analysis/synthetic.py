"""H82 synthetic validation on the real boundaries: size of the placebo-corrected remanence test (S0), power for planted
remanence (S1, all agents, decaying with tau = 1 active day), veteran-only remanence (S2), and the newcomer contrast.
Planted vectors: v = Z_null @ alpha_hat (+ gamma(d) e_{P-1}^{(-i)}) + eps, with alpha_hat the regime's null fit
(exogenous + prior, no endogenous term) and eps drawn from that fit's real residual pool (permuted across agents and
days). alpha_hat and the residual pool are sampling facts; no remanence statistic is computed on real data here.

Output: data/processed/H82-remanence-endogenous-field/synthetic/synthetic_<model>.json, replicates_<model>.parquet
Usage: uv run python hypotheses/H82-remanence-endogenous-field/analysis/synthetic.py [--reps 200] [--model bge_small]
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
import h82lib as L  # noqa: E402


def null_fit(D, all_designs):
    """Per regime: alpha_hat on the non-e columns of the prev designs (days 1..5 pooled), residual pool."""
    fits = {}
    for regime in ("I", "III"):
        Ys, Zs = [], []
        for brow, des in all_designs:
            if brow["regime"] != regime:
                continue
            for item in des:
                if item is None:
                    continue
                Y, Z, names, *_ = item[1]["prev"]
                keep = [k for k, n in enumerate(names) if not n.startswith("e")]
                Ys.append(Y); Zs.append(Z[:, :, keep])
        Y = np.concatenate(Ys); Z = np.concatenate(Zs)
        Zf = Z.reshape(-1, Z.shape[2]); y = Y.reshape(-1)
        cols = np.abs(Zf).sum(0) > 0
        a = np.zeros(Z.shape[2]); a[cols] = np.linalg.lstsq(Zf[:, cols], y, rcond=None)[0]
        E = Y - np.einsum("nck,k->nc", Z, a)
        fits[regime] = (a, E)
    return fits


def make_ysub(D, fits, rng, gamma=0.0, tau=1.0, vets_only=False):
    cache = {}
    prev_of = {int(r["P"]): (int(r["prev"]), r["regime"]) for r in D.bd.iter_rows(named=True)}
    dayidx = {}
    for r in D.bd.iter_rows(named=True):
        for k, d in enumerate(r["days_P"]):
            dayidx[(int(r["P"]), d)] = k + 1

    def ysub(P, day, agents, Z, names):
        prev, regime = prev_of[P]
        a_hat, E = fits[regime]
        keep = [k for k, n in enumerate(names) if not n.startswith("e")]
        prev_agents = set(D.agent[(D.goal == prev) & (D.regime == regime)].tolist())
        out = np.empty((len(agents), 32))
        for j, ag in enumerate(agents):
            key = (P, day, int(ag))
            if key not in cache:
                v = Z[j][:, keep] @ a_hat + E[rng.integers(len(E))]
                if gamma > 0 and (not vets_only or ag in prev_agents):
                    e = D.centroid(prev, regime, leave_agent=int(ag))
                    v = v + gamma * np.exp(-(dayidx[(P, day)] - 1) / tau) * e
                cache[key] = v
            out[j] = cache[key]
        return out
    return ysub


def summarize(rows, split=False):
    df = pl.DataFrame(rows)
    res = {}
    for regime in ("I", "III", "all"):
        d = df if regime == "all" else df.filter(pl.col("regime") == regime)
        for term in (["e_vet", "e_new"] if split else ["e"]):
            dd = d.filter(pl.col("term") == term)
            d1 = dd.filter(pl.col("d") == 1)
            res[f"{regime}/{term}/mean_dg1"] = float(np.nanmean(d1["dgamma"].to_numpy())) if d1.height else np.nan
            res[f"{regime}/{term}/frac_pos_dg1"] = float(np.nanmean(d1["dgamma"].to_numpy() > 0)) if d1.height else np.nan
            res[f"{regime}/{term}/mean_dg_all"] = float(np.nanmean(dd["dgamma"].to_numpy())) if dd.height else np.nan
            res[f"{regime}/{term}/mean_asym1"] = float(np.nanmean(d1["asym"].to_numpy())) if d1.height else np.nan
            for dday in range(2, 6):
                x = dd.filter(pl.col("d") == dday)["dgamma"].to_numpy()
                res[f"{regime}/{term}/mean_dg{dday}"] = float(np.nanmean(x)) if len(x) else np.nan
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--reps", type=int, default=200); ap.add_argument("--model", default="bge_small")
    a = ap.parse_args()
    out = L.OUT / "synthetic"; out.mkdir(parents=True, exist_ok=True)
    D = L.Data(a.model)
    bds = list(D.bd.iter_rows(named=True))
    des = [(b, L.boundary_designs(D, b)) for b in bds]
    des_split = [(b, L.boundary_designs(D, b, newcomer_split=True)) for b in bds]
    fits = null_fit(D, des)
    scen = [("S0", dict(), a.reps), ("S1_0.05", dict(gamma=0.05), a.reps // 2), ("S1_0.1", dict(gamma=0.1), a.reps // 2),
            ("S1_0.2", dict(gamma=0.2), a.reps // 2), ("S2_0.1", dict(gamma=0.1, vets_only=True), a.reps // 2),
            ("S2_0.2", dict(gamma=0.2, vets_only=True), a.reps // 2)]
    rows = []
    for name, kw, n in scen:
        t0 = time.time()
        rng = np.random.default_rng(zlib.crc32(f"{a.model}|{name}".encode()))
        for r in range(n):
            ys = make_ysub(D, fits, rng, **kw)
            st = []
            for b, dd in des:
                st += L.boundary_stats(b, dd, n_boot=0, Ysub=ys)
            sp = []
            for b, dd in des_split:
                sp += L.boundary_stats(b, dd, n_boot=0, Ysub=ys)
            rows.append({"scenario": name, "rep": r, **summarize(st), **summarize(sp, split=True)})
        print(name, n, f"{time.time() - t0:.0f}s", flush=True)
    df = pl.DataFrame(rows)
    df.write_parquet(out / f"replicates_{a.model}.parquet")
    keys = [c for c in df.columns if "/" in c]
    s0 = df.filter(pl.col("scenario") == "S0")
    res = {"model": a.model, "alpha_hat": {r: fits[r][0].tolist() for r in fits},
           "S0_q95": {k: float(np.nanquantile(s0[k].to_numpy(), 0.95)) for k in keys},
           "S0_q05": {k: float(np.nanquantile(s0[k].to_numpy(), 0.05)) for k in keys},
           "scenarios": {}}
    for name in df["scenario"].unique(maintain_order=True).to_list():
        d = df.filter(pl.col("scenario") == name)
        res["scenarios"][name] = {"n": d.height,
                                  **{f"mean:{k}": float(np.nanmean(d[k].to_numpy())) for k in keys},
                                  **{f"sd:{k}": float(np.nanstd(d[k].to_numpy())) for k in keys},
                                  **{f"pass:{k}": float(np.nanmean(d[k].to_numpy() > res["S0_q95"][k])) for k in keys}}
    (out / f"synthetic_{a.model}.json").write_text(json.dumps(res, indent=1))
    for name in res["scenarios"]:
        sc = res["scenarios"][name]
        print(name, {k: round(sc[f"mean:{k}"], 3) for k in ("all/e/mean_dg1", "all/e/mean_asym1", "all/e_vet/mean_dg_all",
                                                         "all/e_new/mean_dg_all")},
              {k: round(sc[f"pass:{k}"], 2) for k in ("all/e/mean_dg1", "I/e/mean_dg1", "III/e/mean_dg1",
                                                       "all/e_new/mean_dg_all")})


if __name__ == "__main__":
    main()
