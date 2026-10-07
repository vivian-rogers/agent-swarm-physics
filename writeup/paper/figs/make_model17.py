"""Model 17 (collective modes vs a calibrated random-matrix edge) paper figure, from H12 round 1b.

(a) Per scored unit (24 non-holdout units), top eigenvalue / calibrated 95% surrogate edge for three channels:
    activity (fixed table, trimmed block-shift edge, DQ8), talk (trimmed block-shift edge, DQ8), content (bge, cross-day
    edge). Count of units above the edge printed over each channel.
(b) #12 debates: participation ratio of content (bge, H12 ruler) while the motion is on vs in the 20 min after the
    verdict, paired per debate.

Plotting only, from existing outputs (no new analysis):
  data/processed/H12-groupthink-dimensional-collapse/r1b/unit_table.parquet
  data/processed/H12-groupthink-dimensional-collapse/r1b/native/g12_debates.parquet, r1b/native/native.json
Usage (repo root): uv run python writeup/paper/figs/make_model17.py
Output: writeup/paper/figs/model17_modes.{pdf,png}
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
import vstyle as vs  # noqa: E402

D = ROOT / "data/processed/H12-groupthink-dimensional-collapse/r1b"
OUT = Path(__file__).resolve().parent / "model17_modes"
CARD_COUNTS = {"activity": "7/24", "talk": "21/24", "content": "24/24"}   # H12 card, round 1b


def panel_a(ax):
    u = pl.read_parquet(D / "unit_table.parquet").filter(pl.col("scored")).sort("unit")
    chans = (("activity", "l1_edge_trim", "activity\nblock-shift edge"),
             ("talk", "talk_l1_edge_trim", "talk\nblock-shift edge"),
             ("content", "content_l1_edge", "content (bge)\ncross-day edge"))
    ax.axhspan(0.5, 1.0, color=vs.NULL, alpha=0.28, lw=0, zorder=0)
    ax.axhline(1, color=vs.INK2, lw=0.8, zorder=1)
    counts = {}
    rng = np.random.default_rng(0)
    for k, (name, col, _) in enumerate(chans):
        y = u[col].to_numpy().astype(float)
        assert np.isfinite(y).all() and len(y) == 24
        jit = (rng.permutation(len(y)) / (len(y) - 1) - 0.5) * 0.42
        up = y > 1
        ax.scatter(k + jit[up], y[up], s=13, color=vs.COUPLING, edgecolor="white", linewidth=0.3, zorder=3)
        ax.scatter(k + jit[~up], y[~up], s=13, facecolor="white", edgecolor=vs.MUTED, linewidth=0.8, zorder=3)
        ax.plot([k - 0.28, k + 0.28], [np.median(y)] * 2, color=vs.INK, lw=1.2, zorder=4)
        c = f"{int(up.sum())}/{len(y)}"
        counts[name] = (c, float(np.median(y)), float(y.min()), float(y.max()))
        if c != CARD_COUNTS[name]:
            print(f"WARNING: {name} count {c} differs from the card's {CARD_COUNTS[name]}")
        ax.text(k, 2.75, c, ha="center", va="bottom", fontsize=7.5, color=vs.INK)
    ax.set_yscale("log")
    ax.set_ylim(0.8, 3.3)
    ax.set_yticks([0.8, 1, 1.5, 2, 3]); ax.set_yticklabels(["0.8", "1", "1.5", "2", "3"])
    ax.minorticks_off()
    ax.set_xlim(-0.55, 2.55)
    ax.set_xticks(range(3)); ax.set_xticklabels([c[2] for c in chans], fontsize=7)
    ax.grid(axis="x", visible=False)
    ax.text(2.53, 0.83, "below edge", ha="right", va="bottom", fontsize=6.5, color=vs.INK2)
    ax.text(-0.5, 2.75, "above edge:", ha="left", va="bottom", fontsize=6.5, color=vs.INK2)
    ax.set_ylabel(r"top eigenvalue / edge, $\lambda_1/\lambda_+$")
    ax.set_title("(a) collective mode per unit (24 units)", loc="left")
    return counts


def panel_b(ax):
    d = pl.read_parquet(D / "native/g12_debates.parquet")
    nat = json.loads((D / "native/native.json").read_text())["G12_motion"]["bge_h12"]
    ok = d.filter(pl.col("pr_on_bge_h12").is_not_nan() & pl.col("pr_off_bge_h12").is_not_nan())
    off, on = ok["pr_off_bge_h12"].to_numpy(), ok["pr_on_bge_h12"].to_numpy()
    for a, b in zip(off, on):
        ax.plot([0, 1], [a, b], color=vs.MUTED, lw=0.8, zorder=2)
    ax.scatter(np.zeros(len(off)), off, s=14, facecolor="white", edgecolor=vs.INK2, linewidth=0.8, zorder=3)
    ax.scatter(np.ones(len(on)), on, s=14, color=vs.FIELD, edgecolor="white", linewidth=0.3, zorder=3)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["after\nverdict", "motion\non"], fontsize=7)
    ax.set_xlim(-0.35, 1.9)
    ax.grid(axis="x", visible=False)
    lo = min(off.min(), on.min()); hi = max(off.max(), on.max())
    ax.set_ylim(lo - 0.08 * (hi - lo), hi + 0.12 * (hi - lo))
    n_low, n = nat["n_on_lower"], nat["n_usable"]
    rel, p = nat["median_rel"], nat["wilcoxon_p_less"]
    ax.text(1.12, lo + 0.62 * (hi - lo), f"lower in {n_low}/{n}\nmedian {rel * 100:+.0f}%\nWilcoxon $p$ = {p:.3f}".replace("-", "−"),
            ha="left", va="center", fontsize=6.8, color=vs.INK)
    ax.set_ylabel("participation ratio (bge)")
    ax.set_title("(b) #12 debates: content", loc="left")
    return dict(n_low=n_low, n=n, rel=rel, p=p, off=off, on=on, n_debates=d.height)


def main():
    vs.use()
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.45), gridspec_kw={"width_ratios": [1.75, 1]})
    ca = panel_a(ax[0])
    cb = panel_b(ax[1])
    fig.tight_layout(w_pad=1.5)
    vs.save(fig, OUT)
    for k, v in ca.items():
        print(k, "above edge", v[0], "median", round(v[1], 3), "range", round(v[2], 3), round(v[3], 3))
    print("G12:", f"{cb['n_low']}/{cb['n']} lower (of {cb['n_debates']} debates)", "median rel", round(cb["rel"], 4),
          "p", round(cb["p"], 4))
    print("off", np.round(cb["off"], 2).tolist()); print("on ", np.round(cb["on"], 2).tolist())


if __name__ == "__main__":
    main()
