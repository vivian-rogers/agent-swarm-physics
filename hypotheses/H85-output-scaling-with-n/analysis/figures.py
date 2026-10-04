"""H85 summary figures: figures/summary_obs.pdf (unit scaling, two outputs) and figures/summary_obsb.pdf (exponents
against predictions; within-day room contrasts).
Usage: uv run python hypotheses/H85-output-scaling-with-n/analysis/figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
import matplotlib.ticker
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h85lib as L  # noqa: E402

INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
COL = {"I": "#2a78d6", "II": "#1baf7a", "III": "#eb6834"}
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})
FIG = L.ROOT / "hypotheses/H85-output-scaling-with-n/figures"


def obs():
    u = pl.read_parquet(L.DATA / "units.parquet")
    rep = json.loads((L.DATA / "replication/replication.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(4.2, 2.0))
    for a, (y, lab, key) in zip(ax, ((u["msg"] / u["T_h"], "messages per hour", "msg"),
                                     (u["ment"] / u["msg"], "addressed pairs per message", None))):
        for r in ("I", "II", "III"):
            s = u["regime"] == r
            a.scatter(u["N"].filter(s), y.filter(s), s=10, color=COL[r], edgecolor="white", linewidth=0.4, label=f"regime {r}", zorder=3)
            x = np.log(u["N"].filter(s).to_numpy())
            yy = np.log(y.filter(s).to_numpy())
            if len(x) > 5:
                b = np.polyfit(x, yy, 1)
                xs = np.linspace(x.min(), x.max(), 10)
                a.plot(np.exp(xs), np.exp(np.polyval(b, xs)), color=COL[r], lw=1.2)
        a.set_xscale("log"); a.set_yscale("log")
        a.set_xticks([4, 8, 16, 32]); a.set_xticklabels(["4", "8", "16", "32"])
        a.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        a.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        a.set_xlabel("active population $N$"); a.set_ylabel(lab)
        a.grid(color=GRID, lw=0.5, which="both"); a.set_axisbelow(True)
    m = rep["levels"]["msg"]["M1"]
    ax[0].set_title(f"(a) $\\beta_{{msg}}$ = {m['beta']:.2f} [{m['ci_lo']:.2f}, {m['ci_hi']:.2f}]", fontsize=7, loc="left")
    d = rep["mechanism"]["ment_per_msg"]
    ax[1].set_title(f"(b) slope {d['est']:.2f} [{d['ci'][0]:.2f}, {d['ci'][1]:.2f}]", fontsize=7, loc="left")
    ax[0].set_yticks([50, 100, 200]); ax[0].set_yticklabels(["50", "100", "200"])
    ax[1].set_yticks([0.1, 0.3, 1]); ax[1].set_yticklabels(["0.1", "0.3", "1"])
    ax[0].legend(fontsize=6, loc="lower right", handletextpad=0.2)
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "summary_obs.pdf")


def obsb():
    rep = json.loads((L.DATA / "replication/replication.json").read_text())
    nat = json.loads((L.DATA / "natives/natives.json").read_text())
    lev, me = rep["levels"], rep["mechanism"]
    rows = [("$\\beta$ messages", lev["msg"]["M1"]["beta"], (lev["msg"]["M1"]["ci_lo"], lev["msg"]["M1"]["ci_hi"]), 1.0),
            ("$\\beta$ addressed pairs", lev["ment"]["M1"]["beta"], (lev["ment"]["M1"]["ci_lo"], lev["ment"]["M1"]["ci_hi"]), 1.34),
            ("$\\beta$ reply parents", lev["reply"]["M1"]["beta"], (lev["reply"]["M1"]["ci_lo"], lev["reply"]["M1"]["ci_hi"]), 1.25),
            ("$\\Delta\\beta$ addressing/msg", me["ment_per_msg"]["est"], me["ment_per_msg"]["ci"], me["pred_dbeta_ment"]["est"]),
            ("$\\Delta\\beta$ replies/msg", me["reply_per_msg"]["est"], me["reply_per_msg"]["ci"], me["pred_dbeta_reply"]["est"]),
            ("$\\gamma_k$ pending set", me["k"]["est"], me["k"]["ci"], 1.0)]
    fig, ax = plt.subplots(1, 2, figsize=(4.2, 2.0), gridspec_kw={"width_ratios": [1.15, 1]})
    a = ax[0]
    for i, (lab, est, ci, pred) in enumerate(rows[::-1]):
        a.plot(ci, [i, i], color="#2a78d6", lw=1.6, solid_capstyle="round")
        a.plot(est, i, "o", color="#2a78d6", ms=4, zorder=3)
        a.plot(pred, i, "D", color="#eb6834", ms=3.5, zorder=4)
    a.set_yticks(range(len(rows))); a.set_yticklabels([r[0] for r in rows[::-1]], fontsize=6.3)
    a.axvline(0, color=MUTED, lw=0.5); a.axvline(1, color=GRID, lw=0.8, ls="--")
    a.set_xlabel("exponent (71 units, 95% cluster CI)")
    a.plot([], [], "o", color="#2a78d6", ms=4, label="observed"); a.plot([], [], "D", color="#eb6834", ms=3.5, label="predicted")
    a.legend(fontsize=6, loc="lower right", handletextpad=0.2)
    a.set_title("(a)", fontsize=7, loc="left")
    b = ax[1]
    keys = [g for g, v in nat["rooms"].items() if g.startswith("G") and v["identified"]]
    for j, (k, c, lab) in enumerate((("msg", "#2a78d6", "messages"), ("ment_per_msg", "#eb6834", "addr. per msg"))):
        for i, g in enumerate(keys):
            v = nat["rooms"][g][k]
            b.plot([i + (j - 0.5) * 0.25] * 2, v["ci"], color=c, lw=1.4)
            b.plot(i + (j - 0.5) * 0.25, v["est"], "o", color=c, ms=3.5, label=lab if i == 0 else None)
        p = nat["rooms"]["pooled_RE"][k]
        b.plot([len(keys) + (j - 0.5) * 0.25] * 2, p["ci"], color=c, lw=2.2)
        b.plot(len(keys) + (j - 0.5) * 0.25, p["est"], "s", color=c, ms=4)
    b.set_xticks(range(len(keys) + 1)); b.set_xticklabels(keys + ["pooled"], fontsize=6.3)
    b.axhline(1, color=GRID, lw=0.8, ls="--"); b.axhline(0, color=MUTED, lw=0.5)
    b.set_ylabel("within-day room exponent"); b.set_ylim(-1.0, 2.6)
    b.legend(fontsize=6, loc="upper center", ncol=2, handletextpad=0.2, columnspacing=0.8)
    b.set_title("(b)", fontsize=7, loc="left")
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "summary_obsb.pdf")


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    obs(); obsb()
