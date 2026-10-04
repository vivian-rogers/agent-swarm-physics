"""H85 visual: talk output scales sublinearly with swarm size; in regime I the room's talk is nearly fixed.

    uv run python writeup/visuals/H85-output-scaling-with-n/make.py

Inputs (read only; non-holdout by construction, asserted):
  data/processed/H85-output-scaling-with-n/units.parquet          per unit: N (active, hour-weighted), T_h, msg, talk_calls
  data/processed/H86-taylor-law-field-gauge/bins15.parquet         per-unit call counts (as in H85's post hoc PH2)
Fits reuse H85's own design and OLS (hypotheses/H85-output-scaling-with-n/analysis/h85lib.py, read-only import):
M1 = regime intercepts + common slope, goal-cluster bootstrap (B = 2000, H85's seed), so the exponent and CI match the card.
Output: fig.pdf / fig.png.
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
sys.path.insert(0, str(ROOT / "hypotheses/H85-output-scaling-with-n/analysis"))
import vstyle as vs  # noqa: E402
import h85lib as L  # noqa: E402
from common import load_holdout  # noqa: E402

REG_C = {"I": vs.C["green"], "II": vs.C["pink"], "III": vs.C["blue"]}
REG_M = {"I": "s", "II": "D", "III": "o"}
B = 2000


def load():
    held = set(load_holdout()["goal_periods_held_out"])
    u = pl.read_parquet(ROOT / "data/processed/H85-output-scaling-with-n/units.parquet")
    assert not set(u["goal_no"].to_list()) & held
    u = u.filter((pl.col("T_h") >= 1) & (pl.col("msg") >= 20))           # H85 replication filter (71 units)
    calls = (pl.read_parquet(ROOT / "data/processed/H86-taylor-law-field-gauge/bins15.parquet")
             .group_by("unit_id").agg(pl.col("calls").sum().alias("calls_all")))
    return u.join(calls, on="unit_id", how="left")


def cluster_boot(X, y, cl, rng):
    groups = sorted(set(cl))
    idx_by = {g: np.where(cl == g)[0] for g in groups}
    out = np.empty((B, X.shape[1]))
    for i in range(B):
        pick = rng.choice(len(groups), len(groups), replace=True)
        ii = np.concatenate([idx_by[groups[p]] for p in pick])
        out[i] = L.ols(X[ii], y[ii])
    return out


def main():
    vs.use()
    u = load()
    lnN = np.log(u["N"].to_numpy())
    y = np.log(u["msg"].to_numpy() / u["T_h"].to_numpy())
    reg = u["regime"].to_numpy()
    cl = u["goal_no"].to_numpy()
    X, names = L.design(lnN, reg)
    b = L.ols(X, y)
    bt = cluster_boot(X, y, cl, np.random.default_rng(20261004))
    beta, lo, hi = b[0], *np.quantile(bt[:, 0], [0.025, 0.975])

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(vs.W["double"], 2.85), gridspec_kw={"width_ratios": [1.25, 1]})
    # (a) messages per scheduled hour vs N, M1 fit and the extensive reference
    for r in ("I", "II", "III"):
        m = reg == r
        ax.scatter(u["N"].to_numpy()[m], np.exp(y[m]), marker=REG_M[r], s=13, color=REG_C[r], edgecolor="white",
                   lw=0.3, zorder=3, label=f"regime {r} ({m.sum()} units)")
        j = names.index(f"reg_{r}")
        xs = np.linspace(lnN[m].min(), lnN[m].max(), 40)
        fit = b[j] + b[0] * xs
        band = bt[:, [j]] + bt[:, [0]] * xs[None, :]
        blo, bhi = np.quantile(band, [0.025, 0.975], axis=0)
        ax.fill_between(np.exp(xs), np.exp(blo), np.exp(bhi), color=REG_C[r], alpha=0.15, lw=0, zorder=1)
        ax.plot(np.exp(xs), np.exp(fit), color=REG_C[r], lw=1.4, zorder=2)
        if r != "II":
            x0 = lnN[m].mean(); y0 = b[j] + b[0] * x0
            ax.plot(np.exp(xs), np.exp(y0 + (xs - x0)), color=vs.MUTED, lw=1.0, ls="--", zorder=1)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xticks([4, 6, 10, 15, 25]); ax.set_xticklabels(["4", "6", "10", "15", "25"])
    ax.set_yticks([30, 100, 300, 1000]); ax.set_yticklabels(["30", "100", "300", "1000"]); ax.set_ylim(28, 2200)
    ax.minorticks_off()
    ax.set_xlabel("active agents $N$ (unit, hour-weighted)")
    ax.set_ylabel("agent messages per scheduled hour")
    ax.set_title("(a) talk grows slower than the swarm", loc="left")
    ax.text(0.03, 0.97, f"messages $\\propto N^{{\\beta}}$\n$\\beta$ = {beta:.2f} [{lo:.2f}, {hi:.2f}]\n"
            "(regime intercepts,\ngoal-cluster 95% CI)", transform=ax.transAxes, va="top", fontsize=6.6, color=vs.INK)
    h, l = ax.get_legend_handles_labels()
    h += [Line2D([], [], color=vs.INK2, lw=1.4), Line2D([], [], color=vs.MUTED, ls="--", lw=1.0)]
    l += [f"common-slope fit ($\\beta$ = {beta:.2f}) + 95% band", "$\\beta = 1$ (independent agents)"]
    ax.legend(h, l, loc="upper right", fontsize=6.0, handlelength=1.6)

    # (b) regime-I talk budget: exponent decomposition with goal-cluster CIs
    I = u.filter(pl.col("regime") == "I")
    xI = np.log(I["N"].to_numpy())
    XI = np.c_[xI, np.ones_like(xI)]
    NI, TI, mI = I["N"].to_numpy(), I["T_h"].to_numpy(), I["msg"].to_numpy()
    tcI, caI = I["talk_calls"].to_numpy(), I["calls_all"].to_numpy()
    parts = [("one clock per agent", None),
             ("calls per agent-hour", np.log(caI / (NI * TI))),
             ("talk share of calls", np.log(tcI / caI)),
             ("messages per talk call", np.log(mI / tcI))]
    rngI = np.random.default_rng(85)
    clI = I["goal_no"].to_numpy()
    vals, cis = [1.0], [(1.0, 1.0)]
    for _, yy in parts[1:]:
        s = L.ols(XI, yy)[0]
        bb = cluster_boot(XI, yy, clI, rngI)[:, 0]
        vals.append(s); cis.append(tuple(np.quantile(bb, [0.025, 0.975])))
    ytot = np.log(mI / TI)
    tot = L.ols(XI, ytot)[0]
    rep = json.loads((ROOT / "data/processed/H85-output-scaling-with-n/replication/replication.json").read_text())
    wI = rep["levels"]["msg"]["within_I"]                    # the card's regime-I exponent and CI
    assert abs(wI["beta"] - tot) < 1e-6
    tot_ci = (wI["ci_lo"], wI["ci_hi"])
    cum = 0.0
    for i, ((lab, _), v, ci) in enumerate(zip(parts, vals, cis)):
        col = vs.MUTED if i == 0 else (vs.C["red"] if v < 0 else vs.C["sky"])
        bx.bar(i, v, bottom=cum, width=0.6, color=col, zorder=2)
        if i > 0:
            bx.errorbar(i, cum + v, yerr=[[v - ci[0]], [ci[1] - v]], color=vs.INK, elinewidth=0.8, capsize=2, zorder=3)
            bx.plot([i - 1 + 0.3, i - 0.3], [cum, cum], color=vs.MUTED, lw=0.6, ls=":")
        if i == 0:
            bx.text(i, 1.06, "+1", ha="center", va="bottom", fontsize=6.5)
        else:
            if abs(v) < 0.1:
                bx.text(i, max(cum, cum + v) + 0.2, f"{v:+.2f}", ha="center", va="bottom", fontsize=6.5)
            else:
                bx.text(i + 0.34, cum + v / 2, f"{v:+.2f}", ha="left", va="center", fontsize=6.5)
        cum += v
    k = len(parts)
    bx.plot([k - 1 + 0.3, k - 0.3], [cum, cum], color=vs.MUTED, lw=0.6, ls=":")
    bx.bar(k, tot, width=0.6, color=REG_C["I"], zorder=2)
    bx.errorbar(k, tot, yerr=[[tot - tot_ci[0]], [tot_ci[1] - tot]], color=vs.INK, elinewidth=0.8, capsize=2, zorder=3)
    bx.text(k + 0.34, tot / 2 + 0.03, f"{tot:+.2f}", ha="left", va="center", fontsize=6.5)
    bx.axhline(1, color=vs.MUTED, ls="--", lw=0.9)
    bx.text(k + 0.6, 1.02, "$\\beta=1$", ha="right", va="bottom", fontsize=6.2, color=vs.INK2)
    bx.axhline(0, color=vs.INK2, lw=0.6)
    bx.set_xticks(range(k + 1))
    bx.set_xticklabels([p[0] for p in parts] + ["room messages\nper hour"], fontsize=5.8, rotation=28, ha="right")
    bx.set_ylim(-0.75, 1.35); bx.set_xlim(-0.5, k + 0.75)
    bx.set_ylabel("exponent of $N$ (regime I, 41 units)")
    bx.set_title("(b) regime I: same clock, less talk each", loc="left")
    fig.tight_layout(w_pad=1.4)
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    print(f"beta_msg {beta:.3f} [{lo:.3f}, {hi:.3f}]; regime I parts {np.round(vals, 3)} CIs {np.round(cis, 2).tolist()}; total {tot:.3f} {np.round(tot_ci, 2)}")


if __name__ == "__main__":
    main()
