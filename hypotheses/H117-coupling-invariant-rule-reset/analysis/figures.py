"""H117 summary figures: observed coupling-shift Q vs the placebo pools; synthetic size and power."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "data/processed/H117-coupling-invariant-rule-reset"
FIG = ROOT / "hypotheses/H117-coupling-invariant-rule-reset/figures"
B, O, G, INK = "#2a78d6", "#eb6834", "#1baf7a", "#52514e"
plt.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": INK,
                     "axes.labelcolor": "#0b0b0b", "xtick.color": INK, "ytick.color": INK})


def obs():
    df = pl.read_parquet(D / "splits.parquet").filter(pl.col("Q").is_not_null())
    pl_ = df.filter(pl.col("kind") == "placebo")
    st = df.filter(pl.col("kind") != "placebo")
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.4))
    for reg, y0 in (("I", 0), ("III", 1)):
        v = pl_.filter((pl.col("regime") == reg) & (pl.col("k") == 2))["Q"].to_numpy()
        ax[0].scatter(v, y0 + np.random.default_rng(1).uniform(-0.15, 0.15, len(v)), s=8, color="#bdbcb6",
                      label="placebo splits" if reg == "I" else None, zorder=1)
        ax[0].plot([np.quantile(v, 0.95)] * 2, [y0 - 0.3, y0 + 0.3], color=INK, lw=1.2)
    cnt = {"I": 0, "III": 0}
    for r in st.filter(pl.col("k") == 2).sort("Q").iter_rows(named=True):
        y0 = 0 if r["regime"] == "I" else 1
        c = O if r["kind"] == "native" else B
        yy = y0 + 0.35 + 0.12 * (cnt[r["regime"]] % 4)
        cnt[r["regime"]] += 1
        ax[0].scatter(r["Q"], yy, s=18, color=c, zorder=3, edgecolor="white", lw=0.6)
        ax[0].annotate(r["name"], (r["Q"], yy), xytext=(5, -2), textcoords="offset points", fontsize=5.5)
    ax[0].set_yticks([0, 1]); ax[0].set_yticklabels(["regime I", "regime III"])
    ax[0].set_xlabel("coupling-shift Q (fixed pairs, k = 2)"); ax[0].set_ylim(-0.5, 2.0)
    ax[0].scatter([], [], color=B, s=22, label="replication step"); ax[0].scatter([], [], color=O, s=22, label="native")
    ax[0].legend(frameon=False, fontsize=5.5, loc="lower right")
    ax[0].set_title("(a) J shift at field steps vs placebo splits (line: 95th pct)", fontsize=7, loc="left")
    ax[1].scatter(pl_["F"], pl_["Q"], s=8, color="#bdbcb6", label="placebo splits")
    s2 = st.filter(pl.col("k") == 2)
    ax[1].scatter(s2["F"], s2["Q"], s=22, color=B, edgecolor="white", lw=0.6, label="steps")
    for r in s2.filter(pl.col("name").is_in(["NE17", "G42", "NE07"])).iter_rows(named=True):
        ax[1].annotate(r["name"], (r["F"], r["Q"]), xytext=(3, 2), textcoords="offset points", fontsize=5.5)
    ax[1].set_xlabel("field-shift F (first stage)"); ax[1].set_ylabel("Q")
    ax[1].legend(frameon=False, fontsize=5.5)
    ax[1].set_title("(b) field steps are no larger than day-to-day field changes", fontsize=7, loc="left")
    fig.tight_layout(); fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)


def syn():
    s = json.loads((D / "synthetic/p0_summary.json").read_text())
    sk = ["NE17", "NE06", "NE38", "NE38k3"]
    lab = ["#38 (N 6)", "regime I (N 8)", "#51 k=2 (N 19)", "#51 k=3 (N 22)"]
    worlds = [("field", "field step", "#bdbcb6"), ("field_drive", "field + drive", INK),
              ("jstep_0.6", "J step ±0.6", B), ("jstep_1.2", "J step ±1.2", O)]
    fig, ax = plt.subplots(figsize=(7.0, 2.0))
    w = 0.19
    for k, (key, nm, c) in enumerate(worlds):
        v = [s[x][key]["rej_block"] for x in sk]
        ax.bar(np.arange(4) + (k - 1.5) * w, v, w * 0.9, color=c, label=nm)
    ax.axhline(0.05, color=INK, lw=0.8, ls=":"); ax.axhline(0.8, color=INK, lw=0.8, ls="--")
    ax.set_xticks(range(4)); ax.set_xticklabels(lab); ax.set_ylabel("rejection rate of Q test")
    ax.legend(frameon=False, ncol=4, fontsize=6, loc="upper left"); ax.set_ylim(0, 1.1)
    fig.tight_layout(); fig.savefig(FIG / "summary_synthetic.pdf"); plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    obs(); syn()
