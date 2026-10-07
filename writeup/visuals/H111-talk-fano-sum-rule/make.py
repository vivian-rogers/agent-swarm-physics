"""H111 visual: the talk fluctuation-response sum rule Phi = 1/(1 - g_lag)^2.

    uv run python writeup/visuals/H111-talk-fano-sum-rule/make.py

Inputs (read only; non-holdout by construction, asserted again here):
  data/processed/H111-talk-fano-sum-rule/results/units.parquet   per-unit Phi(10 min), CIs, Phi_pred, g_lag (H67), null
  data/processed/H111-talk-fano-sum-rule/results/summary.json    pooled r_F per regime
Panel (a) is a simulation (linear Hawkes swarm in one room); panel (b) is the measured village quantity.
Outputs: fig.pdf / fig.png (double column, a|b) and fig_col.pdf (single column, a over b) for writeup/paper.
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import vstyle as vs  # noqa: E402
from common import holdout_mask, load_holdout  # noqa: E402

D = ROOT / "data/processed/H111-talk-fano-sum-rule/results"
REG_C = {"I": vs.C["green"], "II": vs.C["pink"], "III": vs.C["blue"]}
REG_M = {"I": "s", "II": "D", "III": "o"}


def phi_pred(g, n):
    """Card's room-adjusted mean-field prediction for one room of n agents."""
    g = np.asarray(g, float)
    a = 1 / (1 - g) ** 2
    return n * a / (a + (n - 1) / (1 + g / (n - 1)) ** 2)


def simulate(g, n=15, mu=0.06, T=24000, win=10, block=60, seed=0):
    """Linear Hawkes swarm on a 1-min clock: each talk event of agent j raises every other agent's
    next-minute rate by g/(n-1) (branching ratio g). Returns Phi(win) after 60-min block demeaning."""
    rng = np.random.default_rng(seed)
    x = np.zeros((T, n))
    prev = np.zeros(n)
    for t in range(T):
        lam = mu + g / (n - 1) * (prev.sum() - prev)
        prev = rng.poisson(lam)
        x[t] = prev
    c = x.reshape(T // win, win, n).sum(1)               # counts per window
    nb = block // win
    c = c[: (len(c) // nb) * nb].reshape(-1, nb, n)
    c = c - c.mean(1, keepdims=True)                      # remove fields slower than an hour
    c = c.reshape(-1, n)
    return (c.sum(1) ** 2).sum() / (c ** 2).sum()


def load():
    held = set(load_holdout()["goal_periods_held_out"])
    u = pl.read_parquet(D / "units.parquet")
    assert not set(u["goal_no"].to_list()) & held
    assert not any(holdout_mask(u["first_day"].cast(pl.Utf8).to_list(), u["goal_no"].to_list()))
    u = u.filter((pl.col("nwin_10") >= 40) & pl.col("r_F").is_finite())
    s = json.loads((D / "summary.json").read_text())["scores"]
    return u, s


def panel_a(ax):
    """(a) simulation: the sum rule in a linear Hawkes swarm."""
    n = 15
    gg = np.linspace(0, 0.62, 200)
    ax.plot(gg, phi_pred(gg, n), color=vs.INK, lw=1.3, zorder=2)
    ax.plot(gg, 1 / (1 - gg) ** 2, color=vs.INK2, lw=0.8, ls=":", zorder=2)
    gs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    reps = np.array([[simulate(g, n=n, seed=100 * i + k) for k in range(8)] for i, g in enumerate(gs)])
    m = reps.mean(1)
    lo, hi = np.percentile(reps, [2.5, 97.5], axis=1)
    ax.axhspan(lo[0], hi[0], color=vs.NULL, alpha=0.45, lw=0, zorder=0)
    ax.text(0.615, hi[0] + 0.03, "no coupling (g = 0), 95% of runs", ha="right", va="bottom", fontsize=6.0, color=vs.INK2)
    ax.errorbar(gs, m, yerr=[m - lo, hi - m], fmt="o", ms=3.5, mfc="white", mec=vs.COUPLING, mew=1.0,
                ecolor=vs.COUPLING, elinewidth=0.8, capsize=0, zorder=3)
    ax.text(0.40, 3.3, r"sum rule $\Phi_{pred}(g)$" + "\n(15 agents, one room)", fontsize=6.6, ha="right", color=vs.INK)
    ax.text(0.585, 5.6, r"$1/(1-g)^2$", fontsize=6.6, ha="right", color=vs.INK2)
    ax.axvspan(0.03, 0.29, color=vs.COUPLING, alpha=0.08, lw=0, zorder=0)
    ax.text(0.16, 4.3, "village\nregime III\n$g_{lag}$ range", ha="center", fontsize=6.0, color=vs.COUPLING)
    ax.set_xlim(-0.02, 0.63)
    ax.set_ylim(0.6, 6.6)
    ax.set_xlabel("loop gain $g$ (simulated)")
    ax.set_ylabel(r"collective Fano ratio $\Phi$(10 min)")
    ax.set_title("(a) simulation: linear Hawkes talk swarm", loc="left")
    ax.legend(handles=[Line2D([], [], marker="o", ls="", mfc="white", mec=vs.COUPLING, label="simulated (8 runs, 95%)")],
              loc="lower right", bbox_to_anchor=(1.0, 0.1))
    return gs, m, n


def panel_b(bx, u, s):
    """(b) village: observed vs predicted Fano ratio, per unit."""
    lim = (0.45, float(u["phi_10"].max()) + 0.12)
    xx = np.linspace(*lim, 10)
    bx.fill_between(xx, 0.8 * xx, 1.2 * xx, color=vs.COUPLING, alpha=0.07, lw=0, zorder=0)
    bx.plot(xx, xx, color=vs.INK, lw=1.0, zorder=1)
    q95 = float(u["phi_null_q95"].median())
    bx.axhspan(lim[0], q95, color=vs.NULL, alpha=0.35, lw=0, zorder=0)
    bx.text(0.86, (q95 - lim[0]) / (lim[1] - lim[0]) - 0.015, "independent agents:\nbelow null 95th pct.",
            transform=bx.transAxes, ha="right", va="top", fontsize=5.8, color=vs.INK2)
    for r in ("I", "II", "III"):
        v = u.filter(pl.col("regime") == r)
        g, se, npres = v["g"].to_numpy(), v["g_se"].to_numpy(), v["N_present"].to_numpy()
        xp = v["phi_pred"].to_numpy()
        # 95% interval of the prediction from g's SE (delta method on the card's formula)
        dphi = (phi_pred(g + 1e-4, npres) - phi_pred(g - 1e-4, npres)) / 2e-4
        xe = 1.96 * np.abs(dphi) * se
        y, ylo, yhi = v["phi_10"].to_numpy(), v["phi_10_lo"].to_numpy(), v["phi_10_hi"].to_numpy()
        bx.errorbar(xp, y, xerr=xe, yerr=[y - ylo, yhi - y], fmt=REG_M[r], ms=3.4, mfc=REG_C[r], mec="white",
                    mew=0.4, ecolor=REG_C[r], elinewidth=0.6, alpha=0.85, capsize=0, zorder=3)
    r3 = s["r_F_pooled_III"]
    r1 = s["r_F_pooled_I"]
    bx.text(0.985, 0.17, f"regime III (18 units): pooled $r_F$ = {r3[0]:.2f} [{r3[1]:.2f}, {r3[2]:.2f}]",
            fontsize=6.3, color=vs.COUPLING, va="bottom", ha="right", transform=bx.transAxes)
    bx.text(0.985, 0.10, f"regime I (21 units): pooled $r_F$ = {r1[0]:.2f} [{r1[1]:.2f}, {r1[2]:.2f}]",
            fontsize=6.3, color=REG_C["I"], va="bottom", ha="right", transform=bx.transAxes)
    bx.text(1.80, 1.84, r"$\Phi_{obs}=\Phi_{pred}$", rotation=45, transform_rotates_text=True, fontsize=6.3,
            ha="center", va="bottom", color=vs.INK)
    bx.text(1.60, 1.98, "±20%", fontsize=6.0, color=vs.COUPLING, rotation=45, transform_rotates_text=True)
    bx.set_xlim(0.8, 2.1)
    bx.set_ylim(*lim)
    bx.set_xlabel(r"predicted $\Phi_{pred} = 1/(1-g_{lag})^2$ (room-adjusted, from H67)")
    bx.set_ylabel(r"observed $\Phi$(10 min)")
    bx.set_title("(b) village: no free parameter", loc="left")
    h = [Line2D([], [], marker=REG_M[r], ls="", mfc=REG_C[r], mec="white", ms=4.5, label=f"regime {r}")
         for r in ("I", "II", "III")]
    bx.legend(handles=h, loc="upper right", ncol=3, handletextpad=0.2, columnspacing=0.8)
    return q95


def main():
    vs.use()
    u, s = load()
    # double column: a | b
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(vs.W["double"], 2.9), gridspec_kw={"width_ratios": [1, 1.15]})
    gs, m, n = panel_a(ax)
    q95 = panel_b(bx, u, s)
    fig.tight_layout(w_pad=1.5)
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    # single column: a over b
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(vs.W["single"], 5.0))
    panel_a(ax)
    panel_b(bx, u, s)
    fig.tight_layout(h_pad=1.2)
    vs.save(fig, HERE / "fig_col")
    plt.close(fig)
    print("sim means", dict(zip(gs, np.round(m, 3))), "pred", np.round(phi_pred(gs, n), 3))
    print("units by regime", u.group_by("regime").len().sort("regime").to_dicts(), "null q95 median", q95)


if __name__ == "__main__":
    main()
