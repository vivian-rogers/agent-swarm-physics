"""H99 round 2 summary figures (figures/r2_obs.pdf, figures/r2_kernel.pdf) from r2/results.
Usage: uv run python .../r2_figures.py"""
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
import r2run as RR  # noqa: E402

RES = RR.R2 / "results"
FIG = HERE.parent / "figures"
BLUE, ORANGE, GREY, INK, MUTED = "#2a78d6", "#eb6834", "#9a9a94", "#222222", "#6b6b66"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 1.5})


def obs():
    U = pl.read_parquet(RES / "r2_units.parquet").filter(pl.col("regime") == "III")
    fig, ax = plt.subplots(1, 2, figsize=(6.8, 2.5))
    # left: V0 vs V5 (W0-corrected)
    a = ax[0]
    x, y = U["d_V0"].to_numpy(), U["d_V5"].to_numpy()
    s = 8 + 40 * U["n_calls_trim"].to_numpy() / U["n_calls_trim"].max()
    g51 = (U["goal_no"] == 51).to_numpy()
    a.axhline(0, color=GREY, lw=0.6); a.axvline(0, color=GREY, lw=0.6)
    a.plot([-0.2, 0.3], [-0.2, 0.3], color=GREY, lw=0.8, ls="--")
    a.scatter(x[~g51], y[~g51], s=s[~g51], color=BLUE, edgecolor="white", lw=0.6, label="#36–#44")
    a.scatter(x[g51], y[g51], s=s[g51], color=ORANGE, edgecolor="white", lw=0.6, label="#51")
    a.set_xlabel("Δρ₁ before removal (V0, minus W0)"); a.set_ylabel("Δρ₁ after removal (V5, minus W0)")
    a.set_xlim(-0.17, 0.27); a.set_ylim(-0.2, 0.3); a.legend(frameon=False, loc="upper left")
    a.set_title("Collective talk memory survives scheduler removal", fontsize=7, color=INK, loc="left")
    # right: R2 fit vs H67 g_lag
    b = ax[1]
    R = U.filter(pl.col("g1_fit").is_finite() & pl.col("h67_g_lag").is_not_null())
    gx, gy = R["h67_g_lag"].to_numpy(), R["g1_fit"].to_numpy()
    lo, hi = R["g1_fit_lo"].to_numpy(), R["g1_fit_hi"].to_numpy()
    m51 = (R["goal_no"] == 51).to_numpy()
    for k in range(len(gx)):
        if np.isfinite(lo[k]) and np.isfinite(hi[k]):
            b.plot([gx[k], gx[k]], [lo[k], min(hi[k], 0.8)], color=GREY, lw=0.6, zorder=1)
    b.plot([0, 0.6], [0, 0.6], color=GREY, lw=0.8, ls="--")
    b.plot([0, 0.3], [0, 0.6], color=GREY, lw=0.5, ls=":")
    b.plot([0, 0.6], [0, 0.3], color=GREY, lw=0.5, ls=":")
    b.scatter(gx[~m51], gy[~m51], s=14, color=BLUE, edgecolor="white", lw=0.6, zorder=2, label="#36–#44")
    b.scatter(gx[m51], gy[m51], s=14, color=ORANGE, edgecolor="white", lw=0.6, zorder=2, label="#51")
    b.set_xlim(-0.12, 0.42); b.set_ylim(-0.02, 0.8)
    b.set_xlabel("H67 read-out gain g_lag (call clock)"); b.set_ylabel("g₁ needed for the minute-grid Δρ₁ (R2)")
    b.set_title("The minute memory needs exactly the read-out gain", fontsize=7, color=INK, loc="left")
    b.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "r2_obs.pdf")


def kernel():
    s = json.loads((RES / "r2_summary.json").read_text())
    k = s["kernel"]["III"]
    fig, ax = plt.subplots(1, 2, figsize=(6.8, 2.5))
    a = ax[0]
    labels = ["in flight\n(hop 0)", "cross-room\nsame window", "read at call\n(hop 1)", "read one\ncall earlier"]
    named = [k["beta_P0n"], None, k["beta_R1n"], k["beta_R2n"]]
    unnamed = [k["beta_P0u"], k["beta_X1"], k["beta_R1u"], k["beta_R2u"]]
    xs = np.arange(4)
    w = 0.36
    for off, vals, col, lab in ((-w / 2, named, ORANGE, "message names the recipient"),
                                (w / 2, unnamed, BLUE, "unnamed (cross-room bar: all messages)")):
        for xi, v in zip(xs, vals):
            if v is None:
                continue
            a.bar(xi + off, v["re"], width=w - 0.04, color=col, label=lab if xi == 2 else None)
            a.plot([xi + off] * 2, [v["lo"], v["hi"]], color=INK, lw=0.8)
    a.axhline(0, color=GREY, lw=0.6)
    a.set_xticks(xs); a.set_xticklabels(labels)
    a.set_ylabel("Δ P(talk) per message (regime III, pooled)")
    a.set_title("Talk responds to reads, at the next call, by address", fontsize=7, color=INK, loc="left")
    a.set_ylim(-0.025, 0.105)
    a.legend(frameon=False, loc="upper left", fontsize=6)
    b = ax[1]
    r4 = s.get("R4") or {}
    ng = (r4.get("nudge_G51") or {}).get("ya")
    if ng:
        G, S = np.array(ng["G"]), np.array(ng["S"])
        t = np.arange(len(G))
        b.axhline(0, color=GREY, lw=0.6)
        b.plot(t, G, color=ORANGE, label="nudge response G(k), receiving call")
        p = int(ng.get("peak", 0) or 0)
        if S[p] > 0 and G[p] > 0:
            b.plot(t[p:], G[p] * S[p:] / S[p], color=BLUE, ls="--", label="Onsager: spontaneous regression from the peak")
        b.set_xlabel("minutes after the receiving call"); b.set_ylabel("extra active-minute probability")
        b.set_title("#51 nudges on the receiving call", fontsize=7, color=INK, loc="left")
        b.set_ylim(-0.1, 0.2)
        b.legend(frameon=False, loc="upper right", fontsize=6)
    fig.tight_layout()
    fig.savefig(FIG / "r2_kernel.pdf")


if __name__ == "__main__":
    obs()
    kernel()
