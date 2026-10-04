"""H62 figures: figures/summary_obs.pdf (real data) and figures/summary_obs2.pdf (synthetic + dilution).

  uv run python hypotheses/H62-ideas-travel-reply-graph/analysis/figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
DATA = ROOT / "data/processed/H62-ideas-travel-reply-graph"
FIG = HYP / "figures"
REP, ROOM = "#2a78d6", "#eb6834"
REGM = {"I": "o", "II": "s", "III": "^"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e9e7e1"
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "font.family": "serif"})


def _ci(r, key):
    return r.get(f"{key}_lo", np.nan), r.get(f"{key}_hi", np.nan)


def fig1():
    rows = [r for r in json.loads((DATA / "results/periods.json").read_text()) if r.get("eligible")]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.4))
    a = ax[0]
    x = np.arange(len(rows))
    for i, r in enumerate(rows):
        for k, c, dx in (("A_hr_rec_rep", REP, -0.15), ("A_hr_rec_room", ROOM, 0.15)):
            lo, hi = _ci(r, k)
            a.plot([i + dx, i + dx], [lo, hi], color=c, lw=1.0)
            a.plot(i + dx, r[k], marker=REGM[r["regime"]], ms=3.8, color=c, mec="white", mew=0.3)
    a.set_yscale("log")
    a.axhline(1, color=INK2, lw=0.8)
    a.set_xticks(x); a.set_xticklabels([str(r["goal"]) for r in rows], fontsize=5.5, rotation=90)
    a.plot([], [], color=REP, marker="o", ls="", label="reply channel (HR$_{\\rm rep}$)")
    a.plot([], [], color=ROOM, marker="o", ls="", label="room-only (HR$_{\\rm room}$)")
    a.legend(frameon=False, fontsize=6, loc="upper left")
    a.set_ylabel("adoption hazard ratio vs no recent read")
    a.set_xlabel("goal period (marker: regime I ○, II □, III △)")
    a.grid(axis="y", color=GRID, lw=0.6)
    a.set_title("(a) exposure locking by channel (recency window)", fontsize=7.5, loc="left")
    b = ax[1]
    for i, r in enumerate(rows):
        for k, c, dx in (("C_rep", REP, -0.15), ("C_room", ROOM, 0.15)):
            if k not in r:
                continue
            lo, hi = r.get(f"{k}_wlo", np.nan), r.get(f"{k}_whi", np.nan)
            pw = r.get("B_rep_power" if k == "C_rep" else "B_room_power")
            b.plot([i + dx, i + dx], [lo, hi], color=c, lw=0.9, alpha=1 if pw else 0.4)
            b.plot(i + dx, r[k], marker=REGM[r["regime"]], ms=3.8, color=c if pw else "white", mec=c, mew=0.8)
    b.set_yscale("log")
    b.axhline(1, color=INK2, lw=0.8)
    b.set_ylim(0.1, 100)
    b.set_xticks(x); b.set_xticklabels([str(r["goal"]) for r in rows], fontsize=5.5, rotation=90)
    b.set_ylabel("seen ÷ unread-only hazard at 300 s")
    b.set_xlabel("goal period (open: < 10 adoptions in a cell)")
    b.grid(axis="y", color=GRID, lw=0.6)
    b.set_title("(b) in-flight placebo per channel (C)", fontsize=7.5, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")


def fig2():
    s1 = pl.read_parquet(DATA / "synthetic/s1.parquet")
    rows = [r for r in json.loads((DATA / "results/periods.json").read_text()) if r.get("eligible")]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.3))
    a = ax[0]
    truths = ["field", "room", "thread", "reply"]
    stats = [("Lam", "Λ", "#2a78d6"), ("T_ratio", "T$_{\\rm rep}$/T$_{\\rm room}$", "#1baf7a"), ("C_rep", "C$_{\\rm rep}$", "#eb6834")]
    w = 0.26
    for j, (k, lab, c) in enumerate(stats):
        for i, t in enumerate(truths):
            v = s1.filter(pl.col("truth") == t)[k].drop_nulls().drop_nans().to_numpy()
            q = np.percentile(v, [25, 50, 75])
            a.plot([i + (j - 1) * w] * 2, [q[0], q[2]], color=c, lw=2.2, alpha=0.6)
            a.plot(i + (j - 1) * w, q[1], "o", color=c, ms=4, label=lab if i == 0 else None)
    a.set_yscale("log"); a.axhline(1, color=INK2, lw=0.8)
    a.set_xticks(range(len(truths))); a.set_xticklabels(["pure field", "room contagion", "thread field", "reply contagion"], fontsize=6.3)
    a.set_ylabel("estimate (median, IQR; 18 runs)")
    a.legend(frameon=False, fontsize=6, loc="upper left")
    a.set_title("(a) synthetic truths on real schedules (G20, G38, G41)", fontsize=7.5, loc="left")
    b = ax[1]
    for r in rows:
        if not np.isfinite(r.get("T_ratio", np.nan)):
            continue
        b.plot(r["N_room"], r["T_rep"], marker=REGM[r["regime"]], color=REP, ls="", ms=4, mec="white", mew=0.3)
        b.plot(r["N_room"], r["T_room"], marker=REGM[r["regime"]], color=ROOM, ls="", ms=4, mec="white", mew=0.3)
    b.set_xscale("log"); b.set_yscale("log")
    b.plot([], [], color=REP, marker="o", ls="", label="T$_{\\rm rep}$ (reply channel)")
    b.plot([], [], color=ROOM, marker="o", ls="", label="T$_{\\rm room}$ (room-only)")
    b.legend(frameon=False, fontsize=6, loc="lower left")
    b.set_xlabel("agents posting per room-day (median)")
    b.set_ylabel("T = P(adopt in 3 calls | 1st read)")
    from matplotlib.ticker import ScalarFormatter, NullFormatter
    b.xaxis.set_major_formatter(ScalarFormatter()); b.xaxis.set_minor_formatter(NullFormatter())
    b.set_xticks([4, 6, 10, 20])
    b.grid(color=GRID, lw=0.6)
    b.set_title("(b) per-edge transmissibility vs room size", fontsize=7.5, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs2.pdf")


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    fig1()
    fig2()
    print("figures written")
