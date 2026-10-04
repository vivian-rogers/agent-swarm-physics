"""H125 figures: figures/summary_obs.pdf ((a) mean excess alignment relative to days 4-5 by active day, both models, with the
M_osc and M_fade shapes from the synthetic as references; (b) per-kickoff U against the placebo-day band) and
figures/synthetic_compact.pdf (P1 pass rate per synthetic world)."""
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
sys.path.insert(0, str(HERE))
import h125lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "writeup/visuals"))
import vstyle as vs  # noqa: E402

FIG = HERE.parent / "figures"


def obs():
    vs.use()
    ser = json.loads((L.DATA / "NE34/series.json").read_text())
    d = pl.read_parquet(L.DATA / "NE34/kickoffs_all_configs.parquet")
    plc = pl.read_parquet(L.DATA / "NE34/placebo_all_configs.parquet")
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.4))
    for cfg, col, lab, off in (("bge_white", vs.C["blue"], "bge", -0.08), ("gte_white", vs.C["orange"], "gte", 0.08)):
        days = np.arange(1, 11)
        M = np.full((len(ser), 10), np.nan)
        for j, (des, v) in enumerate(ser.items()):
            prof = v[cfg]["day"]
            for d_ in days:
                x = prof.get(str(d_))
                if x and x[2] >= 3:
                    M[j, d_ - 1] = x[0]
        m = np.nanmean(M, 0); n = np.isfinite(M).sum(0); se = np.nanstd(M, 0, ddof=1) / np.sqrt(np.maximum(n, 1))
        ax[0].errorbar(days + off, m, yerr=1.645 * se, color=col, marker="o", ms=3, lw=1.2, capsize=1.5, label=f"{lab} (kickoffs per day: {n[0]}–{n[-1]})")
    ax[0].axhline(0, color=vs.MUTED, lw=0.8)
    ax[0].axvspan(1.5, 3.5, color=vs.NULL, alpha=0.25, lw=0)
    ax[0].text(2.5, ax[0].get_ylim()[1] * 0.9, "undershoot\nwindow", ha="center", va="top", fontsize=6.5, color=vs.INK2)
    ax[0].set_xlabel("active day after the kickoff"); ax[0].set_ylabel("excess alignment − days 4–5 level")
    ax[0].set_title("(a) day-level response (mean over kickoffs, 90% CI)", loc="left")
    ax[0].legend(loc="upper right", fontsize=6)
    b = d.filter(pl.col("cfg") == "bge_white").sort("U")
    x = np.arange(b.height)
    pu = plc.filter(pl.col("cfg") == "bge_white")["U"].drop_nans().to_numpy()
    lo, md, hi = np.percentile(pu, [5, 50, 95])
    ax[1].axhspan(lo, hi, color=vs.NULL, alpha=0.35, lw=0, label=f"placebo days 5–95% (n = {len(pu)})")
    ax[1].axhline(md, color=vs.MUTED, lw=0.8)
    cols = {"I": vs.C["blue"], "II": vs.C["green"], "III": vs.C["red"]}
    ax[1].errorbar(x, b["U"], yerr=1.645 * b["se_U"].to_numpy(), fmt="none", ecolor=vs.MUTED, lw=0.8)
    for rg in ("I", "II", "III"):
        m = (b["regime"] == rg).to_numpy()
        ax[1].scatter(x[m], b["U"].to_numpy()[m], s=12, color=cols[rg], label=f"regime {rg}", zorder=3)
    ax[1].axhline(0, color=vs.INK2, lw=0.6)
    ax[1].set_xticks(x); ax[1].set_xticklabels([str(g) for g in b["goal_no"]], fontsize=5, rotation=90)
    ax[1].set_xlabel("kickoff of goal period # (sorted by U)"); ax[1].set_ylabel("undershoot U (bge)")
    ax[1].set_title("(b) U per kickoff vs placebo days", loc="left")
    ax[1].legend(fontsize=5.5, loc="upper left", ncol=2)
    fig.tight_layout()
    vs.save(fig, FIG / "summary_obs")


def synth():
    vs.use()
    fig, ax = plt.subplots(1, 1, figsize=(3.4, 2.0))
    names = ["W_fade_3", "W_fade_8", "W_drift", "W_tod", "W_rekick", "W_noisy", "W_osc_0.2", "W_osc_0.5", "W_osc_weak_0.5"]
    lab = ["fade 3h", "fade 8h", "drift", "time of day", "re-kick", "noisy", "osc ζ0.2", "osc ζ0.5", "osc ζ0.5 weak"]
    for j, (cfg, col) in enumerate((("bge_white", vs.C["blue"]), ("gte_white", vs.C["orange"]))):
        r = json.loads((L.DATA / f"synthetic/results_{cfg}.json").read_text())["worlds"]
        ax.bar(np.arange(len(names)) + (j - 0.5) * 0.38, [r[n]["P1"] for n in names], width=0.38, color=col,
               label=cfg.split("_")[0] + " calibration")
    ax.axvline(5.5, color=vs.MUTED, lw=0.8, ls="--")
    ax.set_xticks(range(len(names))); ax.set_xticklabels(lab, rotation=45, ha="right", fontsize=6)
    ax.set_ylabel("P1 pass rate"); ax.set_ylim(0, 1.05)
    ax.text(2.5, 0.9, "no inertia (size)", ha="center", fontsize=6.5); ax.text(7, 0.9, "inertia (power)", ha="center", fontsize=6.5)
    ax.legend(fontsize=6, loc="center left")
    fig.tight_layout()
    vs.save(fig, FIG / "synthetic_compact")


if __name__ == "__main__":
    synth()
    obs()
