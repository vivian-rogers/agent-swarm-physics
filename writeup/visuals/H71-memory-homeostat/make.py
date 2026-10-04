"""H71 writeup visual: memory size is held by a homeostat on the consolidation clock.

Static figure (fig.pdf/png, double column):
  (a) sawtooth: memory size of three G51 agents over four hours of one day (append snapshots grow it, compress
      snapshots cut it), with each agent's set point (its mean post-compression size in G51)
  (b) reversion: post-compression deviation from the agent set point vs the previous cycle's deviation (G51,
      binned, agent-bootstrap 95% CIs), with the fitted phi+ and the random-walk (slope 1, gray) and
      deadbeat (slope 0) references
  (c) phi+ per period unit (37 units, three regimes) with the pooled value; random walk = 1 (gray)

Inputs (processed, non-holdout): data/processed/H71-memory-homeostat/{snapshots,cycles}.parquet, results/*.json;
agent names from data/processed/shared/roster.parquet.
Run: uv run python writeup/visuals/H71-memory-homeostat/make.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import vstyle as vs  # noqa: E402
from common import holdout_mask  # noqa: E402

HERE = Path(__file__).resolve().parent
D = ROOT / "data/processed/H71-memory-homeostat"
TRACES = [(14, "2026-07-16"), (6, "2026-07-17")]   # two G51 agent-days with dense snapshots
TCOL = [vs.C["sky"], vs.C["pink"]]
HOURS = 1.5
REG = {"I": vs.INK2, "II": vs.C["sky"], "III": vs.C["green"]}


def nonholdout(df):
    m = np.array(holdout_mask(df["pt_date"].to_list(), df["goal_no"].to_list()))
    return df.filter(pl.Series(~m))


def panel_sawtooth(ax, names, per):
    snaps = nonholdout(pl.read_parquet(D / "snapshots.parquet").filter(pl.col("period") == "G51"))
    mu = {a["agent"]: a["mu"] for a in per["G51"]["agents"]}
    for (ag, day), col in zip(TRACES, TCOL):
        s = snaps.filter((pl.col("agent") == ag) & (pl.col("pt_date") == day) & (pl.col("phase") != "same")).sort("t")
        t = s["t"].to_numpy()
        h = (t - t[0]) / np.timedelta64(1, "h")
        sel = h <= HOURS
        h, n, ph = h[sel], s["n_chars"].to_numpy()[sel] / 1000, s["phase"].to_numpy()[sel]
        ax.step(h, n, where="post", color=col, lw=1.0)
        c = ph == "compress"
        ax.plot(h[c], n[c], "v", ms=2.2, color=col, mec="none")
        ax.axhline(np.exp(mu[ag]) / 1000, color=col, ls="--", lw=0.8, alpha=0.9)
        ax.text(HOURS + 0.02, np.exp(mu[ag]) / 1000, names[ag], fontsize=6.3, color=vs.INK, va="center")
    ax.set_yscale("log")
    ax.set_yticks([5, 10, 20, 40, 80]); ax.set_yticklabels(["5", "10", "20", "40", "80"])
    ax.minorticks_off()
    ax.set_ylim(5, 130)
    ax.set_xlim(0, HOURS)
    ax.set_xlabel("hours into the day (G51)")
    ax.set_ylabel("memory size (k chars)")
    ax.set_title("(a) sawtooth around a set point", loc="left")
    ax.legend(handles=[Line2D([], [], color=vs.INK2, marker="v", ms=3, lw=0, label="compress snapshot"),
                       Line2D([], [], color=vs.INK2, ls="--", lw=0.8, label="set point (mean post-compression size)")],
              loc="upper left", fontsize=6.3, handlelength=1.4, borderaxespad=0.2)


def panel_reversion(ax, per, B=300, seed=2):
    cyc = nonholdout(pl.read_parquet(D / "cycles.parquet").filter(
        (pl.col("period") == "G51") & (pl.col("period_prev") == "G51")).drop_nulls(["xplus", "xplus_prev"]))
    mu = cyc.group_by("agent").agg(pl.col("xplus").mean().alias("mu"))
    cyc = cyc.join(mu, on="agent")
    x = (cyc["xplus_prev"] - cyc["mu"]).to_numpy()
    y = (cyc["xplus"] - cyc["mu"]).to_numpy()
    ag = cyc["agent"].to_numpy()
    edges = np.quantile(x, np.linspace(0.005, 0.995, 16))
    b = np.clip(np.digitize(x, edges) - 1, 0, len(edges) - 2)
    nb = len(edges) - 1
    ua, inv = np.unique(ag, return_inverse=True)

    def means(w):
        return (np.bincount(b, weights=x * w, minlength=nb) / np.bincount(b, weights=w, minlength=nb),
                np.bincount(b, weights=y * w, minlength=nb) / np.bincount(b, weights=w, minlength=nb))

    mx, my = means(np.ones_like(x))
    rng = np.random.default_rng(seed)
    dr = np.array([means(rng.multinomial(len(ua), np.full(len(ua), 1 / len(ua)))[inv].astype(float))[1]
                   for _ in range(B)])
    lo, hi = np.nanpercentile(dr, [2.5, 97.5], axis=0)
    ph = per["G51"]["phi"]
    xx = np.linspace(-0.8, 0.8, 50)
    ax.plot(xx, xx, color=vs.NULL, lw=2.0, ls="--")
    ax.text(0.30, 0.47, "random walk", fontsize=6.3, color=vs.MUTED, ha="right", rotation=40)
    ax.axhline(0, color=vs.INK2, lw=0.6)
    ax.text(-0.78, 0.03, "deadbeat (reset each cycle)", fontsize=6.3, color=vs.MUTED)
    ax.fill_between(xx, ph["lo"] * xx, ph["hi"] * xx, color=vs.C["green"], alpha=0.2, lw=0)
    ax.plot(xx, ph["est"] * xx, color=vs.C["green"], lw=1.3)
    ax.errorbar(mx, my, yerr=[my - lo, hi - my], fmt="o", ms=3, color=vs.INK, elinewidth=0.8, capsize=0)
    ax.text(0.05, -0.45, rf"$\phi^+ = {ph['est']:.2f}$ [{ph['lo']:.2f}, {ph['hi']:.2f}]", fontsize=6.8,
            color=vs.C["green"])
    ax.set_xlim(-0.8, 0.8); ax.set_ylim(-0.65, 0.65)
    ax.set_xlabel(r"previous deviation $x^+_{n-1}-\mu_i$ (ln chars)")
    ax.set_ylabel(r"next deviation $x^+_n-\mu_i$")
    ax.set_title("(b) reversion per cycle (G51)", loc="left")
    return len(x)


def panel_periods(ax, per, cross):
    keys = list(per.keys())
    xs = np.arange(len(keys))
    for i, k in enumerate(keys):
        p = per[k]
        col = REG[p["regime"]]
        ax.plot([i, i], [p["phi"]["lo"], p["phi"]["hi"]], color=col, lw=1.0)
        ax.plot(i, p["phi"]["est"], "o", ms=2.8, color=col)
    pa = cross["pools"]["all"]
    ax.axhspan(pa["lo"], pa["hi"], color=vs.C["green"], alpha=0.15, lw=0)
    ax.axhline(pa["phi"], color=vs.C["green"], lw=0.8)
    ax.axhline(1, color=vs.NULL, lw=2.0, ls="--")
    ax.text(0, 1.03, "random walk", fontsize=6.3, color=vs.MUTED)
    ax.axhline(0, color=vs.INK2, lw=0.6)
    show = {0: keys[0], keys.index("G20"): "G20", keys.index("G36b"): "G36b", len(keys) - 1: keys[-1]}
    ax.set_xticks(list(show.keys())); ax.set_xticklabels(list(show.values()), fontsize=6.5)
    ax.set_xlim(-1, len(keys))
    ax.set_ylim(-0.5, 1.15)
    ax.set_xlabel("period unit (time order)")
    ax.set_ylabel(r"$\phi^+$ per compression cycle")
    ax.set_title("(c) every period reverts", loc="left")
    ax.legend(handles=[Line2D([], [], color=REG[r], marker="o", ms=3, lw=1.0, label=f"regime {r}") for r in REG]
              + [Line2D([], [], color=vs.C["green"], lw=4, alpha=0.4, label=f"pooled {pa['phi']:.2f} [{pa['lo']:.2f}, {pa['hi']:.2f}]")],
              loc="lower left", fontsize=6.0, ncol=2, handlelength=1.0, columnspacing=0.8, borderaxespad=0.2)
    ax.grid(axis="x", visible=False)


def static():
    vs.use()
    per = json.loads((D / "results/periods.json").read_text())
    cross = json.loads((D / "results/cross.json").read_text())
    names = dict(pl.read_parquet(ROOT / "data/processed/shared/roster.parquet").select("agent", "name").iter_rows())
    fig, axs = plt.subplots(1, 3, figsize=(vs.W["double"], 2.5), gridspec_kw={"width_ratios": [1.15, 1, 1]})
    panel_sawtooth(axs[0], names, per)
    n = panel_reversion(axs[1], per)
    panel_periods(axs[2], per, cross)
    fig.tight_layout(w_pad=0.7)
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    print("G51 cycles in panel b", n)


if __name__ == "__main__":
    static()
