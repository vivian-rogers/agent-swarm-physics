"""Two-panel observables figure for the H05 one-page summary (no new analysis).

Reads the confirmatory output data/processed/H05-rooms-cut/confirm/confirm_ne12.json (NE15 split, locked-holdout
pre window; post window #35 not held out) and writes figures/summary_obs.pdf:
  (a) pair difference-in-differences at the 03-16 split (cut pairs vs. pairs that stayed together), talk and active
      spins, with the 02-25 placebo (no pair separated) for comparison; day-bootstrap 95% CIs, permutation p.
  (b) two-block mean-field couplings J_in / J_out (talk spins) before vs. after the split.
Usage: uv run python hypotheses/H05-rooms-cut/analysis/summary_figure.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H05-rooms-cut/confirm/confirm_ne12.json"
OUT = Path(__file__).resolve().parents[1] / "figures/summary_obs.pdf"
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#8a8984"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "font.family": "sans-serif"})


def main():
    d = json.loads(DATA.read_text())
    cs, pl = d["C_split"], d["A_placebo"]
    rows = []  # (label, est, lo, hi, color, note)
    for spin, col in (("talk", BLUE), ("active", GRAY)):
        for y, lab in (("kappa_x", "κ_x"), ("c0_x", "c0_x")):
            q = cs[spin][y]["cut"]
            rows.append((f"{spin} {lab}", q["did"], *q["ci95_dayboot"], col, f"p={q['p_assign_perm_2sided']:.2f}"))
    for y, lab in (("kappa_x", "κ_x"), ("c0_x", "c0_x")):
        q = pl["talk"][y]
        rows.append((f"placebo {lab}", q["post_minus_pre"], *q["ci95"], ORANGE, ""))

    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [1.25, 1]})
    # (a) forest plot of the pair DiD
    ys = list(range(len(rows)))[::-1]
    for yv, (lab, est, lo, hi, col, note) in zip(ys, rows):
        a.plot([lo, hi], [yv, yv], color=col, lw=1.6, solid_capstyle="butt")
        a.plot(est, yv, "o", color=col, ms=4.5, mec="white", mew=0.8, zorder=3)
        if note:
            a.text(0.075, yv, note, va="center", ha="right", fontsize=6, color=INK2)
    a.axvline(0, color=INK2, lw=0.7)
    a.text(0.078, 0.5, "02-25, talk,\nno pair cut\n(post − pre)", va="center", ha="right", fontsize=5.6,
           color=INK2)
    a.axhline(1.5, color=GRID, lw=0.8)
    a.set_yticks(ys)
    a.set_yticklabels([r[0] for r in rows], fontsize=6.3)
    a.set_xlim(-0.075, 0.08)
    a.set_xlabel("pair DiD (cut − stayed), corr. units", fontsize=6.5)
    a.set_title("(a) NE15 split: cut pairs decouple\n(talk = C1, primary; 18 cut, 37 stayed)", fontsize=6.8,
                loc="left", color=INK)
    a.tick_params(axis="both", length=2)

    # (b) block mean-field couplings before / after
    mf = d["E_MF"]["talk"]
    xs = {"C_pre": 0, "C_post": 1}
    for nm, col, off, lab in (("J_in", BLUE, -0.06, "J_in (in room)"), ("J_out", ORANGE, 0.06, "J_out (cross)")):
        v = [mf[w][nm] for w in xs]
        ci = [mf[w][nm + "_ci95"] for w in xs]
        x = [xs[w] + off for w in xs]
        b.plot(x, v, color=col, lw=1.2, alpha=0.6)
        for xi, vi, (lo, hi) in zip(x, v, ci):
            b.plot([xi, xi], [lo, hi], color=col, lw=1.6, solid_capstyle="butt")
            b.plot(xi, vi, "o", color=col, ms=4.5, mec="white", mew=0.8, zorder=3, label=lab if xi == x[0] else None)
    b.axhline(0, color=INK2, lw=0.7)
    b.set_xticks([0, 1])
    b.set_xticklabels(["pre #33–34\n(held out)", "post #35\n(seen in rd 1)"], fontsize=6)
    b.set_xlim(-0.45, 1.45)
    b.set_ylim(-0.12, 0.42)
    b.set_ylabel("block coupling (naive MF), talk", fontsize=6.5)
    b.set_title("(b) Two-block mean field:\nJ_out → 0, but J_in rises ×6", fontsize=6.8, loc="left", color=INK)
    b.legend(fontsize=5.8, frameon=False, loc="upper left", handlelength=1.0)
    b.tick_params(axis="both", length=2)
    fig.tight_layout(pad=0.3, w_pad=0.8)
    fig.savefig(OUT)
    plt.close(fig)
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
