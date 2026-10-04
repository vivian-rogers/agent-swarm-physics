"""H103 visuals: nights do not demagnetize; kickoff remanence decays with active work.

fig.pdf/png  (a) simulation: the two clocks on the wall-time axis (night clock = a step per night, flat in the day;
             active-hour clock = decay during work, flat over the night); (b) one real period's kickoff remanence A_w
             (30-min windows, bge style_resid) against active hours, with the night-clock and active-hour-clock fits
             of H103 (same parameter count, time-of-day slots included); (c) the night step at fixed active lag,
             beta_N: village random-effects mean (both models) against the synthetic truths of H103's validation.

Inputs (read-only): data/processed/H103-nights-demagnetize/results/{o1,o3,card}_<model>_style_resid.json,
synthetic/synthetic.json.
Usage: uv run python writeup/visuals/H103-nights-demagnetize/make.py [--period G10]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIS = HERE.parent
ROOT = VIS.parents[1]
sys.path.insert(0, str(VIS))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import vstyle as vs  # noqa: E402

D = ROOT / "data/processed/H103-nights-demagnetize"
# grid and design copied from hypotheses/H103-nights-demagnetize/analysis/h103lib.py (fit_clock, _design)
GRID = {"N": np.linspace(0.02, 1.0, 50), "H": np.exp(np.linspace(np.log(0.1), np.log(300), 60))}


def _design(f, slot):
    S = np.zeros((len(f), 3))
    for k in (1, 2, 3):
        S[:, k - 1] = slot == k
    return np.column_stack([np.ones(len(f)), f, S])


def fit_clock(ser, clock):
    """Grid-profiled weighted LS with slot effects (h103lib.fit_clock). Returns fitted values and the SSE."""
    y = np.array(ser["A"]); wt = np.array(ser["n"], float); slot = np.array(ser["slot"]); x = np.array(ser[clock], float)
    best = None
    for r in GRID[clock]:
        f = r ** x if clock == "N" else np.exp(-x / r)
        X = _design(f, slot)
        Xw = X * np.sqrt(wt)[:, None]; yw = y * np.sqrt(wt)
        beta, *_ = np.linalg.lstsq(Xw, yw, rcond=None)
        sse = float(((yw - Xw @ beta) ** 2).sum())
        if best is None or sse < best[0]:
            best = (sse, X @ beta, r)
    return best


def panel_sim(ax):
    """Simulation, 4 days: active window 4 h (shaded white), nights 20 h (gray)."""
    day, night = 4.0, 2.5   # nights drawn short (not to scale)
    t = np.linspace(0, 4 * (day + night) - night, 2000)
    k = np.floor(t / (day + night)); inday = (t - k * (day + night)) <= day
    H = np.where(inday, k * day + (t - k * (day + night)), (k + 1) * day)
    N = k
    a_inf, dA = 0.1, 0.3
    A_H = a_inf + dA * np.exp(-H / 5.0)
    A_N = a_inf + dA * 0.55 ** N
    for j in range(3):
        ax.axvspan(j * (day + night) + day, (j + 1) * (day + night), color=vs.GRID, lw=0)
    ax.plot(t, np.where(inday, A_N, np.nan), color=vs.C["green"], lw=1.4, label="night clock (HH331)")
    ax.plot(t, np.where(inday, A_H, np.nan), color=vs.FIELD, lw=1.4, label="active-hour clock")
    ax.plot(t, np.where(~inday, A_N, np.nan), color=vs.C["green"], lw=0.8, ls=":")
    ax.plot(t, np.where(~inday, A_H, np.nan), color=vs.FIELD, lw=0.8, ls=":")
    ax.text(day + night / 2, 0.06, "nights\n(short,\nnot to\nscale)", ha="center", va="bottom", fontsize=5.2, color=vs.INK2)
    ax.set_xlim(0, t[-1]); ax.set_ylim(0.05, 0.56)
    ax.set_xticks([(day + night) * j + day / 2 for j in range(4)]); ax.set_xticklabels(["day 1", "2", "3", "4"])
    ax.set_yticks([]); ax.set_ylabel("remanence (a.u.)")
    ax.grid(False)
    ax.legend(loc="upper right", fontsize=5.8, borderaxespad=0.2)
    ax.set_title("(a) two clocks (simulation)", loc="left")


def panel_period(ax, o1, key):
    r = o1[key]; ser = r["series"]
    H = np.array(ser["H"]); N = np.array(ser["N"]); A = np.array(ser["A"])
    sN, fN, lam = fit_clock(ser, "N"); sH, fH, tau = fit_clock(ser, "H")
    days = np.unique(N)
    for dn in days[1:]:
        h0 = H[N == dn].min(); h1 = H[N == dn - 1].max()
        ax.axvline((h0 + h1) / 2, color=vs.INK2, lw=0.6, ls=(0, (2, 2)))
    for dn in days:
        m = N == dn
        ax.plot(H[m], fN[m], color=vs.C["green"], lw=1.3, zorder=2)
        ax.plot(H[m], fH[m], color=vs.FIELD, lw=1.3, zorder=3)
    ax.scatter(H, A, s=np.array(ser["n"]) * 2.2, color="white", edgecolor=vs.INK, lw=0.6, zorder=4,
               label="30-min window (size = agents)")
    ax.plot([], [], color=vs.C["green"], lw=1.3, label=f"night-clock fit (SSE {sN:.3f})")
    ax.plot([], [], color=vs.FIELD, lw=1.3, label=f"active-hour fit (SSE {sH:.3f})")
    ax.plot([], [], color=vs.INK2, lw=0.6, ls=(0, (2, 2)), label="night")
    ax.set_xlabel("active hours since the kickoff")
    ax.set_ylabel(r"kickoff remanence $A_w$")
    ax.legend(loc="lower left", fontsize=5.6, borderaxespad=0.2)
    ax.set_title(f"(b) #{r['goal_no']}: decay runs during work", loc="left")
    return sN, sH, r


def panel_beta(ax, o3card, syn):
    rows = []
    for m, lab in (("bge_small", "village (bge)"), ("gte_modernbert", "village (gte)")):
        b = o3card[m]["beta_N"]["RE"]
        rows.append((lab, b["est"], b["lo"], b["hi"], "data"))
    for truth, lab in (("H", "sim.: active clock"), ("N", "sim.: night clock"),
                       ("W", "sim.: wall clock")):
        v = np.array([x["beta_N"]["est"] for x in syn["o3"][truth]["rows"]])
        rows.append((lab, float(np.median(v)), float(np.percentile(v, 10)), float(np.percentile(v, 90)), truth))
    for i, (lab, e, lo, hi, kind) in enumerate(rows[::-1]):
        if kind == "data":
            ax.errorbar([e], [i], xerr=[[e - lo], [hi - e]], fmt="o", color=vs.FIELD, mec=vs.INK, mew=0.5, ms=4.5,
                        capsize=1.8, lw=1.2)
        else:
            col = vs.C["green"] if kind == "N" else vs.MUTED
            ax.errorbar([e], [i], xerr=[[e - lo], [hi - e]], fmt="s", color=col, mfc="white", mec=col, ms=4,
                        capsize=1.5, lw=1.0)
    ax.axvline(0, color=vs.INK2, lw=0.6)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=6.3)
    ax.set_xlabel(r"night step at fixed active lag $\beta_N$")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(-0.3, 0.08)
    ax.set_title("(c) no step at night", loc="left")
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--period", default="G10")
    a = ap.parse_args()
    vs.use()
    o1 = json.load(open(D / "results/o1_bge_small_style_resid.json"))
    card = {m: json.load(open(D / f"results/card_{m}_style_resid.json")) for m in ("bge_small", "gte_modernbert")}
    syn = json.load(open(D / "synthetic/synthetic.json"))
    fig = plt.figure(figsize=(vs.W["double"], 2.4))
    gs = fig.add_gridspec(1, 3, width_ratios=[0.95, 1.25, 1.0], wspace=0.55)
    a0, a1, a2 = (fig.add_subplot(gs[0, i]) for i in range(3))
    panel_sim(a0)
    sN, sH, r = panel_period(a1, o1, a.period)
    rows = panel_beta(a2, {m: card[m]["o3"] for m in card}, syn)
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    print(a.period, "SSE N %.4f H %.4f (card ratio %.2f, winner %s)" % (sN, sH, r["sse"]["H"] / r["sse"]["N"], r["winner"]))
    for x in rows:
        print(" ", x)
    c = card["bge_small"]["o1"]; g = card["gte_modernbert"]["o1"]
    print("decay periods", c["n_with_decay"], "share H<=N", c["share_H_le_N_decay"], g["share_H_le_N_decay"],
          "night wins", c["winner_share_decay"]["N"], g["winner_share_decay"]["N"])


if __name__ == "__main__":
    main()
