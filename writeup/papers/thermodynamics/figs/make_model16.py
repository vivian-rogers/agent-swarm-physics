"""Model 16 (Langevin relaxation) paper figure: a fast read kick on a slow well, overdamped.

(a) H125: kickoff day-level response (excess within-agent alignment with the kickoff, relative to the days 4-5 level)
    over the 27 non-holdout kickoffs, both embedding models, 90% CI; days 2-3 (the undershoot window) shaded.
(b) H130 #51: own drive-corrected content autocorrelation (the slow well) and the sender-specific read kick (dose
    coefficients) vs lag in calls of the reader, pooled #51, bge, style-residualized; each divided by its fitted
    amplitude (well: plateau removed) so both fits are e^{-gamma n}.
(c) Simulation: x = s + k, a slow OU well s plus a fast kick k at each read, at the H130 rates.

Plotting only, from existing outputs (no new analysis):
  data/processed/H125-kickoff-damped-oscillator/NE34/series.json, NE34/card.json
  data/processed/H130-ou-private-wells-51/results/natives.json, results/summary.json
Usage (repo root): uv run python writeup/papers/thermodynamics/figs/make_model16.py
Output: writeup/papers/thermodynamics/figs/model16_relaxation.{pdf,png}
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
import vstyle as vs  # noqa: E402

H125 = ROOT / "data/processed/H125-kickoff-damped-oscillator/NE34"
H130 = ROOT / "data/processed/H130-ou-private-wells-51/results"
OUT = Path(__file__).resolve().parent / "model16_relaxation"


def panel_a(ax):
    ser = json.loads((H125 / "series.json").read_text())
    card = json.loads((H125 / "card.json").read_text())
    days = np.arange(1, 11)
    styles = (("bge_white", "bge", vs.FIELD, "o", "-", -0.09, True),
              ("gte_white", "gte", vs.INK2, "s", "--", 0.09, False))
    stats = {}
    for cfg, lab, col, mk, ls, off, filled in styles:
        M = np.full((len(ser), 10), np.nan)
        for j, v in enumerate(ser.values()):
            for d in days:
                x = v[cfg]["day"].get(str(d))
                if x and x[2] >= 3:          # same rule as hypotheses/H125-.../analysis/figures.py
                    M[j, d - 1] = x[0]
        n = np.isfinite(M).sum(0)
        m = np.nanmean(M, 0)
        se = np.nanstd(M, 0, ddof=1) / np.sqrt(np.maximum(n, 1))
        stats[lab] = (m, 1.645 * se, n)
        ax.errorbar(days + off, m, yerr=1.645 * se, color=col, marker=mk, ms=3.2, lw=1.1, ls=ls, capsize=1.5,
                    elinewidth=0.8, mfc=col if filled else "white", mec=col, zorder=3, label=lab)
    ax.axhline(0, color=vs.MUTED, lw=0.7, zorder=1)
    ax.axvspan(1.5, 3.5, color=vs.NULL, alpha=0.28, lw=0, zorder=0)
    ax.set_xlim(0.5, 10.5)
    ax.set_ylim(-0.052, 0.095)
    ax.text(2.5, -0.049, "undershoot\nwindow", ha="center", va="bottom", fontsize=6.5, color=vs.INK2)
    ub, ug = card["bge_white"], card["gte_white"]
    ax.text(10.3, 0.088, f"$U$ = {ub['U']:+.3f} [{ub['U_lo']:+.3f}, {ub['U_hi']:+.3f}] (bge)\n"
                         f"$U$ = {ug['U']:+.3f} [{ug['U_lo']:+.3f}, {ug['U_hi']:+.3f}] (gte)\n"
                         f"{ub['k']} kickoffs, 90% CI".replace("-", "\u2212"), ha="right", va="top", fontsize=6.2, color=vs.INK2, linespacing=1.3)
    ax.legend(loc="upper left", bbox_to_anchor=(0.39, 0.74), handlelength=2.2, borderaxespad=0)
    ax.set_xticks([1, 2, 3, 4, 5, 6, 8, 10])
    ax.set_xlabel("active day after kickoff")
    ax.set_ylabel("alignment − days 4–5 level")
    ax.set_title("(a) kickoff response (H125)", loc="left")
    return stats, card


def panel_b(ax):
    nat = json.loads((H130 / "natives.json").read_text())["pooled|bge_small"]
    summ = json.loads((H130 / "summary.json").read_text())["pools"]["bge_small|style_resid_period"]
    ga, gk, Ak = nat["g_auto"], nat["g_kick"], nat["A_kick"]
    # own well: drive-corrected autocorrelation, bins >= 1 (the fitted bins); remove the fitted plateau at fixed gamma
    C = np.array(nat["C_prof"], float); Ct = np.array(nat["C_tau"], float)
    m = np.isfinite(C) & (Ct > 0)
    C, Ct = C[m], Ct[m]
    X = np.column_stack([np.exp(-ga * Ct), np.ones_like(Ct)])
    A, B = np.linalg.lstsq(X, C, rcond=None)[0]
    yC = (C - B) / A
    # read kick: dose coefficients beta[1..6] at mean lags dose_tau[1..6], the bins kick_rate() fits (no plateau)
    b = np.array(nat["beta"], float)[1:7]; bs = np.array(nat["beta_se"], float)[1:7]
    bt = np.array(nat["dose_tau"], float)[1:7]
    tt = bt
    yK, eK = b / Ak, bs / Ak
    xs = np.concatenate([np.linspace(0, 1, 30), np.logspace(0, np.log10(1500), 200)])
    ax.axhline(0, color=vs.MUTED, lw=0.7, zorder=1)
    ax.plot(xs, np.exp(-ga * xs), color=vs.FIELD, lw=1.0, zorder=2)
    ax.plot(xs, np.exp(-gk * xs), color=vs.COUPLING, lw=1.0, zorder=2)
    ax.plot(Ct, yC, "o", color=vs.FIELD, ms=3.5, mec="white", mew=0.4, zorder=3)
    ax.errorbar(tt, yK, yerr=eK, fmt="s", color=vs.COUPLING, ms=3.3, mec="white", mew=0.4, elinewidth=0.8, capsize=1.5,
                zorder=3)
    ax.set_xscale("symlog", linthresh=1, linscale=0.45)   # log for lags >= 1; lag 0 shown at 0
    ax.set_xlim(-0.12, 1500)
    ax.set_ylim(-0.12, 1.62)
    ax.set_xticks([0, 1, 10, 100, 1000]); ax.set_xticklabels(["0", "1", "10", "100", "1000"])
    ax.minorticks_off()
    ax.text(120, 0.56, f"own well\n$\\approx${round(1 / ga, -1):.0f} calls", fontsize=7, color=vs.INK, ha="left", va="bottom")
    ax.text(0.05, 0.22, f"read kick\n$\\approx${1 / gk:.0f} calls", fontsize=7, color=vs.INK, ha="left", va="bottom")
    r, (rl, rh) = summ["rho"], summ["rho_ci90"]
    ax.text(1400, 1.58, f"$\\rho_\\gamma$ = {r:.1f} [{rl:.1f}, {rh:.1f}]\n(90% CI)", ha="right", va="top",
            fontsize=6.5, color=vs.INK2)
    ax.set_xlabel("lag (calls of the reader)")
    ax.set_ylabel("response / fitted amplitude")
    ax.set_title("(b) #51: well vs read kick (H130)", loc="left")
    return dict(g_auto_fit=ga, g_kick_fit=gk, A_kick=Ak, well_A=A, well_B=B, yC=yC, Ct=Ct, yK=yK, eK=eK, tK=bt,
                summ=summ)


def panel_c(ax, ga: float, gk: float, seed: int = 7):
    """Schematic only: x = s + k with s an OU well (rate ga per call) and k a kick (rate gk) added at each read."""
    rng = np.random.default_rng(seed)
    n = 400
    reads = np.array([70, 150, 230, 245, 320])
    s = np.zeros(n); k = np.zeros(n)
    sig = 0.3 * np.sqrt(2 * ga)        # stationary SD of s = 0.3
    for t in range(1, n):
        s[t] = s[t - 1] * (1 - ga) + sig * rng.standard_normal()
        k[t] = k[t - 1] * (1 - gk) + (0.7 if t in reads else 0.0)
    x = s + k
    tt = np.arange(n)
    ax.plot(tt, x, color=vs.COUPLING, lw=1.0, zorder=2)
    ax.plot(tt, s, color=vs.FIELD, lw=1.2, zorder=3)
    lo = min(x.min(), s.min()); hi = max(x.max(), s.max())
    span = hi - lo
    yb = lo - 0.22 * span
    for r in reads:
        ax.plot([r, r], [yb, yb + 0.1 * span], color=vs.INK2, lw=0.9)
    ax.text(reads[0] - 8, yb + 0.05 * span, "reads", fontsize=6.5, color=vs.INK2, va="center", ha="right")
    ax.set_ylim(yb - 0.05 * span, hi + 0.2 * span)
    ax.set_xlim(0, n)
    r = reads[0] + 1
    ax.annotate("x = s + k", (r, x[r]), xytext=(-6, 2), textcoords="offset points", fontsize=7, color=vs.INK,
                ha="right", va="bottom")
    i = 285
    ax.text(i, min(x[i - 25:i + 25].min(), s[i - 25:i + 25].min()) - 0.06 * span, "well s", fontsize=7, color=vs.INK,
            ha="center", va="top")
    ax.set_xlabel("call")
    ax.set_ylabel("state (a.u.)")
    ax.set_yticks([])
    ax.set_title("(c) simulation", loc="left")


def main():
    vs.use()
    fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.45), gridspec_kw={"width_ratios": [1.12, 1.12, 0.86]})
    sa, card = panel_a(ax[0])
    sb = panel_b(ax[1])
    panel_c(ax[2], sb["g_auto_fit"], sb["g_kick_fit"])
    fig.tight_layout(w_pad=1.0)
    vs.save(fig, OUT)
    # numbers shown, for the report
    mb, eb, nb = sa["bge"]; mg, eg, ng = sa["gte"]
    print("H125 day profile bge:", np.round(mb, 3).tolist(), "±", np.round(eb, 3).tolist(), "n", nb.tolist())
    print("H125 day profile gte:", np.round(mg, 3).tolist(), "±", np.round(eg, 3).tolist(), "n", ng.tolist())
    for c in ("bge_white", "gte_white", "bge_dedupe"):
        r = card[c]
        print(c, "U", round(r["U"], 4), [round(r["U_lo"], 4), round(r["U_hi"], 4)], "E1", round(r["E1"], 4), "±",
              round(r["E1_se"], 4), f"{r['E1_pos']}/{r['k']}")
    s = sb["summ"]
    print("H130 pooled-fit g_auto", round(sb["g_auto_fit"], 5), "-> 1/g", round(1 / sb["g_auto_fit"], 1),
          "| g_kick", round(sb["g_kick_fit"], 4), "-> 1/g", round(1 / sb["g_kick_fit"], 1))
    print("H130 DL pool: g_auto", round(s["g_auto"], 5), [round(v, 5) for v in s["g_auto_ci"]], "g_kick", round(s["g_kick"], 4),
          "rho", round(s["rho"], 2), "90%", [round(v, 2) for v in s["rho_ci90"]], "J", round(s["J"], 4),
          [round(v, 4) for v in s["J_ci"]])
    print("well plateau fit A, B:", round(sb["well_A"], 4), round(sb["well_B"], 4))
    print("well points:", list(zip(np.round(sb["Ct"], 1).tolist(), np.round(sb["yC"], 3).tolist())))
    print("kick points:", list(zip(np.round(sb["tK"], 1).tolist(), np.round(sb["yK"], 3).tolist(), np.round(sb["eK"], 3).tolist())))


if __name__ == "__main__":
    main()
