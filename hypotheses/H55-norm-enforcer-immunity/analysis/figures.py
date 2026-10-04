"""H55 figures (codes and numbers only).
  uv run python hypotheses/H55-norm-enforcer-immunity/analysis/figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h55common as H  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

BLUE, ORANGE, AQUA, GREY, INK, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#9a9893", "#0b0b0b", "#52514e"
FIG = H.HDIR / "figures"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
                     "font.family": "serif"})


def synthetic_fig():
    sd = H.OUT / "synthetic"
    s1 = pl.read_parquet(sd / "s1_reps.parquet")
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.1))
    # (a) friction tests at the #51 structure and small-period structures
    a = s1.group_by("g", "scen", "val").agg((pl.col("p") < 0.05).mean().alias("P1"), (pl.col("p_partial") < 0.05).mean().alias("P1b"),
                                           ((pl.col("p_msg") < 0.05) & (pl.col("gamma") < 0)).mean().alias("P2"))
    labels = [("null0", 0.0, "null"), ("null_style", 0.0, "R-style\nnull"), ("agent", 0.3, "agent\n0.3"), ("agent", 0.6, "agent\n0.6"),
              ("msg", 0.5, "reply\n0.5"), ("msg", 1.0, "reply\n1.0")]
    x = np.arange(len(labels))
    for k, (col, c, mk) in enumerate((("P1", BLUE, "o"), ("P1b", AQUA, "s"), ("P2", ORANGE, "^"))):
        for g, ls, fill in ((51, "-", True), (19, ":", False)):
            ys = [a.filter((pl.col("g") == g) & (pl.col("scen") == sc) & (pl.col("val") == v))[col].item() for sc, v, _ in labels]
            ax[0].plot(x + (k - 1) * 0.12, ys, ls, color=c, marker=mk, ms=4, lw=1.2, mfc=c if fill else "white",
                       label=f"{col} ({'#51' if g == 51 else '#19'})")
    ax[0].axhline(0.05, color=GREY, lw=0.8, ls="--")
    ax[0].set_xticks(x, [l for *_, l in labels], fontsize=6.5)
    ax[0].set_ylabel("rejection rate")
    ax[0].set_ylim(0, 1)
    ax[0].set_title("(a) friction tests, real reply graphs", fontsize=8, loc="left")
    ax[0].legend(fontsize=5.5, ncol=2, loc="upper left")
    # (b) immune contrast power vs beta_C
    for kind, c in (("loop", BLUE), ("blocked", ORANGE)):
        df = pl.read_parquet(sd / f"s2_{kind}_reps.parquet")
        for perf, ls, fill in ((False, "-", True), (True, ":", False)):
            q = df.filter((pl.col("perfect") == perf) & (pl.col("beta_d") == 0.4)).group_by("beta_c").agg(
                ((pl.col("p") < 0.05) & (pl.col("delta") > 0)).mean().alias("pw")).sort("beta_c")
            ax[1].plot(q["beta_c"], q["pw"], ls, color=c, marker="o", ms=4, lw=1.2, mfc=c if fill else "white",
                       label=f"{'loops' if kind == 'loop' else 'blocked'}, {'perfect sensor' if perf else 'Jev sensor'}")
    ax[1].axhline(0.05, color=GREY, lw=0.8, ls="--")
    ax[1].set_xlabel(r"true correction effect $\beta_C$ (logit)")
    ax[1].set_ylabel("power (one-sided, p<0.05)")
    ax[1].set_ylim(0, 1.02)
    ax[1].set_title("(b) immune contrast, real step structure", fontsize=8, loc="left")
    ax[1].legend(fontsize=5.5, loc="lower right")
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "synthetic_validation.pdf")
    plt.close(fig)


def obs_fig():
    per = pl.read_parquet(H.OUT / "replication/per_period.parquet").filter(pl.col("P1_scorable") == True)  # noqa: E712
    summ = json.loads((H.OUT / "replication/summary.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.3), gridspec_kw={"width_ratios": [1.35, 1]})
    # (a) per-period friction rho with Fisher-z CI, ordered by period
    per = per.sort("goal_no")
    r = per["P1_rho"].to_numpy(); n = per["P1_n_agents"].to_numpy()
    z = np.arctanh(np.clip(r, -0.999, 0.999)); se = 1.06 / np.sqrt(np.maximum(n - 3, 1))
    lo, hi = np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)
    x = np.arange(len(r))
    cols = [BLUE if g != 51 else ORANGE for g in per["goal_no"].to_list()]
    ax[0].vlines(x, lo, hi, color=GREY, lw=0.8)
    ax[0].scatter(x, r, c=cols, s=14, zorder=3)
    m = summ["P1"]["meta"]
    ax[0].axhline(0, color=MUTED, lw=0.6)
    ax[0].axhspan(np.tanh(m["mu"] - 1.96 * m["se"]), np.tanh(m["mu"] + 1.96 * m["se"]), color=BLUE, alpha=0.12, lw=0)
    ax[0].axhline(m["rho"], color=BLUE, lw=1.2)
    ax[0].text(0.2, 0.80, f"random-effects mean {m['rho']:.2f} (p {m['p_two']:.2f})", ha="left", fontsize=6.5, color=BLUE,
               bbox=dict(facecolor="white", edgecolor="none", pad=0.5))
    ax[0].text(0.2, 0.93, "friction predicted: > 0", ha="left", fontsize=6.5, color=MUTED)
    ax[0].set_xticks(x, [f"{g}" for g in per["goal_no"].to_list()], fontsize=5.5, rotation=90)
    ax[0].set_ylim(-1.05, 1.05)
    ax[0].set_xlabel("goal period (#51 in orange)")
    ax[0].set_ylabel(r"Spearman $\rho(c_j,\nu_j)$")
    ax[0].set_title("(a) correctors vs negativity they receive", fontsize=8, loc="left")
    # (b) effects on escape: any directed read vs a correction read
    rows = [("addressed, loop", summ["P6_loop_restate_address"], BLUE),
            ("addressed, blocked", summ["P6_blocked_address"], BLUE),
            ("corrected, loop", summ["P4_loop_restate"], ORANGE),
            ("corrected, blocked", summ["P5_blocked"], ORANGE)]
    for k, (lab, d, c) in enumerate(rows):
        y = len(rows) - 1 - k
        ax[1].hlines(y, d["lo"], d["hi"], color=c, lw=1.6)
        ax[1].plot(d["delta"], y, "o", color=c, ms=4.5)
        nn = d.get("n_matched") or d.get("n")
        ax[1].text(0.5, y + 0.18, f"n={nn}", va="bottom", fontsize=5.5, color=MUTED)
    ax[1].axvline(0, color=MUTED, lw=0.6)
    ax[1].set_yticks(range(len(rows)), [r[0] for r in rows][::-1], fontsize=6.3)
    ax[1].set_xlim(-0.6, 0.7)
    ax[1].set_xlabel(r"$\Delta$ escape per step (matched)")
    ax[1].set_title("(b) what ends a failure state", fontsize=8, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)


if __name__ == "__main__":
    which = sys.argv[1:] or ["synthetic"]
    if "synthetic" in which:
        synthetic_fig()
    if "obs" in which:
        obs_fig()
