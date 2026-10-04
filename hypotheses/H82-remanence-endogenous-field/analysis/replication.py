"""H82 replication: remanence regression at every eligible goal boundary (non-holdout; both embedding models).

O1/O2 gamma and the placebo-corrected excess Delta gamma per boundary and day (agent-cluster bootstrap, 300 draws)
O3    time asymmetry A = gamma[P-1] - gamma[P+1]
O4    decay over days 1..5 (RE means), tau_R
O5    newcomers vs veterans (newcomer split)
O6    robustness: white32, style_resid_period, no human direction, wider prior gap (also leaving out P-2 and P+1),
      co-present agents' prior (R4)
Card-level: DerSimonian-Laird RE over boundaries (per regime and all), the unweighted mean against the synthetic S0
95th percentile, sign counts.

Output: data/processed/H82-remanence-endogenous-field/replication/ (boundary_rows.parquet, replication.json)
Usage: uv run python hypotheses/H82-remanence-endogenous-field/analysis/replication.py [--boot 300]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.optimize import curve_fit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h82lib as L  # noqa: E402

MODELS = ["bge_small", "gte_modernbert"]


def run(D, boot, rng, split=False, extra=False, mates=False):
    rows = []
    for b in D.bd.iter_rows(named=True):
        ex = (b["P"] - 2, b["P"] + 1) if extra else ()
        des = L.boundary_designs(D, b, newcomer_split=split, extra_prior_leave=ex, mates=mates)
        rows += L.boundary_stats(b, des, n_boot=boot, rng=rng)
    return pl.DataFrame(rows)


def card(df: pl.DataFrame, term="e", syn=None, model=None) -> dict:
    out = {}
    for scope in ("I", "III", "all"):
        d = df.filter(pl.col("term") == term)
        if scope != "all":
            d = d.filter(pl.col("regime") == scope)
        d1 = d.filter(pl.col("d") == 1)
        if d1.height == 0:
            continue
        re1 = L.re_meta(d1["dgamma"].to_numpy(), d1["dgamma_se"].to_numpy())
        rea = L.re_meta(d1["asym"].to_numpy(), d1["asym_se"].to_numpy())
        prof = {}
        for dd in range(1, 6):
            x = d.filter(pl.col("d") == dd)
            if x.height:
                prof[dd] = L.re_meta(x["dgamma"].to_numpy(), x["dgamma_se"].to_numpy())
        o = {"k": d1.height, "re_dgamma_d1": re1, "re_asym_d1": rea,
             "mean_dgamma_d1": float(np.nanmean(d1["dgamma"].to_numpy())),
             "frac_pos_d1": float(np.nanmean(d1["dgamma"].to_numpy() > 0)),
             "n_ci_above0_d1": int((d1["dgamma_lo"] > 0).sum()),
             "mean_gamma_prev_d1": float(np.nanmean(d1["gamma_prev"].to_numpy())),
             "mean_gamma_placebo_d1": float(np.nanmean(d1["gamma_placebo_med"].to_numpy())),
             "mean_gamma_next_d1": float(np.nanmean(d1["gamma_next"].to_numpy())),
             "mean_dgamma_all_days": float(np.nanmean(d["dgamma"].to_numpy())),
             "re_profile": prof}
        if syn is not None:
            key = f"{scope}/{term}/mean_dg1"
            if key in syn["S0_q95"]:
                o["S0_q95_mean_dg1"] = syn["S0_q95"][key]
                o["pass_vs_S0"] = bool(o["mean_dgamma_d1"] > syn["S0_q95"][key])
            key2 = f"{scope}/{term}/mean_dg_all"
            if key2 in syn["S0_q95"]:
                o["S0_q95_mean_dg_all"] = syn["S0_q95"][key2]
        # decay fit on RE means
        ds = np.array([k for k in prof if np.isfinite(prof[k]["mu"])]); ys = np.array([prof[k]["mu"] for k in ds])
        if len(ds) >= 3 and ys[0] > 0:
            try:
                p, cov = curve_fit(lambda t, a, tau: a * np.exp(-(t - 1) / tau), ds, ys, p0=(ys[0], 1.0),
                                   bounds=([-1, 0.05], [1, 50]))
                o["tau_R_days"] = float(p[1])
            except Exception:  # noqa: BLE001
                o["tau_R_days"] = None
        out[scope] = o
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--boot", type=int, default=300)
    a = ap.parse_args()
    out = L.OUT / "replication"; out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(82)
    res = {"primary": {}, "newcomers": {}, "robustness": {}}
    allrows = []
    for model in MODELS:
        syn = json.loads((L.OUT / "synthetic" / f"synthetic_{model}.json").read_text())
        D = L.Data(model)
        df = run(D, a.boot, rng)
        allrows.append(df.with_columns(pl.lit(model).alias("model"), pl.lit("primary").alias("config")))
        res["primary"][model] = card(df, "e", syn, model)
        dfs = run(D, a.boot, rng, split=True)
        allrows.append(dfs.with_columns(pl.lit(model).alias("model"), pl.lit("newcomer_split").alias("config")))
        res["newcomers"][model] = {"vet": card(dfs, "e_vet", syn), "new": card(dfs, "e_new", syn),
                                   "boundaries_with_newcomers": sorted(set(dfs.filter((pl.col("term") == "e_new")
                                                                                      & (pl.col("n_group") > 0))["P"].to_list()))}
        print(model, "primary all", {k: res["primary"][model]["all"][k] for k in ("mean_dgamma_d1", "frac_pos_d1")},
              res["primary"][model]["all"]["re_dgamma_d1"], flush=True)
        for name, kw in {"white32": dict(variant="white32"), "style_resid_period": dict(variant="style_resid_period"),
                         "no_human_dir": dict(use_human=False), "wider_prior_gap": dict(extra=True),
                         "copresent_prior": dict(mates=True), "no_gemini25": dict(drop=frozenset({6}))}.items():
            D2 = L.Data(model, kw.get("variant", "style_resid"), kw.get("drop", frozenset()), kw.get("use_human", True))
            d2 = run(D2, 100, rng, extra=kw.get("extra", False), mates=kw.get("mates", False))
            allrows.append(d2.with_columns(pl.lit(model).alias("model"), pl.lit(name).alias("config")))
            res["robustness"][f"{model}/{name}"] = card(d2, "e", syn)
            print("  ", name, res["robustness"][f"{model}/{name}"]["all"]["re_dgamma_d1"], flush=True)
    pl.concat(allrows, how="diagonal_relaxed").write_parquet(out / "boundary_rows.parquet")
    (out / "replication.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
