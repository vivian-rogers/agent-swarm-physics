"""H141 round 1: apply every registered prediction and kill rule (as operationalized in the card's Round 1 section),
write results/summary.json and the per_period_estimates rows.

    uv run python hypotheses/H141-easy-plane-anisotropy/analysis/summarize.py [--no-estimates]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import pickle  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "infra/shared"))
import h141lib as L  # noqa: E402
import kick as K  # noqa: E402

RES = L.DATA / "results"
LN3 = np.log(3.0)


def f(x):
    return None if x is None or (isinstance(x, float) and not np.isfinite(x)) else float(x)


def pool(rows, key="rho", se="se_ln"):
    est = np.array([np.log(r[key]) if r.get(key) and r[key] > 0 and np.isfinite(r[key]) else np.nan for r in rows])
    s = np.array([r.get(se, np.nan) if r.get(se) is not None else np.nan for r in rows], float)
    mu, smu, t2, i2, k = L.dl_pool(est, s)
    if k == 0:
        return {"k": 0}
    return {"k": k, "ln_mu": mu, "se": smu, "rho": float(np.exp(mu)), "ci90": [float(np.exp(mu - 1.645 * smu)),
            float(np.exp(mu + 1.645 * smu))], "ci95": [float(np.exp(mu - 1.96 * smu)), float(np.exp(mu + 1.96 * smu))],
            "tau2": t2, "I2": i2}


def kill_flags(p):
    if p.get("k", 0) == 0:
        return {}
    lo, hi = p["ci90"]
    return {"P1_pass": bool(p["rho"] >= 10 and lo >= 3), "kill": bool(lo >= 1 / 3 and hi <= 3),
            "reverse_kill": bool(p["rho"] < 1 / 3 and hi < 1)}


def variant_summary(full: dict, model: str, variant: str) -> dict:
    rows = [r for k, r in full.items() if k.startswith(f"{model}|{variant}|")]
    rows = sorted(rows, key=lambda r: (r["goal"], r["unit"]))
    test = [r for r in rows if r["testable"]]
    out = {"n_units": len(rows), "n_testable": len(test)}
    out["pool_all"] = pool(rows)
    out["pool_all"].update(kill_flags(out["pool_all"]))
    out["pool_shared"] = pool([r for r in rows if r["goal"] != 51])
    out["pool_51"] = pool([r for r in rows if r["goal"] == 51])
    out["pool_raw"] = pool(rows, "raw_rho", "raw_se_ln")
    out["pool_pca"] = pool(rows, "pca_rho", "pca_se_ln")
    out["pool_khat"] = pool(rows, "khat_rho", "khat_se_ln")
    if any("own_rho" in r for r in rows):
        out["pool_own"] = pool([r for r in rows if r["goal"] == 51], "own_rho", "own_se_ln")
    # P2 random-plane percentile
    pct = np.array([r["rand_pct"] for r in test], float)
    out["P2_frac_above95"] = float(np.nanmean(pct > 0.95)) if len(pct) else None
    out["P2_n"] = int(np.isfinite(pct).sum())
    # P3 fluctuation-dissipation (lag-0 V_A, registered) and the lag-1 variant
    ratio = np.array([r["V_A"] / r["rho"] for r in test], float)
    out["P3_frac_within2"] = float(np.nanmean((ratio >= 0.5) & (ratio <= 2)))
    ratio1 = np.array([r["V_A_lag1"] / r["rho"] for r in test], float)
    out["P3_lag1_frac_within2"] = float(np.nanmean((ratio1 >= 0.5) & (ratio1 <= 2)))
    out["V_A_median"] = float(np.nanmedian([r["V_A"] for r in test]))
    out["V_A_lag1_median"] = float(np.nanmedian([r["V_A_lag1"] for r in test]))
    out["V_A_rand_pct_median"] = float(np.nanmedian([r["rand_V_pct"] for r in test]))
    # P5 day scale
    for tag in ("", "cen_", "vg_", "vgcen_"):
        ok = [r for r in test if r.get(f"{tag}P_diff") is not None and np.isfinite(r.get(f"{tag}P_diff", np.nan))]
        if ok:
            lo = np.array([json.loads(r[f"{tag}P_diff_ci95"])[0] if isinstance(r[f"{tag}P_diff_ci95"], str)
                           else r[f"{tag}P_diff_ci95"][0] for r in ok])
            hi = np.array([json.loads(r[f"{tag}P_diff_ci95"])[1] if isinstance(r[f"{tag}P_diff_ci95"], str)
                           else r[f"{tag}P_diff_ci95"][1] for r in ok])
            d = np.array([r[f"{tag}P_diff"] for r in ok])
            out[f"{tag}P5_n"] = len(ok)
            out[f"{tag}P5_frac_pos_sig"] = float(np.mean(lo > 0))
            out[f"{tag}P5_frac_neg_sig"] = float(np.mean(hi < 0))
            out[f"{tag}P5_frac_par_le_perp"] = float(np.mean(d <= 0))
            out[f"{tag}P5_median_diff"] = float(np.median(d))
            out[f"{tag}P5_rand_pct_median"] = float(np.nanmedian([r[f"{tag}P_rand_pct"] for r in ok]))
            out[f"{tag}P5_frac_rand_above95"] = float(np.nanmean([r[f"{tag}P_rand_pct"] > 0.95 for r in ok]))
            se = np.array([r[f"{tag}P_diff_se"] for r in ok])
            mu, smu, t2, i2, k = L.dl_pool(d, se)
            out[f"{tag}P5_pool"] = {"diff": mu, "ci95": [mu - 1.96 * smu, mu + 1.96 * smu], "I2": i2, "k": k}
    # per unit table
    out["units"] = []
    for r in rows:
        u = {k: r.get(k) for k in ("unit", "goal", "n_days", "n_agents", "n_statements", "d_E", "testable", "rho",
                                   "ci90", "g_par", "g_perp", "edge_par", "edge_perp", "plateau_par", "plateau_perp",
                                   "rand_pct", "rand_rho_q", "V_A", "V_A_lag1", "rand_V_pct", "P_par", "P_perp", "P_diff",
                                   "P_diff_ci95", "P_rand_pct", "cen_P_diff", "cen_P_diff_ci95", "vg_P_par", "vg_P_perp", "vg_P_diff",
                                   "vg_P_diff_ci95", "vg_P_rand_pct", "vgcen_P_diff", "vgcen_P_diff_ci95", "vg_n_pairs1",
                                   "vg_n_pairs2", "pca_rho", "pca_ci90",
                                   "pca_rand_pct", "pca_E_overlap", "raw_rho", "khat_rho", "khat_rand_pct", "own_rho",
                                   "own_rand_pct", "roomdiff_rho", "roomdiff_rand_pct", "roomdiff_rand_q", "mhat_rho",
                                   "mhat_ci90", "mhat_rand_pct", "mhat_rand_q", "Emhat_rho", "Emhat_rand_pct",
                                   "frac_edge_par_boot", "se_ln")}
        if r["goal"] == 51 and any(k.startswith("swap") for k in r):
            sw = [r[f"swap{s}_rand_pct"] for s in range(20) if f"swap{s}_rand_pct" in r]
            swr = [r[f"swap{s}_rho"] for s in range(20) if f"swap{s}_rho" in r]
            u["swap_pct_median"] = float(np.nanmedian(sw)) if sw else None
            u["swap_rho_median"] = float(np.nanmedian(swr)) if swr else None
        out["units"].append(u)
    # natives
    nat = {}
    for g in (38, 44):
        gr = [r for r in rows if r["goal"] == g]
        nat[f"G{g}"] = {"units": [{k: r.get(k) for k in ("unit", "n_days", "rho", "ci90", "roomdiff_rho",
                                                          "roomdiff_rand_pct", "mhat_rho", "mhat_ci90",
                                                          "mhat_rand_pct", "Emhat_rho", "P_diff")} for r in gr],
                        "pool_roomdiff": pool(gr, "roomdiff_rho", "roomdiff_se_ln"),
                        "pool_mhat": pool(gr, "mhat_rho", "mhat_se_ln"),
                        "pool_E": pool(gr)}
        main = [r for r in gr if r["n_days"] >= 3] or gr
        nat[f"G{g}"]["rule_units"] = [r["unit"] for r in main]
        nat[f"G{g}"]["roomdiff_below90"] = [bool(r.get("roomdiff_rand_pct", np.nan) < 0.90) for r in main]
        nat[f"G{g}"]["mhat_above95_and_ge3"] = [bool(r.get("mhat_rand_pct", np.nan) > 0.95 and
                                                     r.get("mhat_rho", np.nan) >= 3) for r in main]
    g51 = [r for r in rows if r["goal"] == 51]
    t51 = [r for r in g51 if r["testable"]]
    nat["G51"] = {"pool": pool(g51), "frac_testable_above95": float(np.nanmean([r["rand_pct"] > 0.95 for r in t51]))
                  if t51 else None, "n_testable": len(t51)}
    sw = [x["swap_pct_median"] for x in out["units"] if x.get("swap_pct_median") is not None]
    nat["G51"]["swap_pct_median"] = float(np.median(sw)) if sw else None
    out["natives"] = nat
    return out


def estimates_rows(full: dict, S: dict, kick: dict) -> list[dict]:
    rows = []
    src = "data/processed/H141-easy-plane-anisotropy/results/units.pkl"
    for key, r in full.items():
        model, variant, unit = key.split("|")
        ch = f"content:{model}:{variant}"
        role = "replication"
        base = {"period_unit": unit, "goal_no": int(r["goal"]), "channel": ch, "role": role, "source": src,
                "n": float(r["n_ad"]), "n_kind": "agent-days", "unit_local": unit,
                "status": "ok" if r["testable"] else "underpowered"}
        ci = r.get("ci90") or [None, None]
        rows.append(base | {"statistic": "h141_anisotropy_rhoA", "estimate": f(r["rho"]), "ci_lo": f(ci[0]),
                            "ci_hi": f(ci[1]), "ci_level": 0.90, "ci_kind": "percentile",
                            "method": "gamma_perp/gamma_par from drive-corrected subspace autocorrelation fits on the call "
                                      "clock (E = goal+kickoff[+room kickoffs] text plane); agent-day bootstrap 200",
                            "null": "isotropy rho=1; random-plane band"})
        vci = r.get("V_A_ci95") or [None, None]
        rows.append(base | {"statistic": "h141_variance_ratio_VA", "estimate": f(r["V_A"]), "ci_lo": f(vci[0]),
                            "ci_hi": f(vci[1]), "ci_level": 0.95, "ci_kind": "percentile",
                            "method": "per-dimension lag-0 content variance along E over across E; agent-day bootstrap",
                            "null": "V_A=1; random-plane band"})
        rows.append(base | {"statistic": "h141_random_plane_pct", "estimate": f(r["rand_pct"]), "ci_lo": None,
                            "ci_hi": None, "ci_kind": "none",
                            "method": "share of 200 Haar random planes of dimension d_E with lower rho_A than E",
                            "null": "random-plane band"})
        for tag, meth in (("vg_", "A1 primary: 1 - G(1)/G(>=2), noise-corrected day variogram of agent-day means "
                                   "along/across E (wells cancel); agent bootstrap"),
                          ("", "registered (superseded by A1): split-half noise-corrected day-to-day persistence of "
                               "agent-day mean deviations (leave-pair-out wells); agent bootstrap")):
            if r.get(f"{tag}P_par") is None or not np.isfinite(r.get(f"{tag}P_par", np.nan)):
                continue
            for nm in ("par", "perp"):
                c = r.get(f"{tag}P_{nm}_ci95") or [None, None]
                rows.append(base | {"statistic": f"h141_day_persistence_{nm}", "estimate": f(r[f"{tag}P_{nm}"]),
                                    "ci_lo": f(c[0]), "ci_hi": f(c[1]), "ci_level": 0.95, "ci_kind": "percentile",
                                    "n": float(r.get("vg_n_pairs1" if tag else "day_n_pairs", np.nan)),
                                    "n_kind": "agent day pairs", "method": meth, "null": "random-plane band"})
    for u, k in kick.items():
        goal = 51
        rows.append({"period_unit": u, "goal_no": goal, "channel": "content:bge_small:style_resid_period",
                     "role": "native", "source": "data/processed/H141-easy-plane-anisotropy/results/kick.json",
                     "statistic": "h141_kick_lag1_ratio_perp", "estimate": f(k["ratio_perp"]), "ci_lo": None,
                     "ci_hi": None, "ci_kind": "none", "n": float(k["n_rows"]), "n_kind": "statement x sender rows",
                     "unit_local": u, "method": "beta_perp(lag 1)/beta_perp(lag 0), sender-specific dose regression "
                     "(H130 A1) with response across the reader's text plane", "null": None,
                     "status": "ok" if k.get("n_days", 0) >= 3 else "underpowered"})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-estimates", action="store_true")
    a = ap.parse_args()
    full = pickle.loads((RES / "units.pkl").read_bytes())
    kick = json.loads((RES / "kick.json").read_text()) if (RES / "kick.json").exists() else {}
    S = {}
    for model, variant in L.VARIANTS:
        if any(k.startswith(f"{model}|{variant}|") for k in full):
            S[f"{model}|{variant}"] = variant_summary(full, model, variant)
    if kick:
        units = []
        for u, k in kick.items():
            k = dict(k)
            for nm in ("par", "perp"):
                k[f"boot_{nm}"] = np.array(k[f"boot_{nm}"])
            units.append(k)
        S["kick"] = {nm: K.pooled_ratio(units, nm) for nm in ("par", "perp")}
        S["kick"]["units"] = {u: {"ratio_par": k["ratio_par"], "ratio_perp": k["ratio_perp"],
                                  "beta_par": k["beta_par"][:2], "beta_perp": k["beta_perp"][:2],
                                  "se_par": k["se_par"][:2], "se_perp": k["se_perp"][:2], "n_days": k["n_days"]}
                              for u, k in kick.items()}
    if (RES / "ne38.json").exists():
        S["NE38"] = json.loads((RES / "ne38.json").read_text())
    (RES / "summary.json").write_text(json.dumps(S, indent=1, default=float))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "units"} if isinstance(v, dict) else v
                      for k, v in S.items()}, indent=1, default=float))
    if not a.no_estimates:
        import estimates as E
        rows = estimates_rows(full, S, kick)
        E.write_estimates(rows, hypothesis="H141")
        print(f"wrote {len(rows)} estimates rows")


if __name__ == "__main__":
    main()
