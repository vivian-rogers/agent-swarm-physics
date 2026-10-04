"""H106 figures (static PDFs for the card and the RevTeX summary).
  figures/summary_obs.pdf   (a) disattenuated similarity vs lag by N class with the V1 fit; (b) alpha_k real (CI) vs
                            synthetic drift (D) and magnet (M) distributions, both models
  figures/summary_obsb.pdf  (a) per-period rho_G vs N_G; (b) NE27 Delta ln k real vs D and M
Usage: uv run python hypotheses/H106-slow-mode-finite-size/analysis/figures.py
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
import h106lib as L  # noqa: E402

FIG = Path(__file__).resolve().parent.parent / "figures"
BLUE, ORANGE, AQUA, GRAY, INK, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#a3a29c", "#0b0b0b", "#52514e"
MOD = {"bge_small": ("bge", BLUE), "gte_modernbert": ("gte", ORANGE)}
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "legend.frameon": False,
                     "lines.linewidth": 2})


def main():
    FIG.mkdir(exist_ok=True)
    rep = json.loads((L.OUT / "replication/replication.json").read_text())
    syn = pl.read_parquet(L.OUT / "synthetic/replicates.parquet")
    nat = json.loads((L.OUT / "natives/natives.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6))
    cls_col = {"N<5": AQUA, "N 5.5-8": BLUE, "N>=8": ORANGE}
    for model, ls in (("bge_small", "-"), ("gte_modernbert", "--")):
        for c, prof in rep["profile"][model].items():
            x = [(lo + min(hi, 120)) / 2 for lo, hi, v, n in prof if v is not None and n >= 3]
            y = [v for lo, hi, v, n in prof if v is not None and n >= 3]
            ax[0].plot(x, y, ls, marker="o", ms=4, color=cls_col[c],
                       label=f"{c} ({MOD[model][0]})")
    ax[0].axhline(0, color=GRAY, lw=1)
    ax[0].set_xlabel("lag between blocks (active days)"); ax[0].set_ylabel("disattenuated similarity s̃")
    ax[0].legend(fontsize=6, ncol=2); ax[0].set_title("(a) lag profile by village size (regime I)", fontsize=8, loc="left")
    pos = 0
    for model in ("bge_small", "gte_modernbert"):
        name, col = MOD[model]
        for w, wc in (("D", GRAY), ("M", AQUA)):
            a = syn.filter((pl.col("model") == model) & (pl.col("regime") == "I") & (pl.col("world") == w))["alpha"].to_numpy()
            a = np.clip(a[~np.isnan(a)], -4, 4)
            vp = ax[1].violinplot([a], positions=[pos], widths=0.8, showextrema=False)
            for b in vp["bodies"]:
                b.set_facecolor(wc); b.set_alpha(0.5); b.set_edgecolor("none")
            ax[1].text(pos, -4.6, w, ha="center", fontsize=6, color=MUTED)
            pos += 1
        p = rep["primary"][model]
        ax[1].errorbar([pos], [p["alpha"]], yerr=[[p["alpha"] - p["jk"]["lo"]], [p["jk"]["hi"] - p["alpha"]]],
                       fmt="o", color=col, ms=5, capsize=0, lw=2)
        ax[1].text(pos, -4.6, name, ha="center", fontsize=6, color=MUTED)
        pos += 1.5
    ax[1].axhline(0, color=GRAY, lw=1); ax[1].axhline(-1, color=AQUA, lw=1, ls=":")
    ax[1].set_ylim(-5, 4.2); ax[1].set_xticks([])
    ax[1].set_ylabel("finite-size exponent α_k"); ax[1].set_title("(b) real α_k (jackknife CI) vs drift D / magnet M",
                                                               fontsize=8, loc="left")
    fig.tight_layout(); fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6))
    per = pl.read_parquet(L.OUT / "replication/periods.parquet").filter(pl.col("regime") == "I")
    for model in ("bge_small", "gte_modernbert"):
        name, col = MOD[model]
        s = per.filter(pl.col("model") == model).drop_nans("rho")
        jit = 0.08 if model == "gte_modernbert" else -0.08
        ax[0].errorbar(s["N_G"].to_numpy() + jit, s["rho"].to_numpy(), yerr=1.96 * s["rho_se"].fill_nan(0).to_numpy(),
                       fmt="o", ms=4, color=col, lw=1, label=name, capsize=0)
    ax[0].axhline(0, color=GRAY, lw=1)
    ax[0].set_xlabel("active population N_G"); ax[0].set_ylabel("ρ_G (≤ 10 active days)")
    ax[0].legend(fontsize=7); ax[0].set_title("(a) per-period near-lag similarity", fontsize=8, loc="left")
    pos = 0
    for model in ("bge_small", "gte_modernbert"):
        name, col = MOD[model]
        for w, wc in (("D", GRAY), ("M", AQUA)):
            a = syn.filter((pl.col("model") == model) & (pl.col("regime") == "I") & (pl.col("world") == w))["ne27_dlnk"].to_numpy()
            a = a[~np.isnan(a)]
            vp = ax[1].violinplot([a], positions=[pos], widths=0.8, showextrema=False)
            for b in vp["bodies"]:
                b.set_facecolor(wc); b.set_alpha(0.5); b.set_edgecolor("none")
            ax[1].text(pos, -4.6, w, ha="center", fontsize=6, color=MUTED)
            pos += 1
        v = nat["NE27"]["by_model"][model]
        jk = v["jk"] or {}
        ax[1].errorbar([pos], [v["dlnk"]], yerr=[[v["dlnk"] - jk.get("lo", v["dlnk"])], [jk.get("hi", v["dlnk"]) - v["dlnk"]]],
                       fmt="o", color=col, ms=5, lw=2)
        ax[1].plot([pos - 0.3, pos + 0.3], [v["magnet_pred"]] * 2, color=AQUA, lw=1, ls=":")
        ax[1].text(pos, -4.6, name, ha="center", fontsize=6, color=MUTED)
        pos += 1.5
    ax[1].axhline(0, color=GRAY, lw=1); ax[1].set_ylim(-5, 4.2); ax[1].set_xticks([])
    ax[1].set_ylabel("NE27 Δln k (post − pre)")
    ax[1].set_title("(b) NE27 (N 4 → 7): real vs drift D / magnet M", fontsize=8, loc="left")
    fig.tight_layout(); fig.savefig(FIG / "summary_obsb.pdf"); plt.close(fig)


if __name__ == "__main__":
    main()
