"""One-page summary figure for H05 round 1 (exploratory, non-holdout).

Reads data/processed/H05-rooms-cut/{explore_bin1,explore_bin5,mf_blocks}.json; writes figures/summary_round1.pdf.
Usage: uv run python hypotheses/H05-rooms-cut/analysis/figure_summary.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H05-rooms-cut"
FIG = Path(__file__).resolve().parents[1] / "figures"
IN, OUTC, NULLC = "#1b9e77", "#9a9a9a", "#d95f02"


def main():
    b1 = json.loads((DATA / "explore_bin1.json").read_text())
    b5 = json.loads((DATA / "explore_bin5.json").read_text())
    mf = json.loads((DATA / "mf_blocks.json").read_text())
    fig, ax = plt.subplots(2, 2, figsize=(10, 6.4))

    # (a) kinetic-Ising J_sym, talk spins, within vs cross
    a = ax[0, 0]
    ks = [k for k in b1["X2"]["talk"] if "J_sym" in b1["X2"]["talk"][k]]
    x = np.arange(len(ks))
    w = [b1["X2"]["talk"][k]["J_sym"]["within"] for k in ks]; c = [b1["X2"]["talk"][k]["J_sym"]["cross"] for k in ks]
    a.bar(x - 0.2, w, 0.4, color=IN, label="within room"); a.bar(x + 0.2, c, 0.4, color=OUTC, label="cross room")
    for xi, k in zip(x, ks):
        a.text(xi, max(w[xi], c[xi]) + 0.005, f"p={b1['X2']['talk'][k]['J_sym']['p_perm']:.2f}", ha="center", fontsize=6)
    a.axhline(0, color="k", lw=0.5); a.set_xticks(x); a.set_xticklabels([f"#{k}" for k in ks], fontsize=7)
    a.set_ylabel("J_sym (kinetic Ising)", fontsize=8); a.legend(fontsize=7, frameon=False)
    a.set_title("(a) Talk spins: rooms are coupled blocks\n(#35-36 regime II; p = room-label permutation)", fontsize=8)

    # (b) block mean field, talk
    a = ax[0, 1]
    ks = list(mf["MF1"]["talk"]); x = np.arange(len(ks))
    for off, nm, col in ((-0.15, "J_in", IN), (0.15, "J_out", OUTC)):
        v = np.array([mf["MF1"]["talk"][k][nm] for k in ks]); ci = np.array([mf["MF1"]["talk"][k][nm + "_ci95"] for k in ks])
        a.errorbar(x + off, v, yerr=[v - ci[:, 0], ci[:, 1] - v], fmt="o", color=col, ms=4, capsize=2, label=nm)
    a.axhline(0, color="k", lw=0.5); a.set_xticks(x); a.set_xticklabels([f"#{k}" for k in ks], fontsize=7)
    a.legend(fontsize=7, frameon=False); a.set_ylabel("block coupling (naive MF)", fontsize=8)
    a.set_title("(b) H05-MF two-block mean field, talk spins\n(day-bootstrap 95% CI)", fontsize=8)

    # (c) pooled two-way FE: beta(co-location) +- 1.96 SE
    a = ax[1, 0]
    rows = []
    for spin in ("talk", "active"):
        for era, lab in (("all_III", "all III"), ("two_room_era_37_44", "#37-#44")):
            for y in ("c0_x", "kappa_x"):
                for bn, r in (("1 min", b1), ("5 min", b5)):
                    q = r["X4"][spin][era][y]
                    rows.append((f"{spin} {y} {lab} [{bn}]", q["beta"], q["se_twoway"], spin))
    for k, (lab, be, se, spin) in enumerate(rows):
        a.errorbar(be, k, xerr=1.96 * se, fmt="o", ms=3, color=IN if spin == "talk" else "#7570b3", capsize=2)
    a.axvline(0, color="k", lw=0.6)
    a.set_yticks(range(len(rows))); a.set_yticklabels([r[0] for r in rows], fontsize=5.5)
    a.set_xlabel("β(co-location), pair & day fixed effects (95% CI, two-way clustered)", fontsize=7)
    a.set_title("(c) Pooled pair-day DiD: co-location raises talk coupling, not activity coupling", fontsize=8)

    # (d) EP per agent-hour vs cross-day surrogate null
    a = ax[1, 1]
    ks = list(b1["X5"]["active"]); x = np.arange(len(ks))
    v = np.array([b1["X5"]["active"][k]["newton_cf_truncated_per_agent_hour"] for k in ks])
    nm = np.array([b1["X5"]["active"][k]["crossday_null_newton_per_agent_hour_mean"] for k in ks])
    ns = np.array([b1["X5"]["active"][k]["crossday_null_newton_per_agent_hour_sd"] for k in ks])
    ml = np.array([b1["X5"]["active"][k]["heldout_ml_per_agent_hour"] for k in ks])
    a.fill_between(x, nm - 2 * ns, nm + 2 * ns, color=NULLC, alpha=0.2, label="cross-day null ±2 sd")
    a.plot(x, v, "o-", color="k", ms=3, lw=0.8, label="Newton bound (cross-fitted)")
    a.plot(x, ml, "s", color="#888", ms=3, label="held-out ML bound")
    a.axhline(0, color="k", lw=0.5)
    a.set_xticks(x); a.set_xticklabels([k.replace("#51 2026-", "#51 ") for k in ks], fontsize=5.5, rotation=60)
    a.set_ylabel("pairwise EP bound, nats per agent-hour", fontsize=8); a.legend(fontsize=6, frameon=False)
    a.set_title("(d) Active spins: whole-swarm EP is at the null level", fontsize=8)
    fig.suptitle("H05 round 1 (exploratory, non-holdout, 1-min bins unless marked)", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "summary_round1.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
