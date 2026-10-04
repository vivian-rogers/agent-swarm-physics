"""H92 evaluation: card predictions P1-P6, the per-period replication table and the two natives (G51, G38).
Input: forecasts.parquet (run_forecast.py). Outputs: data/processed/H92-rmt-cleaned-forecast/{periods.parquet,
eval/results.json, native/results.json}
Usage: uv run python hypotheses/H92-rmt-cleaned-forecast/analysis/evaluate.py
"""
from __future__ import annotations

import json

import numpy as np
import polars as pl

import h92lib as L

CONTENT = ["content_bge", "content_gte"]
RIVALS = ["E2_raw", "E3_lwi", "E4_lwcc", "E1_mean", "E0_zero", "E6_clip_mp"]


def with_r(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns([(1 - pl.col("mse_E5_clip") / pl.col(f"mse_{k}")).alias(f"r_{k}") for k in RIVALS] +
                           [(1 - pl.col(f"mse_{k}") / pl.col("mse_E0_zero")).alias(f"skill_{k}") for k in L.EST])


def period_table(f: pl.DataFrame, rng) -> pl.DataFrame:
    rows = []
    for (g, ch), x in f.group_by(["goal_no", "channel"], maintain_order=True):
        rec = {"goal_no": g, "channel": ch, "n_targets": x.height, "N_med": float(x["N"].median()),
               "W_med": float(x["size_target"].median()), "q_med": float(x["q"].median()), "k_cal_med": float(x["k_cal"].median()),
               "first_day": x["pt_date"].min(), "last_day": x["pt_date"].max()}
        for k in L.EST:
            rec[f"mse_{k}"] = float(x[f"mse_{k}"].mean())
        for k in RIVALS:
            m, lo, hi = L.boot_mean_ci(x[f"r_{k}"].to_numpy(), rng)
            rec[f"r_{k}"], rec[f"r_{k}_lo"], rec[f"r_{k}_hi"] = m, lo, hi
        ms = {k: rec[f"mse_{k}"] for k in L.EST[1:]}
        rec["best"] = min(ms, key=ms.get)
        rec["E5_beats_raw"] = rec["mse_E5_clip"] < rec["mse_E2_raw"]
        rec["E5_beats_bestLW"] = rec["mse_E5_clip"] < min(rec["mse_E3_lwi"], rec["mse_E4_lwcc"])
        rec["E5_lowest_E2_E5"] = rec["mse_E5_clip"] <= min(rec["mse_E2_raw"], rec["mse_E3_lwi"], rec["mse_E4_lwcc"])
        rec["skill_E5"] = float(x["skill_E5_clip"].mean()); rec["skill_E4"] = float(x["skill_E4_lwcc"].mean())
        rec["skill_E2"] = float(x["skill_E2_raw"].mean())
        rows.append(rec)
    return pl.DataFrame(rows, infer_schema_length=None).sort("channel", "goal_no")


def verdicts(pt: pl.DataFrame) -> pl.DataFrame:
    out = []
    for g in sorted(pt["goal_no"].unique().to_list()):
        c = pt.filter((pl.col("goal_no") == g) & pl.col("channel").is_in(CONTENT))
        if c.height < 2 or c["n_targets"].min() < 2:
            v = "descriptive"
        elif c["E5_lowest_E2_E5"].all():
            v = "supported"
        elif (~c["E5_beats_raw"]).all():
            v = "failed"
        else:
            v = "mixed"
        out.append({"goal_no": g, "verdict": v})
    return pl.DataFrame(out)


def share(x) -> float:
    x = np.asarray(x, bool)
    return float(x.mean()) if len(x) else float("nan")


def main():
    rng = np.random.default_rng(L.SEED)
    f = with_r(pl.read_parquet(L.OUT / "forecasts.parquet"))
    fe = f.filter(pl.col("variant") == "expand")
    pt = period_table(fe, rng)
    vd = verdicts(pt)
    pt = pt.join(vd, on="goal_no", how="left")
    pt.write_parquet(L.OUT / "periods.parquet", compression="zstd")
    res = {"n_forecasts": {c: fe.filter(pl.col("channel") == c).height for c in fe["channel"].unique().to_list()}}
    elig = pt.filter(pl.col("n_targets") >= 2)
    for ch in elig["channel"].unique().to_list():
        e = elig.filter(pl.col("channel") == ch)
        pm = e["r_E2_raw"].to_numpy()
        bs = [rng.choice(pm, len(pm)).mean() for _ in range(2000)]
        rec = {"n_periods": e.height,
               "P1_share_r_raw_pos": share(e["r_E2_raw"] > 0), "P1_mean_r_raw": float(pm.mean()),
               "P1_ci": [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))],
               "P2_share_E5_beats_bestLW": share(e["E5_beats_bestLW"]),
               "share_E5_beats_lwcc": share(e["mse_E5_clip"] < e["mse_E4_lwcc"]),
               "share_E5_beats_lwi": share(e["mse_E5_clip"] < e["mse_E3_lwi"]),
               "share_E5_beats_mean": share(e["mse_E5_clip"] < e["mse_E1_mean"]),
               "mean_r_lwcc": float(e["r_E4_lwcc"].mean()), "mean_r_lwi": float(e["r_E3_lwi"].mean()),
               "mean_r_mean": float(e["r_E1_mean"].mean()), "mean_r_zero": float(e["r_E0_zero"].mean()),
               "mean_r_mp": float(e["r_E6_clip_mp"].mean()),
               "best_counts": e["best"].value_counts().sort("count", descending=True).to_dicts(),
               "median_skill": {k: float(fe.filter(pl.col("channel") == ch)[f"skill_{k}"].median()) for k in L.EST}}
        pw = e.filter((pl.col("N_med") >= 16) & (pl.col("W_med") >= 8)) if ch.startswith("content") else e.filter(pl.col("N_med") >= 16)
        rec["powered"] = {"n_periods": pw.height, "P2_share": share(pw["E5_beats_bestLW"]) if pw.height else None,
                          "share_E5_beats_lwcc": share(pw["mse_E5_clip"] < pw["mse_E4_lwcc"]) if pw.height else None,
                          "goals": pw["goal_no"].to_list()}
        x = fe.filter(pl.col("channel") == ch)
        rec["P4_spearman_r_raw_q"] = L.spearman(x["r_E2_raw"].to_numpy(), x["q"].to_numpy())
        rec["P5_share_kmp_gt_kcal"] = share(x["k_mp"] > x["k_cal"])
        rec["P5_share_kmp_ge_kcal"] = share(x["k_mp"] >= x["k_cal"])
        rec["k_cal_dist"] = x["k_cal"].value_counts().sort("k_cal").to_dicts()
        rec["edge_cal_over_mp_median"] = float((x["edge_cal"] / x["edge_mp"]).median())
        rec["shrink_lwcc_median"] = float(x["shrink_lwcc"].median()); rec["shrink_lwi_median"] = float(x["shrink_lwi"].median())
        res[ch] = rec
    # P6: expand vs prev, matched forecasts
    p6 = {}
    for ch in f["channel"].unique().to_list():
        a = f.filter((pl.col("channel") == ch) & (pl.col("variant") == "expand") & (pl.col("n_train_days") >= 2))
        b = f.filter((pl.col("channel") == ch) & (pl.col("variant") == "prev")).select(
            "unit_id", "pt_date", pl.col("mse_E2_raw").alias("p_raw"), pl.col("mse_E5_clip").alias("p_clip"),
            pl.col("mse_E4_lwcc").alias("p_lwcc"))
        j = a.join(b, on=["unit_id", "pt_date"])
        p6[ch] = {"n": j.height, "share_expand_better_raw": share(j["mse_E2_raw"] < j["p_raw"]),
                  "rel_gain_raw": float((1 - j["mse_E2_raw"] / j["p_raw"]).mean()) if j.height else None,
                  "rel_gain_clip": float((1 - j["mse_E5_clip"] / j["p_clip"]).mean()) if j.height else None,
                  "rel_gain_lwcc": float((1 - j["mse_E4_lwcc"] / j["p_lwcc"]).mean()) if j.height else None}
    res["P6"] = p6
    # card verdict pieces
    p1 = all(res[c]["P1_share_r_raw_pos"] >= 2 / 3 and res[c]["P1_ci"][0] > 0 for c in CONTENT)
    p2 = all(res[c]["P2_share_E5_beats_bestLW"] >= 2 / 3 for c in CONTENT)
    lose4 = all(res[c]["share_E5_beats_lwcc"] <= 1 / 3 for c in CONTENT)
    res["card"] = {"P1_pass": p1, "P2_pass": p2, "E5_loses_to_E4_in_2of3": lose4,
                   "verdict": "supported" if (p1 and p2) else ("failed" if (not p1 or lose4) else "mixed"),
                   "period_verdicts": vd["verdict"].value_counts().to_dicts()}
    # ---------------------------------------------------------------- natives
    nat = {}
    g51 = fe.filter(pl.col("goal_no") == 51)
    long_units = ["51c", "51d", "51g"]
    n1 = {}
    for ch in CONTENT + ["talk"]:
        x = g51.filter((pl.col("channel") == ch) & pl.col("unit_id").is_in(long_units))
        n1[ch] = {"n": x.height, "spearman_r_raw_ntrain": L.spearman(x["r_E2_raw"].to_numpy(), x["n_train_days"].to_numpy()),
                  "mean_r_raw_by_ntrain": x.group_by("n_train_days").agg(pl.col("r_E2_raw").mean()).sort("n_train_days").to_dicts()}
        u = g51.filter(pl.col("channel") == ch).group_by("unit_id").agg(pl.len().alias("n"), pl.col("mse_E5_clip").mean(),
                                                                         pl.col("mse_E4_lwcc").mean(), pl.col("mse_E2_raw").mean(),
                                                                         pl.col("mse_E1_mean").mean()).filter(pl.col("n") >= 2)
        n1[ch]["units_E5_beats_E4"] = f"{int((u['mse_E5_clip'] < u['mse_E4_lwcc']).sum())}/{u.height}"
        n1[ch]["share_E5_beats_E4"] = share(u["mse_E5_clip"] < u["mse_E4_lwcc"])
        n1[ch]["units"] = u.sort("unit_id").to_dicts()
    gg = g51.filter((pl.col("channel") == "talk") & (pl.col("unit_id") == "51g") & pl.col("cont_real").is_not_null())
    n1["51g_talk_rooms"] = {"n": gg.height, "share_real_pos": share(gg["cont_real"] > 0),
                            "share_E5_err_le_E2": share((gg["cont_E5_clip"] - gg["cont_real"]).abs() <= (gg["cont_E2_raw"] - gg["cont_real"]).abs()),
                            "mean_real": float(gg["cont_real"].mean()) if gg.height else None,
                            "mean_E5": float(gg["cont_E5_clip"].mean()) if gg.height else None,
                            "mean_E2": float(gg["cont_E2_raw"].mean()) if gg.height else None,
                            "E5_beats_E4_51g_talk": bool(gg["mse_E5_clip"].mean() < gg["mse_E4_lwcc"].mean()) if gg.height else None}
    n1a = all((n1[c]["spearman_r_raw_ntrain"] or 0) < 0 for c in CONTENT)
    n1b = all(n1[c]["share_E5_beats_E4"] >= 2 / 3 for c in CONTENT)
    n1["verdict"] = "supported" if (n1a and n1b) else ("failed" if (not n1a and not n1b) else "mixed")
    n1["N1a_pass"], n1["N1b_pass"] = n1a, n1b
    nat["G51"] = n1
    g38 = fe.filter(pl.col("goal_no") == 38)
    n2 = {}
    for ch in ["talk"] + CONTENT:
        x = g38.filter((pl.col("channel") == ch) & pl.col("cont_real").is_not_null() & pl.col("cont_E2_raw").is_not_null())
        keep = x["cont_E5_clip"] / x["cont_E2_raw"]
        n2[ch] = {"n": x.height, "share_real_pos": share(x["cont_real"] > 0), "mean_real": float(x["cont_real"].mean()) if x.height else None,
                  "mean_E2": float(x["cont_E2_raw"].mean()) if x.height else None, "mean_E5": float(x["cont_E5_clip"].mean()) if x.height else None,
                  "mean_E4": float(x["cont_E4_lwcc"].mean()) if x.height else None,
                  "share_keep_ge_half": share(keep >= 0.5), "median_keep": float(keep.median()) if x.height else None,
                  "share_err_E5_le_E2": share((x["cont_E5_clip"] - x["cont_real"]).abs() <= (x["cont_E2_raw"] - x["cont_real"]).abs()),
                  "share_mse_E5_lt_E4": share(x["mse_E5_clip"] < x["mse_E4_lwcc"]),
                  "k_cal_median": float(x["k_cal"].median()) if x.height else None}
    t = n2["talk"]
    n2b = t["share_keep_ge_half"] >= 2 / 3 and t["share_err_E5_le_E2"] >= 2 / 3
    n2c = t["share_mse_E5_lt_E4"] >= 2 / 3
    n2["verdict"] = "supported" if (n2b and n2c) else ("failed" if (t["share_keep_ge_half"] < 2 / 3 and not n2c) else "mixed")
    n2["N2a_pass"], n2["N2b_pass"], n2["N2c_pass"] = t["share_real_pos"] >= 2 / 3, n2b, n2c
    nat["G38"] = n2
    (L.OUT / "eval").mkdir(exist_ok=True); (L.OUT / "native").mkdir(exist_ok=True)
    (L.OUT / "eval/results.json").write_text(json.dumps(res, indent=1, default=float))
    (L.OUT / "native/results.json").write_text(json.dumps(nat, indent=1, default=float))
    pl.Config.set_tbl_rows(100); pl.Config.set_tbl_cols(20); pl.Config.set_tbl_width_chars(250)
    print(pt.filter(pl.col("channel").is_in(CONTENT)).select("goal_no", "channel", "n_targets", "N_med", "W_med", "k_cal_med",
                                                             "r_E2_raw", "r_E3_lwi", "r_E4_lwcc", "r_E1_mean", "best", "verdict"))
    print(json.dumps({k: v for k, v in res.items()}, indent=1, default=float)[:6000])
    print(json.dumps(nat, indent=1, default=float)[:5000])


if __name__ == "__main__":
    main()
