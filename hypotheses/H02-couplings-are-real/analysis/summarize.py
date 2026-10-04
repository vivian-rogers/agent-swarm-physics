"""Print the summary tables used in the card's Results section; also writes results_summary.json."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
DATA = __import__("r1b_common").data_dir()   # round 1 or round 1b (+ mask): analysis/r1b_common.py
pl.Config.set_tbl_rows(60); pl.Config.set_tbl_cols(30); pl.Config.set_tbl_width_chars(250)


def main():
    out = {}
    # ---------------- harness C (null calibration / power at D = 5)
    BASE = ROOT / "data/processed/H02-couplings-are-real"   # synthetic harness: round 1 (data-independent)
    C = pl.read_parquet(BASE / "harness_C.parquet")
    cs = C.group_by("JL", "background").agg(
        *[pl.col(f"{n}_fpr").mean().round(3).alias(f"{n}_fpr") for n in ("blockN1", "naiveN0", "blockN0")],
        *[pl.col(f"{n}_power").mean().round(3).alias(f"{n}_power") for n in ("blockN1", "naiveN0")],
        pl.col("blockN1_pass").mean().round(2).alias("pass_rate"), (pl.col("blockN1_rank") == 1).mean().round(2).alias("rank1"),
        pl.col("blockN1_zI").median().round(2).alias("zI_med")).sort("background", "JL")
    print("harness C\n", cs); out["harness_C"] = cs.to_dicts()
    B2 = pl.read_parquet(BASE / "harness_B2.parquet")
    b2 = B2.group_by("JL", "D").agg(pl.col("ki1_auc").mean().round(3), pl.col("ki5_auc").mean().round(3),
                                    (pl.col("ki1_rank") == 1).mean().alias("ki1_top1"),
                                    (pl.col("ki5_rank") == 1).mean().alias("ki5_top1")).sort("JL", "D")
    print("harness B2 (lag-1 truth)\n", b2); out["harness_B2"] = b2.to_dicts()

    # ---------------- real chunks
    R = pl.read_parquet(DATA / "real_chunks.parquet").sort("regime", "mode", "chunk")
    cols = ["chunk", "mode", "regime", "N", "act", "naive_N0_frac_sig", "naive_N1_frac_sig", "block_N1_frac_sig",
            "block_N1_bh", "block_N1_npairs", "block_N1_frac_pos_sig", "box5_N1_frac_sig", "eq_N1_frac_sig",
            "eq_N1_frac_pos_sig", "block_N1_absJ", "block_N1_absJ_null", "ho_d31_per_bin", "ho_d21_per_bin",
            "ho_days_M3_gt_M1", "ho_days_M3_gt_M2", "n_days"]
    print(R.select(cols).with_columns(pl.col(pl.Float64).round(3)))
    g = R.group_by("regime", "mode").agg(
        pl.len().alias("chunks"),
        *[pl.col(f"{k}_frac_sig").median().round(3).alias(k) for k in ("naive_N0", "naive_N1", "block_N1", "box5_N1", "eq_N1")],
        (pl.col("block_N1_absJ") - pl.col("block_N1_absJ_null")).median().round(4).alias("excess_absJ"),
        (pl.col("box5_N1_absJ") - pl.col("box5_N1_absJ_null")).median().round(4).alias("excess_absJ_box5"),
        pl.col("block_N1_mean_z2").median().round(2).alias("mean_z2"),
        pl.col("block_N1_frac_pos_sig").median().round(2).alias("pos_share_sig"),
        pl.col("eq_N1_frac_pos_sig").median().round(2).alias("eq_pos_share_sig"),
        (pl.col("ho_d31_per_bin") * 1000).median().round(2).alias("ho_d31_mnats"),
        (pl.col("ho_d21_per_bin") * 1000).median().round(2).alias("ho_d21_mnats"),
        pl.col("ho_days_M3_gt_M1").sum().alias("days_M3>M1"), pl.col("n_days").sum().alias("days"),
        pl.col("ho_days_M3_gt_M2").sum().alias("days_M3>M2"),
        pl.col("block_N1_sig_same_share").mean().round(3).alias("sig_same_share"),
        pl.col("same_lab_share").mean().round(3).alias("same_share")).sort("regime", "mode")
    print(g); out["by_mode"] = g.to_dicts()
    # Mann-Whitney I vs C within regime (exploratory, chunks not independent within a goal)
    from scipy.stats import mannwhitneyu
    tests = {}
    for reg in ("I", "III"):
        for k in ("block_N1_frac_sig", "box5_N1_frac_sig", "eq_N1_frac_sig", "ho_d31_per_bin"):
            a = R.filter((pl.col("regime") == reg) & (pl.col("mode") == "I"))[k].to_numpy()
            b = R.filter((pl.col("regime") == reg) & (pl.col("mode") == "C"))[k].to_numpy()
            tests[f"{reg}:{k}"] = {"I_med": float(np.median(a)), "C_med": float(np.median(b)),
                                   "ratio_C_over_I": float(np.median(b) / np.median(a)) if np.median(a) else None,
                                   "p_MW": float(mannwhitneyu(a, b).pvalue)}
    print(json.dumps(tests, indent=1)); out["I_vs_C"] = tests

    # family enrichment over all chunks (KI-1 block vs N1)
    cp = pl.read_parquet(DATA / "real_couplings.parquet")
    fam = (cp.filter(pl.col("est").is_in(["block_N1", "box5_N1"])).group_by("est", "same_lab")
           .agg(pl.len(), (pl.col("z").abs() > 1.96).mean().round(3).alias("frac_sig"), pl.col("z").mean().round(3).alias("mean_z"),
                pl.col("J").mean().round(4).alias("mean_J")).sort("est", "same_lab"))
    print(fam); out["family"] = fam.to_dicts()
    # sign of significant equal-time couplings, pooled
    eq = cp.filter((pl.col("est") == "eq_N1") & (pl.col("z").abs() > 1.96))
    print("EQ significant:", eq.height, "negative share", round((eq["z"] < 0).mean(), 3))
    out["eq_sig_neg_share"] = float((eq["z"] < 0).mean())
    ki = cp.filter((pl.col("est") == "block_N1") & (pl.col("z").abs() > 1.96))
    out["ki_sig_neg_share"] = float((ki["z"] < 0).mean())
    print("KI-1 significant:", ki.height, "negative share", round(out["ki_sig_neg_share"], 3))
    # size of significant couplings (for the plausible leader-strength range)
    q = ki.select(pl.col("J").abs().quantile(0.5).alias("med"), pl.col("J").abs().quantile(0.9).alias("q90"),
                  pl.col("J").abs().max().alias("max"))
    print("|J| of significant KI-1 couplings:", q.to_dicts()); out["sig_absJ"] = q.to_dicts()[0]
    # largest real net influence vs others (margin) per chunk
    inf = pl.read_parquet(DATA / "real_influence.parquet").filter(pl.col("est") == "block")
    mg = inf.group_by("chunk").agg(pl.col("I").max().alias("I_top"), pl.col("I").sort(descending=True).get(1).alias("I_2nd"),
                                   pl.col("zI").max().alias("zI_top")).with_columns((pl.col("I_top") - pl.col("I_2nd")).alias("margin")).sort("chunk")
    print(mg.with_columns(pl.col(pl.Float64).round(3))); out["influence_margins"] = mg.to_dicts()
    # #26
    roster = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet").select("agent", "name", "lab")
    g26 = (pl.read_parquet(DATA / "real_influence.parquet").filter(pl.col("chunk") == "g26c0").join(roster, on="agent")
           .sort("est", "rank"))
    print(g26.select("est", "agent", "name", "I", "zI", "rank", "act").with_columns(pl.col(pl.Float64).round(3)))
    out["g26"] = g26.to_dicts()
    (DATA / "results_summary.json").write_text(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
