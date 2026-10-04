"""Synthetic-validation figure for H30 (figures/synthetic_validation.pdf).

(a) Recovery of the per-nudge activity response at G51-like sampling: truth, the H30 estimator (Amendments A1/A2) and
    H04's isolated matched design run unmodified on the same simulated swarms.
(b) Rate at which "chi_op is the same every day" is rejected (p < 0.05) when it IS the same every day (S0, S1, S5
    day-level activity shocks) and when it varies (S2), for Cochran's Q, the message permutation without day fixed
    effects, and the message permutation with day fixed effects (A2).
Run: uv run python hypotheses/H30-operator-susceptibility/analysis/figures_synth.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h30lib import FIG, OUT, json, np  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

S = json.loads((OUT / "synthetic" / "synthetic_results.json").read_text())
H = json.loads((OUT / "synthetic" / "h04_design_check.json").read_text())["summary"]
hmap = {(r["design"], r["scen"]): r for r in H}

fig, ax = plt.subplots(1, 2, figsize=(7.4, 2.7))
scen = [("S0_null", "no effect"), ("S1_const", "constant"), ("S3_aging", "aging"), ("S5_dayshock", "day shocks")]
x = np.arange(len(scen))
tru = [S[f"G51like|{s}"]["act_N_tgt"]["true_mean"] for s, _ in scen]
est = [S[f"G51like|{s}"]["act_N_tgt"]["est_mean"] for s, _ in scen]
h04 = [hmap.get(("G51like", s), {}).get("nudge_target_iso", np.nan) for s, _ in scen]
ax[0].bar(x - 0.27, tru, 0.25, color="#a0aec0", label="truth (per-kick)")
ax[0].bar(x, est, 0.25, color="#2b6cb0", label="H30 estimator")
ax[0].bar(x + 0.27, h04, 0.25, color="#c05621", label="H04 isolated design")
ax[0].axhline(0, color="0.4", lw=0.6)
ax[0].set_xticks(x); ax[0].set_xticklabels([l for _, l in scen], fontsize=7)
ax[0].set_ylabel("min per nudge (30 min)", fontsize=8)
ax[0].set_title("(a) nudge response recovery, G51-like", fontsize=8)
ax[0].legend(fontsize=6, frameon=False, loc="upper right")
cases = [("S0_null", "χ=0"), ("S1_const", "χ const"), ("S5_dayshock", "const +\nday shocks"), ("S2_hetero", "χ varies\n(power)")]
x = np.arange(len(cases))
q = [S[f"G51like|{s}"].get("stab_p_Q_rej05", np.nan) for s, _ in cases]
nofe = [S[f"G51like|{s}"].get("stab_nofe_p_perm_msg_rej05", np.nan) for s, _ in cases]
fe = [S[f"G51like|{s}"].get("stab_p_perm_msg_rej05", np.nan) for s, _ in cases]
ax[1].bar(x - 0.27, q, 0.25, color="#a0aec0", label="Cochran Q")
ax[1].bar(x, nofe, 0.25, color="#d69e2e", label="permutation, no day FE")
ax[1].bar(x + 0.27, fe, 0.25, color="#2b6cb0", label="permutation + day FE (A2)")
ax[1].axhline(0.05, color="k", lw=0.7, ls="--")
ax[1].set_xticks(x); ax[1].set_xticklabels([l for _, l in cases], fontsize=7)
ax[1].set_ylabel("share rejecting 'same χ every day'", fontsize=8)
ax[1].set_ylim(0, 1); ax[1].set_title("(b) day-to-day test calibration, G51-like", fontsize=8)
ax[1].legend(fontsize=6, frameon=False, loc="upper left")
for a in ax:
    a.tick_params(labelsize=7)
fig.tight_layout()
fig.savefig(FIG / "synthetic_validation.pdf")
print("wrote", FIG / "synthetic_validation.pdf", {"truth": tru, "h30": est, "h04": h04, "Q": q, "nofe": nofe, "fe": fe})
