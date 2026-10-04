"""H61 replication layer: the common estimator on every eligible period (non-holdout only).

  uv run python hypotheses/H61-contagiousness-at-first-use/analysis/explore.py [--goals 38,51]
Output: data/processed/H61-contagiousness-at-first-use/results/{periods.json, period_table.parquet, summary.json}
Verdict rule (card + amendment A1): supported = dLL(F - B4) lower 95% CI > 0 and top-decile lift for Y >= 1.5;
failed = dLL(F - B4) <= 0; mixed otherwise; n/a = < 300 test ideas or < 20 positive test ideas.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h61lib as L  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H61-contagiousness-at-first-use"
RES = OUT / "results"
GOALS = [5, 6, 7, 8, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39, 40,
         41, 42, 44, 51]
MIN_TEST, MIN_POS = 300, 20


def verdict(s: dict) -> str:
    if not s.get("eligible"):
        return "n/a"
    if s["dll_F_B4"] <= 0:
        return "failed"
    if s["dll_F_B4_lo"] > 0 and s["lift_y"] >= 1.5:
        return "supported"
    return "mixed"


def run(g: int) -> dict:
    df = L.prep(pl.read_parquet(OUT / f"G{g:02d}/ideas.parquet"))
    regime = df["regime"][0]
    out = dict(goal=g, regime=regime, n_ideas=df.height, n_days=int(df["day"].n_unique()),
               base_all=float(df["y"].mean()), N_room=float(df["n_present"].median()))
    pred = L.forward_chain(df, "y")
    if pred.height == 0:
        out.update(eligible=False, n_test=0, n_pos=0)
        out["verdict"] = verdict(out)
        return out
    s = L.score_period(pred, "y", B=2000, seed=g)
    out.update(s)
    out["eligible"] = bool(s["n_test"] >= MIN_TEST and s["n_pos"] >= MIN_POS)
    out["verdict"] = verdict(out)
    pred.write_parquet(OUT / f"G{g:02d}/pred_y.parquet", compression="zstd")
    if out["eligible"]:
        out["coef"] = L.coefs(df, "y", "F")
        # gte-modernbert specificity variant (DQ5: report both models)
        dg = L.prep(pl.read_parquet(OUT / f"G{g:02d}/ideas.parquet"), spec_col="spec_gte")
        pg = L.forward_chain(dg, "y", models=("B4", "F"))
        d = (L.ll(pg["y"].to_numpy(), pg["p_F"].to_numpy()) - L.ll(pg["y"].to_numpy(), pg["p_B4"].to_numpy())) * 1000
        bs = L.cluster_boot(lambda idx: d[idx].mean(), pg["seed_msg"].to_numpy(), 500, np.random.default_rng(g))
        out["dll_F_B4_gte"] = float(d.mean())
        out["dll_F_B4_gte_lo"], out["dll_F_B4_gte_hi"] = (float(x) for x in np.percentile(bs, [2.5, 97.5]))
        out["coef_gte_spec"] = L.coefs(dg, "y", "F")["spec"]
        # Y3 (reach >= 3) as a secondary event
        p3 = L.forward_chain(df, "y3", models=("B4", "F"))
        if p3["y3"].sum() >= 10:
            y3 = p3["y3"].to_numpy()
            out["auc_F_y3"] = float(L.auc(y3, p3["p_F"].to_numpy()))
            out["auc_B4_y3"] = float(L.auc(y3, p3["p_B4"].to_numpy()))
        out["conv"] = L.gains_conv(df, B=300, seed=g)
    return out


def summarize(rows: list[dict]) -> dict:
    el = [r for r in rows if r.get("eligible")]
    n = len(el)
    sm = dict(n_periods=len(rows), n_eligible=n,
              verdicts={v: sum(r["verdict"] == v for r in rows) for v in ("supported", "mixed", "failed", "n/a")})
    sm["P1_ci_pos_B4"] = sum(r["dll_F_B4_lo"] > 0 for r in el)
    sm["P1_ci_pos_B3"] = sum(r["dll_F_B3_lo"] > 0 for r in el)
    sm["P1_point_pos_B4"] = sum(r["dll_F_B4"] > 0 for r in el)
    sm["P1_pool_B4"] = L.dl_pool([r["dll_F_B4"] for r in el], [r["dll_F_B4_se"] for r in el])
    sm["P1_pool_B3"] = L.dl_pool([r["dll_F_B3"] for r in el], [r["dll_F_B3_se"] for r in el])
    sm["P1_ci_pos_B4_gte"] = sum(r.get("dll_F_B4_gte_lo", -1) > 0 for r in el)
    gains = [r["auc_F"] - r["auc_B1"] for r in el]
    sm["P2_auc_gain_median"] = float(np.median(gains))
    sm["P2_auc_F_gt_B1"] = sum(g > 0 for g in gains)
    sm["P2_rho_F_gt_B1"] = sum(r["rho_F"] > r["rho_B1"] for r in el)
    sm["auc_median"] = {m: float(np.median([r[f"auc_{m}"] for r in el])) for m in ("B1", "B2", "B3", "B4", "F", "Fm")}
    sm["rho_median"] = {m: float(np.median([r[f"rho_{m}"] for r in el])) for m in ("B1", "B3", "B4", "F")}
    for f in L.FEATS:
        b = np.array([r["coef"][f][0] for r in el])
        se = np.array([r["coef"][f][1] for r in el])
        sm[f"coef_{f}"] = dict(n_neg=int((b < 0).sum()), n_pos=int((b > 0).sum()),
                               n_ci_neg=int((b + 1.96 * se < 0).sum()), n_ci_pos=int((b - 1.96 * se > 0).sum()),
                               median=float(np.median(b)), pooled=L.dl_pool(b, se))
    for c in (0, 1, 3):
        b = np.array([r["coef"][f"cls{c}"][0] for r in el])
        sm[f"coef_cls{c}_median"] = float(np.median(b))
    sm["P4_lift_y_ge2"] = sum(r["lift_y"] >= 2 for r in el)
    sm["P4_lift_y_median"] = float(np.median([r["lift_y"] for r in el]))
    sm["lift_y3_median"] = float(np.median([r["lift_y3"] for r in el]))
    cv = [r["conv"] for r in el if r.get("conv", {}).get("eligible")]
    sm["P5_n"] = len(cv)
    if cv:
        sm["P5_read_gt_unread"] = sum(c["diff"] > 0 for c in cv)
        sm["P5_ci_pos"] = sum(c["diff_lo"] > 0 for c in cv)
        sm["P5_ci_neg"] = sum(c["diff_hi"] < 0 for c in cv)
        sm["P5_pool"] = L.dl_pool([c["diff"] for c in cv], [c["diff_se"] for c in cv])
        sm["P5_g_read_median"] = float(np.median([c["g_read"] for c in cv]))
        sm["P5_g_unread_median"] = float(np.median([c["g_unread"] for c in cv]))
    by_reg = {}
    for reg in ("I", "II", "III"):
        rr = [r for r in el if r["regime"] == reg]
        if rr:
            by_reg[reg] = dict(n=len(rr), ci_pos=sum(r["dll_F_B4_lo"] > 0 for r in rr),
                               med_dll=float(np.median([r["dll_F_B4"] for r in rr])),
                               med_auc_F=float(np.median([r["auc_F"] for r in rr])))
    sm["by_regime"] = by_reg
    ns = [r["N_room"] for r in el]
    sm["rho_dll_N"] = float(stats.spearmanr(ns, [r["dll_F_B4"] for r in el]).statistic)
    return sm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", default="")
    a = ap.parse_args()
    goals = [int(x) for x in a.goals.split(",")] if a.goals else GOALS
    RES.mkdir(parents=True, exist_ok=True)
    goals = sorted(goals, key=lambda g: -1 if g == 51 else g)
    with Pool(4) as pool:
        rows = pool.map(run, goals, chunksize=1)
    rows = sorted(rows, key=lambda r: r["goal"])
    (RES / "periods.json").write_text(json.dumps(rows, indent=1, default=float))
    flat = [{k: v for k, v in r.items() if not isinstance(v, dict)} for r in rows]
    pl.DataFrame(flat).write_parquet(RES / "period_table.parquet")
    if not a.goals:
        sm = summarize(rows)
        (RES / "summary.json").write_text(json.dumps(sm, indent=1, default=float))
        print(json.dumps(sm, indent=1, default=float))
    for r in rows:
        print(f"G{r['goal']:02d} {r['regime']:>3} {r['verdict']:>9} n_test {r.get('n_test', 0):6d} "
              f"dLL(F-B4) {r.get('dll_F_B4', float('nan')):7.2f} [{r.get('dll_F_B4_lo', float('nan')):7.2f}, "
              f"{r.get('dll_F_B4_hi', float('nan')):7.2f}] AUC F {r.get('auc_F', float('nan')):.3f} "
              f"B1 {r.get('auc_B1', float('nan')):.3f} lift {r.get('lift_y', float('nan')):.2f}")


if __name__ == "__main__":
    main()
