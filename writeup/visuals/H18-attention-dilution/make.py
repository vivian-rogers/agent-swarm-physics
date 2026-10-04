"""H18 writeup visual: attention dilution. Per-sender uptake falls as ~k^-0.66; replies go to the newest messages.

    uv run python writeup/visuals/H18-attention-dilution/make.py

Reads only H18's processed outputs (data/processed/H18-attention-dilution/): r1b/G<NN>/fits_mention.json (binned
response curves on ledger k), r1b/summary_r1b.json (per-period beta, D2 timer-wake beta, pooled beta), r1b/G51 talks and
pending tables (reply parent by queue rank; codes only, no text) and synthetic/B.parquet (generative-agent nulls).
Non-holdout only (H18 drops held-out days before building; G51's held-out tail is excluded there). No animation.
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
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import vstyle as vs  # noqa: E402
from common import holdout_mask  # noqa: E402

D = ROOT / "data/processed/H18-attention-dilution"
PERIODS = ["G24", "G25", "G26", "G27", "G30", "G31", "G35", "G36", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
MK = {"I": "s", "II": "D", "II/III": "D", "III": "o"}


def load():
    S = json.loads((D / "r1b/summary_r1b.json").read_text())
    per = {p["period"]: p for p in S["periods"] if p["period"] in PERIODS}
    F = {g: json.loads((D / f"r1b/{g}/fits_mention.json").read_text()) for g in PERIODS}
    B = pl.read_parquet(D / "synthetic/B.parquet").filter(pl.col("variant") == "main")
    return S, per, F, B


def panel_curves(ax, F, S):
    for g in PERIODS:
        cv = [c for c in F[g]["curves"] if c["n"] >= 30 and c["oe"] > 0]
        k = np.array([c["kmean"] for c in cv]); o = np.array([c["oe"] for c in cv])
        if g == "G51":
            lo = np.array([c["oe_lo"] for c in cv]); hi = np.array([c["oe_hi"] for c in cv])
            ax.fill_between(k, lo, hi, color=vs.COUPLING, alpha=0.25, lw=0, zorder=3)
            ax.plot(k, o, "o-", color=vs.COUPLING, lw=1.6, ms=3, zorder=4)
            ax.annotate("G51", (k[-1], o[-1]), xytext=(3, -2), textcoords="offset points", fontsize=6.5,
                        color=vs.COUPLING)
        else:
            ax.plot(k, o, "-", color=vs.COUPLING, lw=0.6, alpha=0.35, zorder=2)
    kk = np.logspace(0, np.log10(200), 50)
    k0 = 8.0
    ax.plot(kk, (kk / k0) ** (-1.0), color=vs.INK2, lw=0.9, ls=":", zorder=5)
    ax.axhline(1, color=vs.MUTED, lw=1.0, ls="--", zorder=1)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(0.85, 300); ax.set_ylim(0.12, 6)
    ax.text(1.0, 1.08, "no budget (null)", fontsize=6, color=vs.INK2, va="bottom")
    ax.text(1.05, 0.2, "$k^{-1}$ (literal $J/N$)", fontsize=6, color=vs.INK2)
    from matplotlib.ticker import FuncFormatter, NullFormatter
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.set_yticks([0.2, 0.5, 1, 2, 5])
    ax.set_xlabel("pending messages $k$ at the talk call")
    ax.set_ylabel("response / no-budget expectation")
    ax.set_title("(a) dilution, 16 periods", loc="left")


def panel_beta(ax, per, S, B):
    rc = B.filter(pl.col("scenario") == "react_const")
    ec = B.filter(pl.col("scenario") == "exo_const")
    n1 = (float(rc["beta_D1"].min()), float(rc["beta_D1"].max()))
    n2 = (float(rc["beta_D2w300"].min()), float(rc["beta_D2w300"].max()))
    y = np.arange(len(PERIODS))[::-1]
    ax.axvspan(*n1, color=vs.NULL, alpha=0.55, lw=0, zorder=0)
    ax.axvspan(*n2, color=vs.NULL, alpha=0.30, lw=0, zorder=0)
    ax.axvline(0, color=vs.INK2, lw=0.5); ax.axvline(1, color=vs.INK2, lw=0.6, ls=":")
    for yi, g in zip(y, PERIODS):
        m = per[g]["mention"]
        reg = per[g]["regime"]
        ax.plot([m["beta_lo"], m["beta_hi"]], [yi + 0.15] * 2, color=vs.COUPLING, lw=1.0)
        ax.plot(m["beta"], yi + 0.15, MK.get(reg, "o"), color=vs.COUPLING, ms=3)
        d2 = m["d2"]
        if d2["beta"] is not None and d2["status"] != "underpowered":
            lo, hi = max(d2["lo"], -0.9), min(d2["hi"], 1.45)
            ax.plot([lo, hi], [yi - 0.2] * 2, color=vs.C["pink"], lw=1.0)
            ax.plot(d2["beta"], yi - 0.2, "^", color=vs.C["pink"], ms=3.4)
    pm = S["pooled_mention"]
    ax.axvline(pm["mean"], color=vs.COUPLING, lw=0.8, ls="--")
    ax.text(pm["mean"] - 0.03, len(PERIODS) - 0.45, "pooled %.2f" % pm["mean"], fontsize=5.6, color=vs.COUPLING,
            ha="right", va="bottom")
    ax.set_yticks(y); ax.set_yticklabels([f"{g} {per[g]['regime']}" for g in PERIODS], fontsize=5.6)
    ax.set_xlim(-0.9, 1.45); ax.set_ylim(-0.8, len(PERIODS) + 0.2)
    ax.set_xlabel(r"exponent $\hat\beta$ (uptake $\propto k^{-\beta}$)")
    ax.set_title("(b) beyond which null?", loc="left")
    ax.grid(axis="y", visible=False)
    h = [Line2D([], [], marker="o", color=vs.COUPLING, ms=3, lw=1.0),
         Line2D([], [], marker="^", color=vs.C["pink"], ms=3.4, lw=1.0),
         Patch(color=vs.NULL, alpha=0.55), Patch(color=vs.NULL, alpha=0.30)]
    ax.legend(h, ["all talk calls (D1)", "timer wakes (D2)", "timing null, D1", "timing null, D2"],
              loc="upper center", bbox_to_anchor=(0.42, -0.2), ncol=2, fontsize=5.6, handlelength=1.3,
              columnspacing=0.8, borderaxespad=0.1)
    ax.annotate("", (1.45, y[PERIODS.index("G40")] - 0.2), xytext=(1.3, y[PERIODS.index("G40")] - 0.2),
                arrowprops=dict(arrowstyle="->", color=vs.C["pink"], lw=0.8))
    return n1, n2, float(ec["beta_D1"].mean())


def recency(nboot=200, seed=20261004):
    T = pl.read_parquet(D / "r1b/G51/talks.parquet").select("talk_id", "k", "pt_date", "goal_no")
    assert not any(holdout_mask(T["pt_date"].to_list(), T["goal_no"].to_list()))
    P = pl.read_parquet(D / "r1b/G51/pending.parquet", columns=["talk_id", "rank", "scored", "resp_reply"])
    P = P.join(T, on="talk_id").filter(pl.col("scored"))
    out = {}
    rng = np.random.default_rng(seed)
    for lo, hi in ((5, 8), (9, 16)):
        q = P.filter(pl.col("k").is_between(lo, hi))
        agg = q.group_by("pt_date", "rank").agg(pl.col("resp_reply").sum().alias("y"), pl.len().alias("n"))
        days = sorted(agg["pt_date"].unique().to_list())
        ranks = np.arange(1, hi + 1)
        Y = np.zeros((len(days), hi)); N = np.zeros((len(days), hi))
        di = {d: i for i, d in enumerate(days)}
        for d, r, yv, nv in agg.iter_rows():
            if r <= hi:
                Y[di[d], r - 1] += yv; N[di[d], r - 1] += nv
        est = Y.sum(0) / np.maximum(N.sum(0), 1)
        bs = []
        for _ in range(nboot):
            w = np.bincount(rng.integers(0, len(days), len(days)), minlength=len(days))
            bs.append((w[:, None] * Y).sum(0) / np.maximum((w[:, None] * N).sum(0), 1))
        bs = np.array(bs)
        keep = N.sum(0) >= 300
        out[(lo, hi)] = dict(r=ranks[keep], est=est[keep], lo=np.percentile(bs, 2.5, 0)[keep],
                             hi=np.percentile(bs, 97.5, 0)[keep], mean=Y.sum() / N.sum())
    return out


def panel_recency(ax, R):
    for (lo, hi), mk, ls in (((5, 8), "s", "--"), ((9, 16), "o", "-")):
        d = R[(lo, hi)]
        ax.fill_between(d["r"], d["lo"] * 100, d["hi"] * 100, color=vs.COUPLING, alpha=0.2, lw=0)
        ax.plot(d["r"], d["est"] * 100, ls=ls, marker=mk, color=vs.COUPLING, ms=2.8, lw=1.1,
                mfc="white" if lo == 5 else vs.COUPLING, label=f"$k$ = {lo}–{hi}")
        ax.axhline(d["mean"] * 100, color=vs.MUTED, lw=0.9, ls=":" if lo == 5 else "--")
    ax.text(15.8, R[(9, 16)]["mean"] * 100 + 0.4, "no recency\n(rank-blind)", fontsize=5.6, color=vs.INK2,
            ha="right", va="bottom")
    ax.set_xlabel("queue rank of the message (1 = newest)")
    ax.set_ylabel("chosen as reply parent (%)")
    ax.set_title("(c) G51: replies go to the newest", loc="left")
    ax.set_xlim(0.5, 16.5); ax.set_ylim(0, 16)
    ax.legend(loc="upper right", fontsize=6, handlelength=1.6)


def main():
    vs.use()
    S, per, F, B = load()
    fig = plt.figure(figsize=(vs.W["double"], 2.8))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.0, 1.05], wspace=0.42, left=0.065, right=0.99, bottom=0.27,
                          top=0.91)
    panel_curves(fig.add_subplot(gs[0]), F, S)
    n1, n2, ec = panel_beta(fig.add_subplot(gs[1]), per, S, B)
    R = recency()
    panel_recency(fig.add_subplot(gs[2]), R)
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    print("pooled", S["pooled_mention"], "null D1", n1, "null D2", n2, "exo_const D1", ec)
    print({k: (np.round(v["est"][:3], 3), round(v["mean"], 3)) for k, v in R.items()})


if __name__ == "__main__":
    main()
