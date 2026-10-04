"""H94 summary figures.
  figures/summary_obs.pdf    bits per work quantum by unit: what ownership, rooms and run persistence explain of
                             I(agent; repo), and the residual above the persistence floor
  figures/summary_kappa.pdf  concentration kappa of work episodes per unit vs the neutral (BE) band and the synthetic
                             references (Polya 1, herding beyond neutral, planned teams)
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H94-maxent-work-allocation"
FIG = HERE.parent / "figures"
PERIODS = [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]
OWN_C, ROOM_C, PERS_C, RES_C = "#3a6ea5", "#8fb8de", "#c9c9c9", "#d1495b"


def units():
    rows = []
    for g in PERIODS:
        p = DATA / "results" / f"G{g:02d}.json"
        if not p.exists():
            continue
        r = json.loads(p.read_text())
        for u, v in r["units"].items():
            if not v.get("testable"):
                continue
            rows.append({"g": g, "unit": u, **{k: v.get(k) for k in ("D1", "D2", "D3", "pfloor1", "pfloor3", "lam_own",
                                                                      "lam_own_lo", "lam_own_hi", "own_unit", "N")},
                         "kappa": (v.get("kappa") or {}).get("kappa"), "be": (v.get("kappa") or {}).get("be_band"),
                         "kappa_nn": (v.get("kappa_no_named") or {}).get("kappa")})
    return rows


def fig_bits(rows):
    rows = sorted(rows, key=lambda r: (r["own_unit"], r["g"], r["unit"]))
    fig, ax = plt.subplots(figsize=(4.2, 2.5))
    x = np.arange(len(rows))
    for i, r in enumerate(rows):
        own = max(r["D1"] - r["D2"], 0)
        room = max(r["D2"] - r["D3"], 0)
        pers = min(r["pfloor3"], r["D3"])
        res = max(r["D3"] - r["pfloor3"], 0)
        b = 0
        for val, c in ((own, OWN_C), (room, ROOM_C), (pers, PERS_C), (res, RES_C)):
            ax.bar(i, val, bottom=b, color=c, width=0.8, linewidth=0)
            b += val
    ax.set_xticks(x)
    ax.set_xticklabels([r["unit"] for r in rows], rotation=90, fontsize=6)
    ax.set_ylabel("bits per work quantum", fontsize=7)
    ax.tick_params(axis="y", labelsize=6)
    k = sum(1 for r in rows if not r["own_unit"])
    ax.axvline(k - 0.5, color="k", lw=0.6, ls=":")
    ax.text(k / 2 - 0.5, ax.get_ylim()[1] * 0.97, "shared", ha="center", va="top", fontsize=6)
    ax.text(k + (len(rows) - k) / 2 - 0.5, ax.get_ylim()[1] * 0.97, "own-artifact", ha="center", va="top", fontsize=6)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=OWN_C, label="ownership"), Patch(color=ROOM_C, label="room"),
                       Patch(color=PERS_C, label="run persistence (null)"), Patch(color=RES_C, label="residual")],
              fontsize=5.5, frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.9), ncol=1)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")


def fig_kappa(rows):
    rows = sorted(rows, key=lambda r: (r["own_unit"], r["g"], r["unit"]))
    syn = pl.read_parquet(DATA / "synthetic" / "summary.parquet")
    ref = {w: float(syn.filter(pl.col("world") == w)["kappa"].median()) for w in ("S2", "S3", "S4")}
    fig, ax = plt.subplots(figsize=(4.2, 2.0))
    for i, r in enumerate(rows):
        if r["be"]:
            ax.plot([i, i], r["be"], color="#bbbbbb", lw=3, solid_capstyle="butt")
        if r["kappa"] is not None:
            ax.plot(i, r["kappa"], "o", ms=3.5, color=OWN_C if r["own_unit"] else RES_C)
        if r["kappa_nn"] is not None and r["kappa_nn"] != r["kappa"]:
            ax.plot(i, r["kappa_nn"], "x", ms=3, color="k", mew=0.7)
    for w, lab, ls in (("S2", "neutral copying", "-"), ("S3", "herding beyond neutral", "--"), ("S4", "planned teams", ":")):
        ax.axhline(ref[w], color="#555555", lw=0.6, ls=ls)
        ax.text(len(rows) - 0.4, ref[w], lab, fontsize=5, va="bottom", ha="right", color="#555555")
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([r["unit"] for r in rows], rotation=90, fontsize=6)
    ax.set_ylabel(r"$\kappa$ (work episodes)", fontsize=7)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], marker="o", color=RES_C, ls="", ms=3, label="shared units"),
                       Line2D([], [], marker="o", color=OWN_C, ls="", ms=3, label="own-artifact units"),
                       Line2D([], [], marker="x", color="k", ls="", ms=3, label="without kickoff-named repos"),
                       Line2D([], [], color="#bbbbbb", lw=3, label="BE (neutral) 95% band")],
              fontsize=5, frameon=False, loc="lower left", ncol=2)
    ax.tick_params(axis="y", labelsize=6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "summary_kappa.pdf")


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    rows = units()
    fig_bits(rows)
    fig_kappa(rows)
    print(len(rows), "units")
