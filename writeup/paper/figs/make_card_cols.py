"""Single-column figures for writeup/paper drawn from card results (read-only), in the writeup style (vstyle).

    uv run python writeup/paper/figs/make_card_cols.py

  h67_named_col.pdf   regime-III units: read-out loop gain g split into named and unnamed reads (H67 units.parquet)
  h67_dial_col.pdf    per period: read-out gain g_lag against the equal-time talk dial g_eq (H67 periods.parquet)
Reserved periods are excluded by the cards' own builds (asserted here with holdout_mask where a day column exists).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "infra/shared"))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
import vstyle as vs  # noqa: E402
from common import load_holdout  # noqa: E402

REG_C = {"I": vs.C["green"], "II": vs.C["pink"], "III": vs.C["blue"]}
REG_M = {"I": "s", "II": "D", "III": "o"}
HELD = set(load_holdout()["goal_periods_held_out"])


def h67_named():
    u = pl.read_parquet(ROOT / "data/processed/H67-lagged-criticality-dial/results/units.parquet")
    u = u.filter(pl.col("ok").fill_null(False) & (pl.col("regime") == "III")).sort("goal_no", "unit_id")
    assert not set(u["goal_no"].to_list()) & HELD
    fig, ax = plt.subplots(figsize=(vs.W["single"], 2.0))
    x = np.arange(u.height)
    ax.bar(x, u["g_named"], color=vs.COUPLING, width=0.7, label="reads that name the reader")
    ax.bar(x, u["g_unnamed"], bottom=u["g_named"], color=vs.C["sky"], width=0.7, label="other reads")
    ax.errorbar(x, u["g"], yerr=[u["g"] - u["g_lo"], u["g_hi"] - u["g"]], fmt="none", ecolor=vs.INK, elinewidth=0.6)
    ax.axhline(float(u["g"].median()), color=vs.INK2, lw=0.7, ls=":")
    ax.text(2.6, float(u["g"].median()) + 0.008, f"median {float(u['g'].median()):.2f}", ha="left",
            fontsize=6.3, color=vs.INK2)
    ax.set_xticks(x)
    ax.set_xticklabels(u["unit_id"].to_list(), rotation=90, fontsize=5.2)
    ax.set_xlabel("regime-III unit (goal period, part)", labelpad=1)
    ax.set_ylabel("loop gain $g$ per message")
    ax.set_ylim(0, max(0.32, float(u["g_hi"].max()) + 0.02))
    ax.legend(loc="upper left", fontsize=6.3, handlelength=1.2)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    vs.save(fig, HERE / "h67_named_col")
    plt.close(fig)
    sh = (u["g_named"] / u["g"]).median()
    print(f"h67 named: {u.height} units, median named share of g = {float(sh):.2f}")


def h67_dial():
    P = pl.read_parquet(ROOT / "data/processed/H67-lagged-criticality-dial/results/periods.parquet")
    assert not set(P["goal_no"].to_list()) & HELD
    fig, ax = plt.subplots(figsize=(vs.W["single"], 2.35))
    lo, hi = -0.12, 0.47
    ax.plot([lo, hi], [lo, hi], color=vs.INK2, lw=0.7, ls="--")
    ax.text(0.36, 0.375, "read-out = equal-time", rotation=45, transform_rotates_text=True, fontsize=6.0,
            color=vs.INK2, ha="center", va="bottom")
    ax.axhline(0, color=vs.INK2, lw=0.5)
    ax.axvline(0, color=vs.INK2, lw=0.5)
    for r in ("I", "II", "III"):
        s = P.filter(pl.col("regime") == r)
        ax.errorbar(s["g_eq"], s["g"], yerr=[s["g"] - s["g_lo"], s["g_hi"] - s["g"]], fmt=REG_M[r], ms=3.6,
                    mfc=REG_C[r], mec="white", mew=0.4, ecolor=REG_C[r], elinewidth=0.7, capsize=0,
                    label=f"regime {r} ({s.height})", zorder=3)
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel("equal-time talk dial $g_{\\rm eq}$ (same calls)")
    ax.set_ylabel("read-out loop gain $g$")
    ax.legend(loc="upper left", fontsize=6.3, handletextpad=0.3)
    fig.tight_layout()
    vs.save(fig, HERE / "h67_dial_col")
    plt.close(fig)
    print("h67 dial:", P.group_by("regime").agg(pl.col("g").median(), pl.col("g_eq").median()).sort("regime").to_dicts())


if __name__ == "__main__":
    vs.use()
    h67_named(); h67_dial()
