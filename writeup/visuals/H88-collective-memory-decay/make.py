"""H88 visuals: attention to a finished period decays fast to a small floor, alike for veterans and newcomers.

fig.pdf/png  (a) veterans' attention share to a finished period's coined terms against village days since the period
             ended, each period normalized by its own fitted share at day 1 (thin lines: per-period exponential +
             floor fits; points: median of the normalized daily shares over periods in day bins, IQR bars); median-
             parameter curves of exp + floor (tau 5.5 d, floor 1.9%), the biexponential where it won (tau1 2.0,
             tau2 48 d) and the single exponential. (b) newcomers' attention relative to veterans' at the same age
             (indirectly standardized ratio R by age band, period bootstrap 95% CI) against "alike" (R = 1) and the
             synthetic slow-only newcomer of the Candia model.

Inputs (read-only): data/processed/H88-collective-memory-decay/{daily.parquet, replication/replication.json,
synthetic/synthetic.json}; estimators imported from hypotheses/H88-collective-memory-decay/analysis/h88lib.py.
Usage: uv run python writeup/visuals/H88-collective-memory-decay/make.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIS = HERE.parent
ROOT = VIS.parents[1]
sys.path.insert(0, str(VIS))
sys.path.insert(0, str(ROOT / "hypotheses/H88-collective-memory-decay/analysis"))

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import vstyle as vs  # noqa: E402
import h88lib as H  # noqa: E402

D = ROOT / "data/processed/H88-collective-memory-decay"
KBINS = [(1, 1), (2, 2), (3, 4), (5, 7), (8, 12), (13, 20), (21, 35), (36, 60), (61, 120)]


def m_params(fit, m):
    return fit["models"][m]["theta"]


def main():
    vs.use()
    rep = json.load(open(D / "replication/replication.json"))
    syn = json.load(open(D / "synthetic/synthetic.json"))
    daily = H.load_daily()
    card = rep["card"]["term"]
    fig = plt.figure(figsize=(vs.W["double"], 2.55))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0], wspace=0.3)
    a0, a1 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])

    # (a) collapse of the veterans' term share
    kk = np.linspace(1, 120, 600)
    norm_pts = {i: [] for i in range(len(KBINS))}
    n_used = 0
    a2s, a1s = [], []
    for P, ch in rep["periods"].items():
        t = ch.get("term")
        if not t or not t.get("fit"):
            continue
        fit = t["fit"]
        th = m_params(fit, "M1c")
        f1 = H.f_of("M1c", th, np.array([1.0]))[0]
        a0.plot(kk, H.f_of("M1c", th, kk) / f1, color=vs.MUTED, lw=0.4, alpha=0.4, zorder=1)
        k, y, O = H.series(daily, int(P), "term", "vet")
        s = y / O / f1
        for i, (lo, hi) in enumerate(KBINS):
            m = (k >= lo) & (k <= hi)
            if m.any():
                norm_pts[i].append(float(np.mean(s[m])))
        n_used += 1
        if fit.get("biexp"):
            p2 = fit["M2_params"]; a1s.append(p2["A1"]); a2s.append(p2["A2"])
    kc = np.array([np.sqrt(lo * hi) for lo, hi in KBINS])
    med = np.array([np.median(norm_pts[i]) for i in range(len(KBINS))])
    q1 = np.array([np.percentile(norm_pts[i], 25) for i in range(len(KBINS))])
    q3 = np.array([np.percentile(norm_pts[i], 75) for i in range(len(KBINS))])
    a0.errorbar(kc, med, yerr=[med - q1, q3 - med], fmt="o", color=vs.INK, ms=3.5, capsize=1.5, lw=0.9, zorder=4,
                label=f"veterans, median of {n_used} periods (IQR)")
    tau, c = card["M1c_tau_median"], card["M1c_floor_ratio_median"]
    g = lambda k: (np.exp(-k / tau) + c) / (np.exp(-1 / tau) + c)  # noqa: E731
    a0.plot(kk, g(kk), color=vs.FIELD, lw=1.8, zorder=3, label=f"exp + floor: τ {tau:.1f} d, floor {100 * c:.1f}%")
    t1, t2 = card["tau1_median"], card["tau2_median"]
    r = np.median(np.array(a2s) / np.array(a1s))
    h = lambda k: (np.exp(-k / t1) + r * np.exp(-k / t2)) / (np.exp(-1 / t1) + r * np.exp(-1 / t2))  # noqa: E731
    a0.plot(kk, h(kk), color=vs.C["green"], lw=1.2, ls="--", zorder=3,
            label=f"biexponential (where it won, {card['best_counts']['M2']}/20): τ₁ {t1:.1f}, τ₂ {t2:.0f} d")
    t0 = card["M1_tau_median"]
    a0.plot(kk, np.exp(-(kk - 1) / t0), color=vs.C["blue"], lw=1.0, ls=":", zorder=3,
            label=f"single exponential: τ {t0:.0f} d")
    a0.set_yscale("log"); a0.set_xscale("log")
    a0.set_ylim(3e-3, 3); a0.set_xlim(0.9, 125)
    a0.set_xticks([1, 3, 10, 30, 100]); a0.set_xticklabels(["1", "3", "10", "30", "100"])
    a0.set_xlabel("village days since the period ended")
    a0.set_ylabel("attention share / share at day 1")
    a0.legend(loc="lower left", fontsize=5.7, borderaxespad=0.2)
    bc = card["best_counts"]
    a0.text(0.99, 0.97, f"best model over 20 periods:\nexp + floor {bc['M1c']}, single {bc['M1']},\n"
            f"biexponential {bc['M2']}, power law {bc['MP']}", transform=a0.transAxes, ha="right", va="top",
            fontsize=6, color=vs.INK2)
    a0.set_title("(a) fast decay to a floor (coined terms)", loc="left")

    # (b) newcomer / veteran ratio
    elig = rep["eligible"]["term"]
    rows = daily.filter((pl.col("kind") == "term") & pl.col("P").is_in(elig) & pl.col("observed")
                        & (pl.col("O") > 0) & pl.col("group").is_in(["vet", "new"])).select("P", "group", "k", "y", "O")
    Ps, obs, exp = H._band_table(rows)
    R, b = H._rb(obs, exp)
    rng = np.random.default_rng(88)
    bs = []
    for _ in range(4000):
        pick = rng.integers(0, len(Ps), len(Ps))
        o, e = obs[pick].sum(0), exp[pick].sum(0)
        bs.append(o / np.where(e > 0, e, np.nan))
    bs = np.array(bs)
    Rv = np.array(list(R.values()))
    lo, hi = np.nanpercentile(bs, 2.5, axis=0), np.nanpercentile(bs, 97.5, axis=0)
    xb = np.arange(3)
    a1.axhline(1, color=vs.MUTED, lw=1.0, ls="--")
    a1.text(2.35, 1.03, "alike (same decay)", fontsize=6, color=vs.INK2, ha="right", va="bottom")
    bslow = syn["newcomer_b"]["term/slow_only"]["b_mean"]
    pred = Rv[0] * np.exp(bslow * np.array([0, 0.5, 1.0]))
    a1.plot(xb, pred, color=vs.C["green"], lw=1.2, ls="--", marker="s", mfc="white", ms=3.5,
            label=f"Candia: newcomers slow-only (synthetic, b = +{bslow:.2f})")
    a1.errorbar(xb, Rv, yerr=[Rv - lo, hi - Rv], fmt="o-", color=vs.FIELD, mec=vs.INK, mew=0.5, ms=4.5, lw=1.4,
                capsize=1.8, label="newcomers / veterans (village)")
    for x, v in zip(xb, Rv):
        a1.text(x + 0.08, v, f"{v:.2f}", fontsize=6.3, va="center")
    a1.set_xticks(xb); a1.set_xticklabels(["1–10", "11–40", "41–120"])
    a1.set_xlim(-0.35, 2.4)
    a1.set_ylim(0, max(2.4, float(np.nanmax(hi)) * 1.05))
    a1.set_xlabel("age of the period's terms (village days)")
    a1.set_ylabel("newcomer rate / veteran rate")
    a1.legend(loc="upper left", fontsize=5.7, borderaxespad=0.2)
    a1.grid(axis="x", visible=False)
    a1.set_title("(b) newcomers forget at the same pace", loc="left")

    vs.save(fig, HERE / "fig")
    plt.close(fig)
    print("periods", n_used, "M1c tau", tau, "floor", c, "biexp", t1, t2, "A2/A1", r)
    print("R", R, "b", b, "card", card["newcomer"]["R"], card["newcomer"]["b"], card["newcomer"]["b_ci"])
    print("CI lo", lo, "hi", hi)


if __name__ == "__main__":
    main()
