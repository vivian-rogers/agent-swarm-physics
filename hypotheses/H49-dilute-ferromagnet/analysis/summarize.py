"""H49 cross-unit summary: unit table, replication scoring (P1-P6), per-unit and per-period verdicts, figures.

Reads data/processed/H49-dilute-ferromagnet/<group>/<unit>.json (run_unit.py), native/*.json (native.py) and
synthetic/results.parquet (synthetic.py). Writes unit_table.parquet, outcomes.json and figures/*.pdf|png.
Usage: uv run python hypotheses/H49-dilute-ferromagnet/analysis/summarize.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h49lib as L  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

FIG = L.HYP / "figures"
C3, C1, CN = "#1f5fa8", "#c2581b", "#555555"


def verdict(r: dict) -> str:
    exc = r["z_g"] > 2
    perc = r["kappa"] >= 2 or r["S1"] > 0.3
    dense = exc and np.isfinite(r["cv_c10"]) and r["cv_c10"] <= 0.2
    if perc or dense:
        return "failed"
    if r["n_pos"] >= 4 and (not exc or (np.isfinite(r["cv_c10"]) and r["cv_c10"] >= 0.4)):
        return "supported"
    return "mixed"


def unit_table() -> pl.DataFrame:
    units = pl.read_parquet(L.DATA / "units.parquet")
    rows = []
    for u in units.iter_rows(named=True):
        p = L.DATA / u["group"] / f"{u['unit']}.json"
        if not p.exists():
            continue
        j = json.loads(p.read_text())
        r = {"unit": u["unit"], "group": u["group"], "kind": u["kind"], "regime": u["regime"],
             "goal_no": u["goal_no"], "N": j["N"], "days": u["n_days"], "T": j["T"], "n_pairs": j["n_pairs"]}
        for v, e in j["variants"].items():
            b, g = e["bonds"], e["graph"]
            pre = "" if v == "scaffold" else f"{v}_"
            r.update({f"{pre}n_pos": b["n_pos"], f"{pre}n_neg": b["n_neg"], f"{pre}n_bh_pos": b["n_bh_pos"],
                      f"{pre}frac_pos": b["n_pos"] / j["n_pairs"], f"{pre}mean_k": g["mean_k"],
                      f"{pre}kappa": g["kappa"], f"{pre}S1": g["S1"], f"{pre}S1_cm": g["S1_cm"],
                      f"{pre}clusters": ",".join(map(str, g["clusters"])), f"{pre}g": e["g"], f"{pre}E": e["E"],
                      f"{pre}z_g": e["z_g"], f"{pre}rho_ex": e["rho_bar_ex"], f"{pre}cv_c10": e["cv_c10"],
                      f"{pre}cv_c10_orig": e.get("cv_c10_orig", np.nan),
                      f"{pre}share_sig": e["share_sig"], f"{pre}mean_z": b["mean_z"], f"{pre}p_mean": b["p_mean"],
                      f"{pre}skew": b["skew_z"], f"{pre}q95_skew": b["q95_skew"], f"{pre}p_skew": b["p_skew"],
                      f"{pre}kurt": b["kurt_z"], f"{pre}pi1": b["pi1"], f"{pre}null_fp": b["null_fp_mean"],
                      f"{pre}frac05": b["frac05_pos"]})
            if "talk" in e:
                t = e["talk"]
                r.update({f"{pre}talk_N": t["N"], f"{pre}talk_n_pos": t["bonds"]["n_pos"],
                          f"{pre}talk_kappa": t["graph"]["kappa"], f"{pre}talk_S1": t["graph"]["S1"],
                          f"{pre}talk_z_g": t["z_g"], f"{pre}talk_mean_z": t["bonds"]["mean_z"]})
        if "boot" in j:
            bt = j["boot"]
            r.update({"boot_kind": bt["kind"], "n_pos_lo": bt["n_pos_ci"][0], "n_pos_hi": bt["n_pos_ci"][1],
                      "kappa_lo": bt["kappa_ci"][0], "kappa_hi": bt["kappa_ci"][1], "S1_lo": bt["S1_ci"][0],
                      "S1_hi": bt["S1_ci"][1], "boot_frac_kappa_ge2": bt["frac_kappa_ge2"],
                      "mean_z_lo": bt["mean_z_ci"][0], "mean_z_hi": bt["mean_z_ci"][1]})
        r["clusters_list"] = j["variants"]["scaffold"]["graph"]["clusters"]
        r["verdict"] = verdict(r)
        rows.append(r)
    return pl.DataFrame(rows)


def score(df: pl.DataFrame) -> dict:
    rep = df.filter(pl.col("kind") == "replication")
    r3 = rep.filter(pl.col("regime") == "III")
    r1 = rep.filter(pl.col("regime") == "I")
    out = {"n_units": {"III": r3.height, "I": r1.height}}
    # P1
    out["P1"] = {"median_frac_pos": float(r3["frac_pos"].median()), "frac_mean_k_lt1": float((r3["mean_k"] < 1).mean()),
                 "pass": bool(r3["frac_pos"].median() <= 0.05 and (r3["mean_k"] < 1).mean() >= 2 / 3)}
    # P2
    ex = r3.filter(pl.col("z_g") > 2)
    cv = ex["cv_c10"].to_numpy()
    out["P2"] = {"n_excess_units": ex.height, "units": ex["unit"].to_list(), "cv_c10": cv.tolist(),
                 "frac_cv_ge04": float(np.mean(cv >= 0.4)) if cv.size else np.nan,
                 "frac_skew_gt_q95": float((ex["skew"] > ex["q95_skew"]).mean()) if ex.height else np.nan}
    out["P2"]["pass"] = bool(cv.size and out["P2"]["frac_cv_ge04"] >= 2 / 3 and out["P2"]["frac_skew_gt_q95"] >= 0.5)
    # P3
    below = (r3["kappa"] < 2) & (r3["S1"] <= 0.3)
    cl = [c for lst in r3["clusters_list"].to_list() for c in lst]
    out["P3"] = {"frac_below": float(below.mean()), "n_clusters": len(cl),
                 "frac_clusters_le3": float(np.mean([c <= 3 for c in cl])) if cl else np.nan,
                 "cluster_sizes": sorted(cl, reverse=True)}
    out["P3"]["pass"] = bool(below.mean() >= 2 / 3 and (not cl or out["P3"]["frac_clusters_le3"] >= 0.8))
    # P4
    med = float(r3["frac_pos"].median())
    hot = r3.filter(pl.col("goal_no").is_in([44, 51]))
    out["P4"] = {"median_frac_pos_III": med, "hot_units": hot["unit"].to_list(), "hot_frac_pos": hot["frac_pos"].to_list(),
                 "frac_hot_above_median": float((hot["frac_pos"] > med).mean()),
                 "hot_share_of_bonds": float(hot["n_pos"].sum() / max(r3["n_pos"].sum(), 1))}
    out["P4"]["pass"] = bool(out["P4"]["frac_hot_above_median"] >= 2 / 3)

    def loss(d):
        x = d.filter(pl.col("raw_n_pos") >= 1)
        return ((x["raw_n_pos"] - x["n_pos"]) / x["raw_n_pos"]).to_numpy()
    l3, l1 = loss(r3), loss(r1)
    out["P5"] = {"median_loss_III": float(np.median(l3)) if l3.size else np.nan,
                 "median_loss_I": float(np.median(l1)) if l1.size else np.nan, "n_III": int(l3.size), "n_I": int(l1.size),
                 "sum_raw_III": int(r3["raw_n_pos"].sum()), "sum_cond_III": int(r3["n_pos"].sum()),
                 "sum_raw_I": int(r1["raw_n_pos"].sum()), "sum_cond_I": int(r1["n_pos"].sum())}
    out["P5"]["pass"] = bool(l3.size and l1.size and np.median(l3) >= 0.5 and np.median(l1) <= 0.25)
    b1 = (r1["kappa"] < 2) & (r1["S1"] <= 0.3)
    out["P6"] = {"frac_below_I": float(b1.mean()), "median_frac_pos_I": float(r1["frac_pos"].median()),
                 "frac_excess_I": float((r1["z_g"] > 2).mean()), "cv_c10_I_excess":
                     r1.filter(pl.col("z_g") > 2)["cv_c10"].to_list()}
    # H (rivals): dense (J = 1.2/N) vs dilute (J = 0.5) likelihood of each excess unit's CV-C10 band, from the
    # synthetic replicates (recall 1, excess z > 2) at the nearest template by N; add-0.5 smoothing
    sp = L.DATA / "synthetic/results.parquet"
    if sp.exists():
        sy = pl.read_parquet(sp).filter((pl.col("recall") == 1.0) & (pl.col("scaffold_z_g") > 2))
        def band(c):
            return 0 if c <= 0.2 else (1 if c < 0.4 else 2)
        probs = {}
        for tpl in ("40", "44b", "51d"):
            for cond in ("dense", "dilute05", "perc"):
                cv = sy.filter((pl.col("template") == tpl) & (pl.col("cond") == cond))["scaffold_cv_c10"].drop_nans().to_list()
                cnt = np.bincount([band(c) for c in cv], minlength=3) + 0.5
                probs[(tpl, cond)] = cnt / cnt.sum()
        rows = []
        for r in ex.iter_rows(named=True):
            tpl = "40" if r["N"] <= 15 else ("44b" if r["N"] <= 20 else "51d")
            b = band(r["cv_c10"]) if np.isfinite(r["cv_c10"]) else None
            if b is None:
                continue
            rows.append({"unit": r["unit"], "template": tpl, "band": b,
                         "llr_dense_vs_dilute": float(np.log(probs[(tpl, "dense")][b] / probs[(tpl, "dilute05")][b])),
                         "llr_dense_vs_perc": float(np.log(probs[(tpl, "dense")][b] / probs[(tpl, "perc")][b]))})
        out["H_dense_vs_dilute"] = {"units": rows,
                                    "sum_llr_dense_vs_dilute": float(sum(x["llr_dense_vs_dilute"] for x in rows)),
                                    "sum_llr_dense_vs_perc": float(sum(x["llr_dense_vs_perc"] for x in rows)),
                                    "band_probs": {f"{k[0]}|{k[1]}": v.tolist() for k, v in probs.items()}}
    # null-internal calibration on real data
    out["internal_null_fp"] = {"median": float(rep["null_fp"].median()), "max": float(rep["null_fp"].max())}
    # counts and verdicts
    out["verdicts_units"] = {reg: dict(zip(*np.unique(rep.filter(pl.col("regime") == reg)["verdict"].to_list(),
                                                      return_counts=True))) for reg in ("III", "I")}
    for reg in out["verdicts_units"]:
        out["verdicts_units"][reg] = {k: int(v) for k, v in out["verdicts_units"][reg].items()}
    out["totals"] = {"III_pairs": int(r3["n_pairs"].sum()), "III_pos": int(r3["n_pos"].sum()),
                     "III_neg": int(r3["n_neg"].sum()), "I_pairs": int(r1["n_pairs"].sum()),
                     "I_pos": int(r1["n_pos"].sum()), "I_neg": int(r1["n_neg"].sum()),
                     "III_expected_false_pos": int(r3.height), "I_expected_false_pos": int(r1.height),
                     "III_excess_units": r3.filter(pl.col("z_g") > 2)["unit"].to_list(),
                     "I_excess_units": r1.filter(pl.col("z_g") > 2)["unit"].to_list(),
                     "III_meanz_sig_units": r3.filter(pl.col("p_mean") < 0.05)["unit"].to_list(),
                     "I_meanz_sig_units": r1.filter(pl.col("p_mean") < 0.05)["unit"].to_list()}
    return out


def period_verdicts(df: pl.DataFrame) -> dict:
    out = {}
    for g in df.filter(pl.col("kind") == "replication")["group"].unique().sort().to_list():
        v = df.filter((pl.col("group") == g) & (pl.col("kind") == "replication"))["verdict"].to_list()
        c = {k: v.count(k) for k in set(v)}
        top = max(c.values())
        winners = [k for k, n in c.items() if n == top]
        out[g] = winners[0] if len(winners) == 1 else "mixed"
    return out


def fig_main(df: pl.DataFrame):
    """(a) Where the surviving excess lives: CV-C10 vs mean bond z for units with a significant conditioned excess,
    against planted dense (J = 1.2/N) and dilute (J = 0.5) synthetic swarms at village sampling.
    (b) Significant positive bonds per unit, raw vs conditioned, against the ~1 expected false bond per unit."""
    rep = df.filter(pl.col("kind") == "replication")
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
    sp = L.DATA / "synthetic/results.parquet"
    if sp.exists():
        sy = pl.read_parquet(sp).filter((pl.col("recall") == 1.0) & (pl.col("scaffold_z_g") > 2))
        for cond, col, mk, lab in (("dense", "#999999", "x", "synthetic dense"), ("dilute05", "#3a9a3a", "+", "synthetic dilute")):
            d = sy.filter(pl.col("cond") == cond)
            ax[0].scatter(d["scaffold_mean_z"], d["scaffold_cv_c10"], s=14, c=col, marker=mk, alpha=0.6, label=lab,
                          linewidths=0.8)
    for reg, col, mk in (("III", C3, "o"), ("I", C1, "s")):
        d = rep.filter((pl.col("regime") == reg) & (pl.col("z_g") > 2))
        ax[0].scatter(d["mean_z"], d["cv_c10"], s=30, c=col, marker=mk, edgecolor="k", linewidth=0.5,
                      label=f"regime {reg} (excess z>2)")
        for u, xi, yi in zip(d["unit"].to_list(), d["mean_z"].to_list(), d["cv_c10"].to_list()):
            if reg == "III":
                ax[0].annotate(u, (xi, yi), fontsize=5.5, xytext=(2, 2), textcoords="offset points")
    ax[0].axhline(0.4, color=CN, lw=0.6, ls="--"); ax[0].axhline(0.1, color=CN, lw=0.5, ls=":")
    ax[0].set_ylim(-0.3, 1.3)
    ax[0].set_xlabel("mean bond z (dense shift)")
    ax[0].set_ylabel("CV-C10 (excess share, top 10% pairs)")
    ax[0].legend(fontsize=5.5, frameon=False, loc="upper right")
    ax[0].set_title("(a) surviving excess is spread, not concentrated", fontsize=8.5)
    d3 = rep.filter(pl.col("regime") == "III").sort("goal_no", "unit")
    x = np.arange(d3.height)
    ax[1].bar(x - 0.2, d3["raw_n_pos"], 0.4, color="#bbbbbb", label="raw")
    ax[1].bar(x + 0.2, d3["n_pos"], 0.4, color=C3, label="conditioned")
    ax[1].axhline(1, color="k", lw=0.6, ls=":", label="≈ expected false / unit")
    ax[1].set_xticks(x); ax[1].set_xticklabels(d3["unit"].to_list(), fontsize=5.5, rotation=90)
    ax[1].set_ylabel("significant positive bonds")
    ax[1].legend(fontsize=6, frameon=False)
    ax[1].set_title("(b) regime III: bonds fall to the false floor", fontsize=8.5)
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "summary_obs.pdf"); fig.savefig(FIG / "summary_obs.png", dpi=160)
    plt.close(fig)


def fig_synth():
    p = L.DATA / "synthetic/results.parquet"
    if not p.exists():
        return
    df = pl.read_parquet(p)
    conds = [("null", 1.0, "null"), ("null", 0.7, "null\nr=.7"), ("dilute05", 1.0, "dil.\n.5"),
             ("dilute025", 1.0, "dil.\n.25"), ("dense", 1.0, "dense"), ("perc", 1.0, "perc.")]
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.4))
    xs = np.arange(len(conds))
    for k, (c, r, lab) in enumerate(conds):
        d = df.filter((pl.col("cond") == c) & (pl.col("recall") == r))
        ax[0].bar(k - 0.2, d["raw_n_pos"].mean(), 0.4, color="#bbbbbb")
        ax[0].bar(k + 0.2, d["scaffold_n_pos"].mean(), 0.4, color=C3)
        dv = d.filter(pl.col("scaffold_z_g") > 2)["scaffold_cv_c10"].drop_nans()
        ax[1].bar(k, dv.median() if dv.len() else 0.0, 0.6, color=C3 if dv.len() >= 10 else "#bbbbbb")
        ax[1].text(k, (dv.median() if dv.len() else 0.0) + 0.01, f"n={dv.len()}", ha="center", fontsize=5)
        ax[2].bar(k - 0.2, ((d["scaffold_kappa"] < 2) & (d["scaffold_S1"] <= 0.3)).mean(), 0.4, color=C3)
        ax[2].bar(k + 0.2, ((d["scaffold_z_g"] > 2) & (d["scaffold_cv_c10"] >= 0.4)).mean(), 0.4, color="#7fb37f")
    for a in ax:
        a.set_xticks(xs); a.set_xticklabels([c[2] for c in conds], fontsize=6)
    ax[0].set_ylabel("significant + bonds / unit", fontsize=7); ax[0].set_title("(a) raw (grey) vs conditioned", fontsize=8)
    ax[1].axhline(0.1, color=CN, lw=0.5, ls=":"); ax[1].set_ylabel("CV-C10 (median, excess z>2)", fontsize=7)
    ax[1].set_title("(b) excess concentration", fontsize=8)
    ax[2].set_ylabel("fraction of replicates", fontsize=7)
    ax[2].set_title("(c) 'below percolation' / 'concentrated'", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic.pdf"); fig.savefig(FIG / "synthetic.png", dpi=160)
    plt.close(fig)


def main():
    df = unit_table()
    df.drop("clusters_list").write_parquet(L.DATA / "unit_table.parquet")
    out = score(df)
    out["period_verdicts"] = period_verdicts(df)
    (L.DATA / "outcomes.json").write_text(json.dumps(out, indent=1, default=float))
    fig_main(df)
    fig_synth()
    L.write_prov("unit_results", "hypotheses/H49-dilute-ferromagnet/analysis/run_unit.py (+ summarize.py)",
                 {"n_surr": 200, "n_boot": 200, "variants": ["scaffold", "edge", "raw"], "lam": L.LAM,
                  "threshold": "one-sided empirical p < 1/n_pairs (pooled leave-one-out surrogate z)",
                  "cv_c10": "pooled ratio (Amendment 1)", "bins": "activity_bins_fixed (Amendment 2)"})
    if (L.DATA / "synthetic/results.parquet").exists():
        L.write_prov("synthetic", "hypotheses/H49-dilute-ferromagnet/analysis/synthetic.py",
                     {"reps": 30, "n_surr": 100, "templates": ["40", "44b", "51d"], "update_prob": 0.35,
                      "dense_J": "1.2/N", "dilute_J": [0.5, 0.25], "perc": "ER mean degree 3, J 0.3"})
    if (L.DATA / "native").exists():
        L.write_prov("native", "hypotheses/H49-dilute-ferromagnet/analysis/native.py",
                     {"tests": ["NE43", "G44", "G51", "NE14"], "split_half_surr": 100, "checkpoint_window_min": 30},
                     tables=["activity_bins_fixed", "outages_fixed/reasons", "outages_fixed/stall_minutes",
                             "kicks_classified", "ground_truth_labels", "roster"])
    cols = ["unit", "regime", "N", "days", "raw_n_pos", "edge_n_pos", "n_pos", "n_neg", "mean_k", "kappa", "S1",
            "raw_z_g", "z_g", "g", "cv_c10", "mean_z", "p_mean", "skew", "q95_skew", "null_fp", "verdict"]
    with pl.Config(tbl_rows=80, tbl_width_chars=260, float_precision=3):
        print(df.select([c for c in cols if c in df.columns]))
    print(json.dumps({k: v for k, v in out.items() if k != "P3"}, indent=1, default=float)[:4000])
    print("P3", {k: v for k, v in out["P3"].items() if k != "cluster_sizes"})


if __name__ == "__main__":
    main()
