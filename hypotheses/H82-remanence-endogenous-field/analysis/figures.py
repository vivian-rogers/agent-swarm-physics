"""H82 figures (no text): summary_obs.pdf ((a) Delta gamma_1 per boundary, both models; (b) day profile of the RE mean
Delta gamma_d with the S0 bias), summary_obsb.pdf ((a) gamma on P-1 vs P+1 vs placebo, pooled; (b) synthetic power).
Usage: uv run python hypotheses/H82-remanence-endogenous-field/analysis/figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h82lib as L  # noqa: E402

FIG = L.ROOT / "hypotheses/H82-remanence-endogenous-field/figures"
C = {"bge_small": "#2a78d6", "gte_modernbert": "#eb6834"}
LAB = {"bge_small": "bge", "gte_modernbert": "gte"}
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6})


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    rows = pl.read_parquet(L.OUT / "replication/boundary_rows.parquet")
    prim = rows.filter((pl.col("config") == "primary") & (pl.col("term") == "e"))
    rep = json.loads((L.OUT / "replication/replication.json").read_text())
    syn = {m: json.loads((L.OUT / f"synthetic/synthetic_{m}.json").read_text()) for m in C}
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.4), gridspec_kw={"width_ratios": [1.5, 1]})
    Ps = sorted(set(prim["P"].to_list()))
    xx = np.arange(len(Ps))
    for k, m in enumerate(C):
        d = prim.filter((pl.col("model") == m) & (pl.col("d") == 1)).sort("P")
        off = (k - 0.5) * 0.3
        ax[0].errorbar(xx + off, d["dgamma"], yerr=[d["dgamma"] - d["dgamma_lo"], d["dgamma_hi"] - d["dgamma"]],
                       fmt="o", ms=3, lw=0.7, color=C[m], label=LAB[m])
        ax[0].axhline(syn[m]["scenarios"]["S0"]["mean:all/e/mean_dg1"], color=C[m], lw=0.6, ls=":")
    ax[0].axhline(0, color="#999", lw=0.5)
    ax[0].set_xticks(xx); ax[0].set_xticklabels([str(p) for p in Ps], fontsize=6)
    ax[0].axvline(18.5, color="#ccc", lw=0.6); ax[0].text(18.7, ax[0].get_ylim()[1] * 0.9, "regime III", fontsize=6.5)
    ax[0].set_xlabel("new goal period P"); ax[0].set_ylabel("Δγ₁ (day-1 remanence excess)")
    ax[0].set_title("(a) per boundary, 95% agent bootstrap (dotted: S0 bias)", loc="left", fontsize=8)
    ax[0].legend(frameon=False, fontsize=7, loc="lower left", ncol=2)
    for m in C:
        prof = rep["primary"][m]["all"]["re_profile"]
        ds = sorted(int(k) for k in prof)
        mu = np.array([prof[str(d)]["mu"] for d in ds]); se = np.array([prof[str(d)]["se"] for d in ds])
        b = np.array([syn[m]["scenarios"]["S0"].get(f"mean:all/e/mean_dg{d}", np.nan) for d in ds])
        ax[1].errorbar(ds, mu - b, yerr=1.96 * se, fmt="-o", ms=3, lw=1.2, color=C[m], label=LAB[m])
    ax[1].axhline(0, color="#999", lw=0.5)
    ax[1].set_xlabel("active day d of the new period"); ax[1].set_ylabel("RE mean Δγ_d − S0 bias")
    ax[1].set_title("(b) decay of the remanence", loc="left", fontsize=8); ax[1].legend(frameon=False, fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.1))
    labs = ["γ[P−1]", "γ[placebo]", "γ[P+1]"]
    for k, m in enumerate(C):
        d = prim.filter((pl.col("model") == m) & (pl.col("d") == 1))
        nx = d.filter(pl.col("gamma_next").is_not_nan())
        vals = [float(nx["gamma_prev"].mean()), float(nx["gamma_placebo_med"].mean()), float(nx["gamma_next"].mean())]
        ax[0].bar(np.arange(3) + (k - 0.5) * 0.38, vals, width=0.34, color=C[m], label=f"{LAB[m]} ({nx.height} boundaries)")
    ax[0].set_xticks(range(3)); ax[0].set_xticklabels(labs); ax[0].axhline(0, color="#999", lw=0.5)
    ax[0].set_ylabel("mean day-1 loading"); ax[0].legend(frameon=False, fontsize=6.5)
    ax[0].set_title("(a) past vs future vs placebo centroid", loc="left", fontsize=8)
    sc = ["S0", "S1_0.05", "S1_0.1", "S1_0.2", "S2_0.1"]
    for k, m in enumerate(C):
        pw = [syn[m]["scenarios"][s]["pass:all/e/mean_dg1"] for s in sc]
        pn = [syn[m]["scenarios"][s]["pass:all/e_new/mean_dg_all"] for s in sc]
        ax[1].plot(range(len(sc)), pw, "-o", ms=3, color=C[m], label=f"{LAB[m]} pooled Δγ₁")
        ax[1].plot(range(len(sc)), pn, "--s", ms=3, color=C[m], label=f"{LAB[m]} newcomers")
    ax[1].axhline(0.8, color="#999", lw=0.5, ls="--")
    ax[1].set_xticks(range(len(sc))); ax[1].set_xticklabels(["S0", "γ .05", "γ .1", "γ .2", "vets .1"])
    ax[1].set_ylabel("pass rate"); ax[1].legend(frameon=False, fontsize=6); ax[1].set_title("(b) synthetic power", loc="left", fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / "summary_obsb.pdf"); plt.close(fig)


if __name__ == "__main__":
    main()
