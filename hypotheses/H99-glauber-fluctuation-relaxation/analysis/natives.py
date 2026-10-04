"""H99 period-native tests (layer 2); predictions are in each folder's README, written before running.

  ne42  #39 -> #40 -> #41: talk g_chi and g_tau (lag 1) and the A2 call per unit; differences #40 - #39 and #40 - #41
        with CIs from independent 1-h block bootstraps of each unit.
  ne14  #36a (regime II) -> #36b, #36c (regime III): talk drho1, drho2, g_chi per unit.
  g51   H04 round-1b kernels read as data (data/processed/H04-reversible-forcing/r1b/G51.json): the read-out-aligned
        nudge-target activity kernel G(l) (per minute after the receiving call), its geometric decay ratio over lags
        0..5 (as h99lib.geom_ratio) against the #51 activity transverse rho_perp(1) and the Glauber collective
        prediction rho_perp^(1-g_chi); the bystander/target A30 ratio against g_chi / (N (1 - g_chi)). H59's shared
        call-lag kernel is quoted for its per-call decay.
Usage: uv run python hypotheses/H99-glauber-fluctuation-relaxation/analysis/natives.py
"""
from __future__ import annotations

import json
import sys
import zlib
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h99lib as L  # noqa: E402
import run as R  # noqa: E402

ROOT = HERE.parents[2]
BASE = ROOT / "data/processed/H99-glauber-fluctuation-relaxation"
OUT = BASE / "natives"


def unit_draws(unit, chan="talk", B=400, seed=0):
    g = R.load_grid(unit)
    rows = L.binary_sums(g["talk"] if chan == "talk" else g["act"], g["keep"])
    rng = np.random.default_rng(zlib.crc32(f"{unit}|{seed}".encode()))
    d = []
    for _ in range(B):
        e = L.estimates(rows[rng.integers(0, len(rows), len(rows))].sum(0))
        d.append((e["g_chi"], e["g_tau"], e["drho1"]))
    return np.array(d, float), L.estimates(rows.sum(0))


def diff_ci(a, b):
    n = min(len(a), len(b))
    d = a[:n] - b[:n]
    d = d[np.isfinite(d)]
    return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))] if len(d) > 50 else [None, None]


def ne42():
    U = pl.read_parquet(BASE / "results" / "units_called.parquet").filter((pl.col("variant") == "main") & (pl.col("channel") == "talk"))
    out = {"units": {}}
    dr = {}
    for u in ("39", "40", "41"):
        r = U.filter(pl.col("unit") == u).to_dicts()[0]
        out["units"][u] = {k: r[k] for k in ("g_chi", "g_chi_lo", "g_chi_hi", "g_tau", "g_tau_lo", "g_tau_hi", "drho1", "drho1_lo",
                                             "drho1_hi", "drho2", "rho_c1", "rho_p1", "call", "n_min")}
        dr[u] = unit_draws(u)[0]
    for k, j in (("g_chi", 0), ("g_tau", 1), ("drho1", 2)):
        for o in ("39", "41"):
            out[f"{k}_40_minus_{o}"] = {"est": out["units"]["40"][k] - out["units"][o][k], "ci": diff_ci(dr["40"][:, j], dr[o][:, j])}
    return out


def ne14():
    U = pl.read_parquet(BASE / "results" / "units_called.parquet").filter((pl.col("variant") == "main") & (pl.col("channel") == "talk"))
    return {u: {k: r[k] for k in ("g_chi", "g_chi_lo", "g_chi_hi", "drho1", "drho1_lo", "drho1_hi", "drho2", "drho2_lo", "drho2_hi",
                                  "rho_c1", "rho_p1", "call", "n_min")}
            for u in ("36a", "36b", "36c") for r in U.filter(pl.col("unit") == u).to_dicts()}


def g51():
    U = pl.read_parquet(BASE / "results" / "units_called.parquet").filter((pl.col("variant") == "main") & (pl.col("goal_no") == 51))
    act = U.filter(pl.col("channel") == "act")
    talk = U.filter(pl.col("channel") == "talk")
    p_rho = L.re_pool(act["rho_p1"].to_numpy(), ((act["rho_p1_hi"] - act["rho_p1_lo"]) / 3.92).to_numpy()) if "rho_p1_hi" in act.columns else None
    w = act["n_min"].to_numpy()
    rho_p = float((w * act["rho_p1"].to_numpy()).sum() / w.sum())
    g_act = L.re_pool(act["g_chi"].to_numpy(), act["g_chi_se"].to_numpy())
    N = float(np.median(act["N_med"].to_numpy()))
    h04 = json.loads((ROOT / "data/processed/H04-reversible-forcing/r1b/G51.json").read_text())["G"]
    res = {"rho_perp_act_pooled": rho_p, "g_chi_act_pooled": g_act, "N_median": N}
    for key in ("nudge_target_readout_aligned", "nudge_target_all", "nudge_target_first"):
        G = np.array(h04[key]["G"], float)
        lo = np.array(h04[key]["G_lo"], float)
        hi = np.array(h04[key]["G_hi"], float)
        p = int(np.argmax(G[:10]))
        lam = L.geom_ratio(G[p:])
        lam_lo = L.geom_ratio(lo[p:])
        lam_hi = L.geom_ratio(hi[p:])
        # integrated response after the peak relative to the peak (mean-delay proxy), first 10 min
        res[key] = {"peak_lag": p, "G_first12": [round(x, 4) for x in G[:12]], "lam_kernel": lam,
                    "lam_kernel_from_bounds": [lam_lo, lam_hi], "A30": h04[key]["A30"], "relax_1e_h04": h04[key].get("relax_1e"),
                    "t50_h04": h04[key].get("t50"), "n_cells": h04[key]["n_cells"]}
    gc = g_act["mean"]
    res["lam_pred_transverse"] = rho_p
    res["lam_pred_collective"] = rho_p ** (1 - gc)
    tgt = h04["nudge_target_all"]["A30"]
    by = h04["nudge_bystander"]["A30"]
    res["bystander_target_ratio"] = by[0] / tgt[0] if tgt[0] else None
    res["bystander_A30"] = by
    res["target_A30"] = tgt
    res["meanfield_ratio_pred"] = gc / (N * (1 - gc))
    h59 = json.loads((ROOT / "data/processed/H59-one-lever-model/G51/results.json").read_text())
    res["h59_shared_call_kernel"] = h59["triples"]["K"]
    res["talk_units"] = talk.select("unit", "g_chi", "g_chi_lo", "drho1", "drho1_lo", "drho1_hi", "call").to_dicts()
    res["talk_calls"] = dict(zip(*np.unique(talk["call"].to_list(), return_counts=True)))
    res["talk_calls"] = {k: int(v) for k, v in res["talk_calls"].items()}
    return res


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    allr = {"ne42": ne42(), "ne14": ne14(), "g51": g51()}
    for k, v in allr.items():
        (OUT / f"{k}.json").write_text(json.dumps(v, indent=1, default=float))
    print(json.dumps(allr, indent=1, default=float))


if __name__ == "__main__":
    main()
