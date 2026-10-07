"""H140 round-1 figures: figures/summary_obs.pdf (per-unit self-weight slope and read-weight exponent) and
figures/summary_synth.pdf (synthetic w1 by world, registered vs A1 estimator)."""
from __future__ import annotations

import glob
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H140-degroot-readout-self-weight"
FIG = HERE.parent / "figures"
BLUE, ORANGE, GRAY, INK = "#2a78d6", "#eb6834", "#8a8a85", "#333333"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": GRAY, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False})


def units():
    U = {}
    for p in glob.glob(str(DATA / "results/units_G*.json")):
        U.update(json.load(open(p)))
    order = sorted(U, key=lambda x: (int("".join(c for c in x if c.isdigit())), x))
    return U, order


def obs():
    U, order = units()
    S = json.load(open(DATA / "results/score.json"))
    test = [u for u in order if U[u]["bge"]["n_scored"] >= 300]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8))
    y = np.arange(len(test))
    a0 = ax[0]
    a0.axvspan(0.5, 1.5, color=GRAY, alpha=0.15, lw=0)
    a0.axvline(0, color=GRAY, lw=0.8, ls=":")
    for i, u in enumerate(test):
        for off, tag, col, mk in ((-0.15, "bge", BLUE, "o"), (0.15, "gte", ORANGE, "s")):
            f = U[u][tag].get("A1", {})
            if f.get("w1") is None:
                continue
            a0.plot([f["w1_lo"], f["w1_hi"]], [i + off] * 2, color=col, lw=1.2)
            a0.plot(f["w1"], i + off, mk, color=col, ms=4)
    p = S["P1_A1_bge"]
    a0.plot([p["lo"], p["hi"]], [-1.2] * 2, color=INK, lw=2); a0.plot(p["est"], -1.2, "D", color=INK, ms=5)
    a0.set_yticks(list(y) + [-1.2]); a0.set_yticklabels(test + ["pool (25)"])
    a0.set_xlim(-1.3, 1.6); a0.set_xlabel(r"self-weight slope $\hat w_1$ (A1, 95% CI)")
    a0.text(1.0, -1.2, "HH383 band", ha="center", color=INK, fontsize=7)
    a0.invert_yaxis()
    a1 = ax[1]
    a1.axvspan(0.15, 0.40, color=GRAY, alpha=0.15, lw=0)
    a1.axvline(1, color=GRAY, lw=0.8, ls=":")
    for i, u in enumerate(test):
        f = U[u]["bge"].get("A1", {})
        ident = U[u]["bge"].get("identified")
        col = BLUE if ident else GRAY
        a1.plot([f["a_lo"], f["a_hi"]], [i] * 2, color=col, lw=1.2)
        a1.plot(f["a"], i, "o", color=col, ms=4, mfc=col if ident else "white")
    p = S["P2_a_bge"]
    a1.plot([p["lo"], p["hi"]], [-1.2] * 2, color=INK, lw=2); a1.plot(p["est"], -1.2, "D", color=INK, ms=5)
    a1.set_yticks(list(y) + [-1.2]); a1.set_yticklabels(test + ["pool (10 id.)"])
    a1.set_xlim(-0.6, 1.6); a1.set_xlabel(r"read-weight exponent $\hat a$ (bge; filled = identified)")
    a1.text(0.275, -2.0, "P2 band", ha="center", color=INK, fontsize=7)
    a1.set_ylim(len(test) - 0.5, -2.5)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf"); fig.savefig(FIG / "summary_obs.png", dpi=150)


def synth():
    d = pl.read_parquet(DATA / "synthetic/runs_main.parquet")
    worlds = ["W0", "W-DG", "W-DGh", "W-lin", "W-well", "W-field"]
    truth = {"W0": 0, "W-DG": 1, "W-DGh": 0.5, "W-lin": 1, "W-well": 0, "W-field": 0}
    fig, ax = plt.subplots(1, 1, figsize=(3.4, 2.6))
    for j, (tag, col, off) in enumerate((("main", GRAY, -0.18), ("A1", BLUE, 0.18))):
        for i, w in enumerate(worlds):
            x = d.filter(pl.col("world") == w)[f"{tag}_w1"].drop_nulls().to_numpy()
            q = np.percentile(x, [10, 50, 90])
            ax.plot([i + off] * 2, [q[0], q[2]], color=col, lw=1.5)
            ax.plot(i + off, q[1], "o", color=col, ms=4, label=("registered" if tag == "main" else "A1") if i == 0 else None)
    for i, w in enumerate(worlds):
        ax.plot([i - 0.35, i + 0.35], [truth[w]] * 2, color=INK, lw=0.8, ls="--")
    ax.set_xticks(range(len(worlds))); ax.set_xticklabels(worlds, rotation=30)
    ax.set_ylabel(r"$\hat w_1$ (median, 10–90%)"); ax.legend(frameon=False, fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG / "summary_synth.pdf"); fig.savefig(FIG / "summary_synth.png", dpi=150)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    obs(); synth()
