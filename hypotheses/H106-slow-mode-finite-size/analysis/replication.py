"""H106 replication on real data (non-holdout; regime I primary, regime III descriptive; both embedding models).

O3  finite-size exponent alpha_k (V1: 4-agent subsets, split-half disattenuated, active-day integrated rate),
    delete-one-goal jackknife CI; P1 pass / kill flags
O4  per-period points (N_G, rho_G, implied k)
O5  variants V2 (free amplitude), V3 (full roster), V4 (overlap-adjusted), V5 (scaffold-segment intercepts),
    V6 (N = eligible members), V7 (calendar days), V8 (without Gemini 2.5 Pro), V9 (white32, style_resid_period)
N1  NE27 two-rate contrast (also natives.py reads it) + two placebo breaks
Lag profile per N class (descriptive, axis B).
Output: data/processed/H106-slow-mode-finite-size/replication/{replication.json, periods.parquet, pairs_<model>.parquet}
Usage: uv run python hypotheses/H106-slow-mode-finite-size/analysis/replication.py [--draws 200]
"""
from __future__ import annotations

import argparse
import json
import sys
import zlib
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h106lib as L  # noqa: E402
from synthetic import ne27_spec, seg_bounds  # noqa: E402

MODELS = ["bge_small", "gte_modernbert"]


def flags(f):
    jk = f.get("jk", {})
    lo, hi = jk.get("lo", np.nan), jk.get("hi", np.nan)
    return {"pass_P1": bool(hi < 0 and lo <= -1 <= hi), "kill": bool(lo <= 0 <= hi and lo > -0.5),
            "excl0_pos": bool(lo > 0), "excl0_neg": bool(hi < 0)}


def clean(f):
    return {k: v for k, v in f.items() if k not in ("x",)}


def run_panel(model, variant, regime, rng, draws, drop=frozenset(), n_mode="active", time="active", variants=("V1",),
              ne27=False):
    ad, X, blocks = L.load(model, variant, regime, drop)
    P = L.projectors(model, regime, ad)
    pan = L.Panel(ad, blocks, P, n_mode=n_mode)
    if time == "calendar":
        pan.block_a = pan.block_mid.copy()
    grid = L.RateGrid(pan.block_a, pan.block_N)
    spec, plac = ne27_spec(pan) if ne27 else (None, ())
    out = L.pipeline(pan, X, rng, D=draws, variants=variants, grid=grid,
                     seg_bounds=seg_bounds() if "V5" in variants else None, restrict_ne27=spec, placebo_breaks=plac)
    return pan, out


def periods_table(pan, T, fitA, model, regime, max_lag=10.0):
    rows = []
    gb = pan.block_goal
    b0, b1 = T[:, 0].astype(int), T[:, 1].astype(int)
    lag = np.abs(T[:, 3] - T[:, 2])
    for g in np.unique(gb):
        m = ((gb[b0] == g) | (gb[b1] == g)) & (lag <= max_lag) & ~np.isnan(T[:, 7])
        NG = float(pan.block_N[gb == g].mean())
        if m.sum() == 0:
            rows.append({"model": model, "regime": regime, "goal_no": int(g), "N_G": NG, "rho": np.nan, "rho_se": np.nan,
                         "n_pairs": 0, "lag_mean": np.nan, "k_implied": np.nan})
            continue
        w = T[m, 9]; s = T[m, 7]
        rho = float((w * s).sum() / w.sum())
        se = float(np.std(s) / np.sqrt(m.sum())) if m.sum() > 1 else np.nan
        lm = float((w * lag[m]).sum() / w.sum())
        ratio = rho / fitA if fitA and fitA > 0 else np.nan
        k = float(-np.log(ratio) / lm) if ratio == ratio and 0 < ratio < 1 and lm > 0 else np.nan
        rows.append({"model": model, "regime": regime, "goal_no": int(g), "N_G": NG, "rho": rho, "rho_se": se,
                     "n_pairs": int(m.sum()), "lag_mean": lm, "k_implied": k,
                     "first_day": min(np.array(pan.block_first)[gb == g]), })
    return rows


def lag_profile(T, pan, edges=(0, 10, 20, 40, 80, 400)):
    out = {}
    Nb = pan.block_N
    cls = {"N<5": lambda b: Nb[b] < 5, "N 5.5-8": lambda b: (Nb[b] >= 5.5) & (Nb[b] < 8),
           "N>=8": lambda b: Nb[b] >= 8}
    b0, b1 = T[:, 0].astype(int), T[:, 1].astype(int)
    lag = np.abs(T[:, 3] - T[:, 2])
    for name, f in cls.items():
        m = f(b0) & f(b1) & ~np.isnan(T[:, 7])
        prof = []
        for lo, hi in zip(edges[:-1], edges[1:]):
            mm = m & (lag > lo) & (lag <= hi)
            prof.append([lo, hi, float((T[mm, 9] * T[mm, 7]).sum() / T[mm, 9].sum()) if mm.any() else None, int(mm.sum())])
        out[name] = prof
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=200)
    a = ap.parse_args()
    out = L.OUT / "replication"; out.mkdir(parents=True, exist_ok=True)
    res = {"primary": {}, "variants": {}, "regime_III": {}, "ne27": {}, "profile": {}}
    prow = []
    for model in MODELS:
        rng = np.random.default_rng(zlib.crc32(f"H106|{model}".encode()))
        pan, o = run_panel(model, "style_resid", "I", rng, a.draws, variants=("V1", "V2", "V3", "V4", "V5"), ne27=True)
        f = o["V1"]
        res["primary"][model] = {**clean(f), **flags(f), "reliability": o["reliability"], "tau6_active_days": 1 / f["k6"]}
        for v in ("V2", "V3", "V4", "V5"):
            res["variants"][f"{model}/{v}"] = clean(o[v])
        res["ne27"][model] = {"NE27": clean(o["NE27"]), "placebo": {k: clean(v) for k, v in o["NE27_placebo"].items()}}
        T = o["_T"]
        pl.DataFrame(T, schema=["b", "c", "t_b", "t_c", "N_b", "N_c", "s", "s_dis", "J", "w"], orient="row") \
            .write_parquet(out / f"pairs_{model}_I.parquet")
        prow += periods_table(pan, T, f["A"], model, "I")
        res["profile"][model] = lag_profile(T, pan)
        print(model, "V1", {k: round(f[k], 3) for k in ("alpha", "k6", "A", "s_inf")}, f["jk"]["lo"], f["jk"]["hi"],
              flush=True)
        # more variants, each with its own jackknife
        for name, kw in {"V6_members": dict(n_mode="members"), "V7_calendar": dict(time="calendar"),
                         "V8_no_gemini25": dict(drop=frozenset({L.GEMINI_25})), "V9_white32": dict(variant="white32"),
                         "V9_style_resid_period": dict(variant="style_resid_period")}.items():
            rng2 = np.random.default_rng(zlib.crc32(f"H106|{model}|{name}".encode()))
            _, o2 = run_panel(model, kw.pop("variant", "style_resid"), "I", rng2, a.draws, **kw)
            res["variants"][f"{model}/{name}"] = {**clean(o2["V1"]), **flags(o2["V1"])}
            print("  ", name, round(o2["V1"]["alpha"], 3), o2["V1"]["jk"]["lo"], o2["V1"]["jk"]["hi"], flush=True)
        # regime III, descriptive
        rng3 = np.random.default_rng(zlib.crc32(f"H106|{model}|III".encode()))
        pan3, o3 = run_panel(model, "style_resid", "III", rng3, a.draws)
        res["regime_III"][model] = {**clean(o3["V1"]), **flags(o3["V1"]), "reliability": o3["reliability"]}
        prow += periods_table(pan3, o3["_T"], o3["V1"]["A"], model, "III")
        print(model, "III", round(o3["V1"]["alpha"], 3), o3["V1"]["jk"]["lo"], o3["V1"]["jk"]["hi"], flush=True)
    pl.DataFrame(prow).write_parquet(out / "periods.parquet")
    # Amendment A3: percentiles of the real estimate in the synthetic D and M worlds, and the likelihood ratio
    syn = pl.read_parquet(L.OUT / "synthetic/replicates.parquet")
    res["evidence"] = {}
    for model in MODELS:
        for col, real in (("alpha", res["primary"][model]["alpha"]), ("ne27_dlnk", res["ne27"][model]["NE27"].get("dlnk"))):
            d = {}
            for w in ("D", "M", "H", "DR3", "DR5"):
                x = syn.filter((pl.col("model") == model) & (pl.col("regime") == "I") & (pl.col("world") == w))[col].to_numpy()
                x = x[~np.isnan(x)]
                bw = 1.06 * x.std() * len(x) ** -0.2
                d[w] = {"pct": float((x < real).mean()), "density": float(np.mean(np.exp(-0.5 * ((real - x) / bw) ** 2))
                                                                        / (bw * np.sqrt(2 * np.pi)))}
            d["LR_M_over_D"] = d["M"]["density"] / d["D"]["density"] if d["D"]["density"] > 0 else None
            d["real"] = real
            res["evidence"][f"{model}/{col}"] = d
    (out / "replication.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: res[k] for k in ("primary", "ne27")}, indent=1, default=float))


if __name__ == "__main__":
    main()
