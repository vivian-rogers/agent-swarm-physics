"""H52 figures: observables (per-period premium by channel) and synthetic validation (compact).

Writes figures/h52_obs.pdf, figures/h52_synth.pdf (+ png). Palette: the dataviz reference categorical slots 1-3
(blue = human, orange = bot, aqua = agent naming reference), neutral ink for text.
Usage: uv run python hypotheses/H52-humans-loud-agents/analysis/figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h52lib as L  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

BLUE, ORANGE, AQUA, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.linewidth": 0.6, "font.family": "DejaVu Sans"})
NAMES = {"con": "content pull (DiD χ, cosine)", "rep": "reply probability", "act": "activity (min / 30 min)",
         "st": "stance (P(sup) − P(opp))"}


def obs():
    T = pl.read_parquet(L.OUT / "period_table.parquet")
    S = json.loads((L.OUT / "summary.json").read_text())
    per = [p for p in L.REPLICATION if p in set(T["period"].to_list())]
    fig, axs = plt.subplots(2, 2, figsize=(7.0, 4.2))
    for ax, oc in zip(axs.ravel(), ("con", "rep", "act", "st")):
        ax.axhline(0, color=MUTED, lw=0.6)
        for i, p in enumerate(per):
            for c, col, off in (("human", BLUE, -0.15), ("bot", ORANGE, 0.15)):
                r = T.filter((pl.col("period") == p) & (pl.col("outcome") == oc) & (pl.col("cls") == c))
                if r.height == 0:
                    continue
                r = r.row(0, named=True)
                if r["lo"] is None or not np.isfinite(r["lo"]):
                    continue
                ax.plot([i + off, i + off], [r["lo"], r["hi"]], color=col, lw=0.9, alpha=0.9)
                ax.plot(i + off, r["att"], "o", ms=3.6, color=col if r["powered"] else "white", mec=col, mew=0.9)
        # pooled per regime
        xs = len(per) + 0.6
        for k, (reg, mk) in enumerate((("I", "D"), ("III", "s"))):
            for c, col, off in (("human", BLUE, -0.15), ("bot", ORANGE, 0.15)):
                pr = S["pooled"].get(f"{oc}_{c}_{reg}")
                if not pr or pr.get("pooled") is None or not np.isfinite(pr["pooled"]):
                    continue
                x = xs + k + off
                ax.plot([x, x], pr["ci"], color=col, lw=1.4)
                ax.plot(x, pr["pooled"], mk, ms=4.5, color=col)
        ax.set_xticks(list(range(len(per))) + [xs, xs + 1])
        ax.set_xticklabels(per + ["pool I", "pool III"], rotation=90, fontsize=5.5)
        n_I = sum(1 for p in per if int(p[1:3]) < 37)
        ax.axvline(n_I - 0.5, color=GRID, lw=0.8)
        ax.set_title(NAMES[oc], fontsize=7, color=INK, loc="left")
        ax.grid(axis="y", color=GRID, lw=0.5)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        if oc == "act":
            ax.set_ylim(-3, 3)
    h1 = plt.Line2D([], [], marker="o", color=BLUE, ls="-", ms=4, label="human − matched agent (filled: powered)")
    h2 = plt.Line2D([], [], marker="o", color=ORANGE, ls="-", ms=4, label="bot − matched agent")
    fig.legend(handles=[h1, h2], loc="upper center", ncol=2, frameon=False, fontsize=6.5)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    for ext in ("pdf", "png"):
        fig.savefig(L.FIG / f"h52_obs.{ext}", dpi=200)
    plt.close(fig)


def synth():
    df = pl.read_parquet(L.OUT / "synthetic" / "replicates.parquet").filter((pl.col("cls") == "human") & (pl.col("subset") == "all"))
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.1))
    cases = [(sk, lab) for sk in ("G51", "G04") for lab in ("confounded", "real")]
    for ax, scn in zip(axs, ("S0", "S1")):
        ax.axhline(0, color=MUTED, lw=0.6)
        xt = []
        for j, oc in enumerate(("con", "con_dd", "rep", "act", "st")):
            for k, (sk, lab) in enumerate(cases):
                sub = df.filter((pl.col("outcome") == oc) & (pl.col("skeleton") == sk) & (pl.col("labels") == lab)
                                & (pl.col("scenario") == scn))
                if sub.height == 0:
                    continue
                truth = sub["truth"].mean()
                scale = 1.0 if oc != "act" else 0.03     # activity in units of 1/0.03 min to share an axis
                x = j * 5 + k
                est_col = "att_bc" if oc == "act" else "att"
                e = (sub[est_col] - sub["truth"]).to_numpy() * scale
                nv = (sub["naive"] - sub["truth"]).to_numpy() * scale
                ax.plot([x] * len(nv), nv, "_", color=MUTED, ms=5, alpha=0.6)
                ax.plot([x] * len(e), e, ".", color=BLUE if oc != "con" else ORANGE, ms=3, alpha=0.8)
                ax.plot(x, np.nanmean(e), "o", color=BLUE if oc != "con" else ORANGE, ms=4, mec="white", mew=0.5)
            xt.append(j * 5 + 1.5)
        ax.set_xticks(xt)
        ax.set_xticklabels(["H30 orth χ", "DiD χ", "reply", "activity\n(×0.03 min)", "stance"], fontsize=6)
        ax.set_title(("null (π = 0): estimate − truth" if scn == "S0" else "planted premium: estimate − truth"), fontsize=7,
                     loc="left", color=INK)
        ax.grid(axis="y", color=GRID, lw=0.5)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.set_ylim(-0.08, 0.08)
    h1 = plt.Line2D([], [], marker="o", color=BLUE, ls="", ms=4, label="matched (CEM; activity bias-corrected)")
    h2 = plt.Line2D([], [], marker="o", color=ORANGE, ls="", ms=4, label="H30 orthogonalized χ (rejected)")
    h3 = plt.Line2D([], [], marker="_", color=MUTED, ls="", ms=6, label="naive contrast")
    fig.legend(handles=[h1, h2, h3], loc="upper center", ncol=3, frameon=False, fontsize=6)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    for ext in ("pdf", "png"):
        fig.savefig(L.FIG / f"h52_synth.{ext}", dpi=200)
    plt.close(fig)


def synth_compact():
    """Page-2 figure (column width): mean estimate - truth (+-1 SD over replicates) per estimator, for the four
    skeleton x label cells, null (circles) and planted premium (squares)."""
    df = pl.read_parquet(L.OUT / "synthetic" / "replicates.parquet").filter((pl.col("cls") == "human") & (pl.col("subset") == "all"))
    cells = [("G51", "real", BLUE), ("G51", "confounded", "#7fb0ea"), ("G04", "real", ORANGE), ("G04", "confounded", "#f4a582")]
    ests = [("con", "H30 χ"), ("con_dd", "DiD χ"), ("rep", "reply"), ("act", "activity/30"), ("st", "stance")]
    fig, ax = plt.subplots(figsize=(3.5, 1.85))
    ax.axhline(0, color=MUTED, lw=0.6)
    for j, (oc, lab) in enumerate(ests):
        for k, (sk, lb, col) in enumerate(cells):
            for m, (scn, mk) in enumerate((("S0", "o"), ("S1", "s"))):
                sub = df.filter((pl.col("outcome") == oc) & (pl.col("skeleton") == sk) & (pl.col("labels") == lb) & (pl.col("scenario") == scn))
                if sub.height == 0:
                    continue
                est = sub["att_bc"] if oc == "act" else sub["att"]
                e = (est - sub["truth"]).to_numpy() * (1 / 30 if oc == "act" else 1)
                x = j + (k - 1.5) * 0.17 + (m - 0.5) * 0.07
                ax.plot([x, x], [np.mean(e) - np.std(e), np.mean(e) + np.std(e)], color=col, lw=0.8)
                ax.plot(x, np.mean(e), mk, ms=2.8, color=col, mec="white", mew=0.3)
    ax.set_xticks(range(len(ests)))
    ax.set_xticklabels([e[1] for e in ests], fontsize=5.8)
    ax.set_ylabel("estimate − truth", fontsize=5.8)
    ax.tick_params(axis="y", labelsize=5.5)
    ax.grid(axis="y", color=GRID, lw=0.5)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    hs = [plt.Line2D([], [], color=c, marker="o", ls="", ms=3, label=f"{sk} {lb}") for sk, lb, c in cells]
    ax.legend(handles=hs, fontsize=4.8, frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.18))
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(L.FIG / f"h52_synth_compact.{ext}", dpi=220)
    plt.close(fig)


def obs_compact():
    """Page-1 figure: forest plots of the reply and content premia for the key contrasts."""
    S = json.loads((L.OUT / "summary.json").read_text())
    N = S["native"]
    r51 = json.loads((L.OUT / "G51" / "results.json").read_text())
    r04 = json.loads((L.OUT / "G04" / "results.json").read_text())
    r05 = json.loads((L.OUT / "G05" / "results.json").read_text())

    def g(d):
        return (d.get("att"), (d.get("ci") or [np.nan, np.nan]))

    def gp(d):
        return (d.get("pooled"), d.get("ci"))
    rep = [("humans, regime I (14 periods)", gp(S["pooled"]["rep_human_I"]), BLUE),
           ("humans, G51", g(r51["primary"]["rep"]["human"]["all"]), BLUE),
           ("  G51 on-role messages", g(N["n2_G51_roles"]["on_role"]["rep"]), BLUE),
           ("  G51 off-role messages", g(N["n2_G51_roles"]["off_role"]["rep"]), BLUE),
           ("  G51 role-conflicting third", g(N["n2_G51_roles"]["bottom_tercile"]["rep"]), BLUE),
           ("elected agent leader (G26)", g(N["n4_leaders"]["G26"]["rep"]["leader"]), AQUA),
           ("appointed lead designers (G35)", g(N["n4_leaders"]["G35"]["rep"]["leader"]), AQUA),
           ("fine-tuned leader (G44)", g(N["n4_leaders"]["G44"]["rep"]["leader"]), AQUA),
           ("bot, named target (12 periods)", gp(S["extra"]["bot_rep_named_allperiods"]), ORANGE)]
    bd04 = r04["boundary"]["human_minus_agent_unnamed"]; bd05 = r05["boundary"]["human_minus_agent_unnamed"]
    con = [("humans G51, DiD χ (primary)", g(r51["primary"]["con"]["human"]["all"]), BLUE),
           ("humans G51, H30 orthogonalized χ", g(r51["robustness"]["con_h30orth"]["human"]["all"]), BLUE),
           ("humans G51, gte-modernbert", g(r51["robustness"]["con_gte"]["human"]["all"]), BLUE),
           ("humans G51, joint per call", g(r51["robustness"]["con_jd"]["human"]["all"]), BLUE),
           ("humans regime I, DiD χ (bias ≈ −0.024)", gp(S["pooled"]["con_human_I"]), BLUE),
           ("humans G04, H29 boundary design", (bd04["diff"], bd04["ci"]), BLUE),
           ("humans G05, H29 boundary design", (bd05["diff"], bd05["ci"]), BLUE),
           ("appointed lead designers (G35)", g(N["n4_leaders"]["G35"]["con"]["leader"]), AQUA),
           ("elected agent leader (G26)", g(N["n4_leaders"]["G26"]["con"]["leader"]), AQUA)]
    fig, axs = plt.subplots(2, 1, figsize=(3.5, 3.5))
    for ax, rows, title in ((axs[0], rep, "(a) reply premium (probability)"), (axs[1], con, "(b) content premium (cosine)")):
        ax.axvline(0, color=MUTED, lw=0.6)
        for i, (lab, (e, c), col) in enumerate(rows):
            y = len(rows) - 1 - i
            if e is None or c[0] is None:
                continue
            ax.plot(c, [y, y], color=col, lw=1.2)
            ax.plot(e, y, "o", ms=3.8, color=col)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=6.4)
        ax.set_title(title, fontsize=6.8, loc="left", color=INK)
        ax.grid(axis="x", color=GRID, lw=0.5)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
        ax.tick_params(axis="x", labelsize=5.8)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(L.FIG / f"h52_obs_compact.{ext}", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    L.FIG.mkdir(parents=True, exist_ok=True)
    which = sys.argv[1:] or ["obs", "synth"]
    if "synth" in which:
        synth()
        synth_compact()
    if "obs" in which:
        obs()
        obs_compact()
