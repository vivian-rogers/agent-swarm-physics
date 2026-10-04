"""H48 cross-period test (replication layer): does tau_settle track read-out coverage / bulk mixing better than lambda_2
and room count? Leave-one-period-out prediction against a constant; one point per goal period (never pooled fits).

  uv run python hypotheses/H48-settling-mixing-time/analysis/compare.py [--n-perm 2000]
Writes data/processed/H48-settling-mixing-time/compare.json and compare_lopo.parquet."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h48lib as L  # noqa: E402
from h48lib import hc  # noqa: E402
from synthetic import PREDICTORS  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

EXTRA = {"h31_l2_sym_min": ("h31_l2_sym_min", "inv"), "h31_g_tr_min": ("h31_g_tr_min", "inv")}
PRIMARY = ["T90_k1_room", "tmix_batch_bulk"]
RIVALS = ["l2_sym_min", "l2_dir_min", "ul2_rw_min", "dg50_gamma", "h31_l2_sym_min", "h31_g_tr_min", "n_rooms"]


def xform(x, tr):
    x = np.asarray(x, float)
    if tr == "log":
        return np.log(x)
    if tr == "inv":
        return -np.log(x)
    return x


def table(S: pl.DataFrame, model: str, est: str = "S1") -> pl.DataFrame:
    return (S.filter((pl.col("model") == model) & (pl.col("estimator") == est))
            .select("goal_no", "tau", "detected", "A_0", "A_inf", "dbic"))


def run_lopo(D: pl.DataFrame, ycol: str, n_perm: int, groups: bool = False, seed: int = 0) -> list[dict]:
    allp = {**PREDICTORS, **EXTRA}
    out = []
    for name, (col, tr) in allp.items():
        if col not in D.columns:
            continue
        s = D.filter(pl.col(col).is_not_null() & pl.col(col).is_finite() & (pl.col(col) > 0 if tr != "lin" else True))
        if s.height < 8:
            continue
        y = np.log(s[ycol].to_numpy())
        x = xform(s[col].to_numpy(), tr)
        gr = np.where(s["regime"].to_numpy() == "I", "I", "II+III") if groups else None
        if groups and min((gr == "I").sum(), (gr != "I").sum()) < 3:
            continue
        r = L.lopo_compare(y, x, groups=gr, n_perm=n_perm, seed=seed)
        out.append(dict(predictor=name, column=col, n=r["n"], rmse=r["rmse"], rmse0=r["rmse0"], gain=r["gain"],
                        p_perm=r["p_perm"], slope=r["slope"], rho=float(stats.spearmanr(x, y).statistic)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-perm", type=int, default=2000)
    a = ap.parse_args()
    S = pl.read_parquet(hc.OUT / "settling_period.parquet")
    X = pl.read_parquet(hc.OUT / "readout_period.parquet").filter(pl.col("goal_no").is_in(hc.REPLICATION))
    res = {"n_replication": len(hc.REPLICATION)}
    rows = []
    for model in ("bge_small", "gte_modernbert"):
        T = table(S, model)
        D = X.join(T, on="goal_no").filter(pl.col("detected").fill_null(False))
        res[f"detected_{model}"] = {"n": D.height, "rate": D.height / len(hc.REPLICATION),
                                    "periods": D["goal_no"].to_list(),
                                    "tau_median_h": float(D["tau"].median()) if D.height else None,
                                    "tau_iqr_h": [float(D["tau"].quantile(0.25)), float(D["tau"].quantile(0.75))]
                                    if D.height else None}
        for grp in (False, True):
            lp = run_lopo(D, "tau", a.n_perm, groups=grp)
            for r in lp:
                r.update(model=model, regime_intercepts=grp)
            rows += lp
        # P2 magnitude
        ratio = (D["tau"] / D["k1_room_T90"]).to_numpy()
        res[f"P2_{model}"] = {"median_ratio_tau_over_T90": float(np.median(ratio)),
                              "iqr": [float(np.quantile(ratio, 0.25)), float(np.quantile(ratio, 0.75))],
                              "median_ratio_tau_over_T90_k5": float(np.median((D["tau"] / D["k5_room_T90"]).to_numpy())),
                              "median_ratio_tau_over_tmix": float(np.median((D["tau"] / D["tmix_batch_bulk"]).to_numpy())),
                              "median_ratio_tau_over_dg": float(np.median((D["tau"] / D["dg_bulk"]).to_numpy()))}
    lp = pl.DataFrame(rows)
    lp.write_parquet(hc.OUT / "compare_lopo.parquet")

    def get(model, pred, grp=False):
        s = lp.filter((pl.col("model") == model) & (pl.col("predictor") == pred) & (pl.col("regime_intercepts") == grp))
        return s.row(0, named=True) if s.height else None
    # P1
    for model in ("bge_small", "gte_modernbert"):
        prim = {p: get(model, p) for p in PRIMARY}
        hp = L.holm({p: v["p_perm"] for p, v in prim.items() if v})
        riv = {p: get(model, p) for p in RIVALS}
        best_riv = min((v["rmse"] for v in riv.values() if v), default=np.inf)
        verdicts = {}
        for p, v in prim.items():
            if not v:
                continue
            verdicts[p] = {"gain": v["gain"], "p_perm": v["p_perm"], "p_holm": hp[p], "rmse": v["rmse"],
                           "rmse0": v["rmse0"], "beats_m0": bool(v["gain"] >= 0.10 and hp[p] < 0.05),
                           "beats_rivals": bool(v["rmse"] < best_riv), "slope": v["slope"]}
        res[f"P1_{model}"] = {"primary": verdicts, "rivals": {p: ({"gain": v["gain"], "p_perm": v["p_perm"],
                                                                   "rmse": v["rmse"]} if v else None)
                                                              for p, v in riv.items()},
                              "best_rival_rmse": best_riv}
    pb, pg = res["P1_bge_small"]["primary"], res["P1_gte_modernbert"]["primary"]
    win_b = [p for p, v in pb.items() if v["beats_m0"]]
    win_g = [p for p, v in pg.items() if v["beats_m0"]]
    if res["detected_bge_small"]["n"] < 12:
        v1 = "inconclusive (too few detected)"
    elif win_b and any(pb[p]["beats_rivals"] for p in win_b) and win_g:
        v1 = "supported"
    elif not win_b:
        v1 = "failed"
    else:
        v1 = "mixed"
    res["P1_verdict"] = v1
    # P3 bulk vs worst
    pairs = [("T90_k1_room", "T99_k1_room"), ("tmix_batch_bulk", "tmix_batch_worst"), ("dg_bulk", "dg_worst")]
    res["P3"] = {f"{b}_vs_{w}": {"rmse_bulk": (get("bge_small", b) or {}).get("rmse"),
                                 "rmse_worst": (get("bge_small", w) or {}).get("rmse")} for b, w in pairs}
    res["P3"]["bulk_wins"] = int(sum(1 for b, w in pairs if get("bge_small", b) and get("bge_small", w)
                                     and get("bge_small", b)["rmse"] < get("bge_small", w)["rmse"]))
    # P4 within regime
    res["P4"] = {p: get("bge_small", p, True) for p in PRIMARY}
    # P5 models agree; P6 DQ5; P7 S1 vs S2; S2 validation
    def tab(model, est, det=True):
        t = table(S, model, est)
        return t.filter(pl.col("detected").fill_null(False)) if det else t

    def rho(t1, t2):
        j = t1.select("goal_no", pl.col("tau").alias("a")).join(t2.select("goal_no", pl.col("tau").alias("b")), on="goal_no")
        j = j.filter(pl.col("a").is_finite() & pl.col("b").is_finite())
        if j.height < 5:
            return {"n": j.height, "rho": None}
        r = stats.spearmanr(j["a"], j["b"])
        return {"n": j.height, "rho": float(r.statistic), "p": float(r.pvalue)}
    res["P5_bge_vs_gte"] = rho(tab("bge_small", "S1"), tab("gte_modernbert", "S1"))
    res["P6_dq5"] = rho(tab("bge_small", "S1"), tab("bge_small", "S1_dq5"))
    res["P6_chat"] = rho(tab("bge_small", "S1"), tab("bge_small", "S1_chat"))
    res["P7_S1_vs_S2"] = rho(tab("bge_small", "S1"), tab("bge_small", "S2_H20"))
    res["P7_S1_vs_S2_gte"] = rho(tab("gte_modernbert", "S1"), tab("gte_modernbert", "S2_H20"))
    res["P7_S1_vs_S3"] = rho(tab("bge_small", "S1"), tab("bge_small", "S3_H54day"))
    res["P7_S1_vs_S5"] = rho(tab("bge_small", "S1"), tab("bge_small", "S5_pair"))
    s2r = S.filter((pl.col("model") == "bge_small") & (pl.col("estimator") == "S2_H20")).select("goal_no", pl.col("tau_days").alias("mine"))
    s2p = S.filter(pl.col("estimator") == "S2_H20_published").select("goal_no", pl.col("tau_days").alias("pub"))
    j = s2r.join(s2p, on="goal_no").filter(pl.col("mine").is_finite() & pl.col("pub").is_finite())
    res["S2_validation"] = {"n": j.height, "spearman": float(stats.spearmanr(j["mine"], j["pub"]).statistic) if j.height > 4 else None,
                            "median_abs_log_ratio": float(np.median(np.abs(np.log(j["mine"] / j["pub"])))) if j.height else None}
    res["S2_detected_bge"] = int(tab("bge_small", "S2_H20").height)
    res["S2_tau_median_h"] = float(tab("bge_small", "S2_H20")["tau"].median() or np.nan)
    res["S5_tau_median_h"] = float(tab("bge_small", "S5_pair")["tau"].median() or np.nan)
    res["S3_tau_median_h"] = float(tab("bge_small", "S3_H54day")["tau"].median() or np.nan)
    # secondary LOPO with S2 (H20 timescale) as the outcome, bge
    D2 = X.join(tab("bge_small", "S2_H20"), on="goal_no")
    res["S2_lopo"] = [r for r in run_lopo(D2, "tau", a.n_perm // 4)] if D2.height >= 8 else None
    hc.save_json(hc.OUT / "compare.json", res)
    print("P1:", v1)
    for model in ("bge_small", "gte_modernbert"):
        print(model, res[f"detected_{model}"]["n"], "detected; median tau", res[f"detected_{model}"]["tau_median_h"])
        sub = lp.filter((pl.col("model") == model) & ~pl.col("regime_intercepts")).sort("rmse")
        print(sub.select("predictor", "n", "rmse", "rmse0", "gain", "p_perm", "slope", "rho").with_columns(pl.col(pl.Float64).round(3)))
    for k in ("P2_bge_small", "P3", "P5_bge_vs_gte", "P6_dq5", "P6_chat", "P7_S1_vs_S2", "P7_S1_vs_S3", "P7_S1_vs_S5", "S2_validation"):
        print(k, res[k])


if __name__ == "__main__":
    main()
