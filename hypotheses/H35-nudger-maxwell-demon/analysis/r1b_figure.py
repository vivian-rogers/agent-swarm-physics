"""H35 round 1b figure: what a first nudge buys on four outcomes (G51), and the response by trap age.
Usage: uv run python hypotheses/H35-nudger-maxwell-demon/analysis/r1b_figure.py  ->  figures/r1b_outcomes.pdf"""
from __future__ import annotations

import json
import os

os.environ.setdefault("POLARS_MAX_THREADS", "2")
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "data/processed/H35-nudger-maxwell-demon/G51/r1b"
r = json.loads((D / "results_r1b.json").read_text())
dd = json.loads((D / "results_r1b_did.json").read_text())
a = r["att"]
rows = [("active min / 30 min (round 1)", a["y30"]["first"], a["y30"]["control_mean"], a["y30"]["placebo"]),
        ("glance (any activity, 30 min)", a["y_glance30"]["first"], a["y_glance30"]["control_mean"], a["y_glance30"]["placebo"]),
        ("sustained run (30 min), matched", a["y_sust30"]["first"], a["y_sust30"]["control_mean"], a["y_sust30"]["placebo"]),
        ("work commits (60 min), matched", a["y_work60"]["first"], a["y_work60"]["control_mean"], a["y_work60"]["placebo"])]
fig, axs = plt.subplots(1, 2, figsize=(7.4, 2.7), gridspec_kw={"width_ratios": [1.3, 1]})
ax = axs[0]
for i, (lab, f, c, p) in enumerate(rows[::-1]):
    ax.errorbar(f[0] / c, i + 0.12, xerr=[[(f[0] - f[1]) / c], [(f[2] - f[0]) / c]], fmt="o", ms=3.5, color="k", lw=0.9)
    ax.errorbar(p[0] / c, i - 0.12, xerr=[[(p[0] - p[1]) / c], [(p[2] - p[0]) / c]], fmt="s", ms=3, color="#bbbbbb", lw=0.9)
n = len(rows)
for j, (k, lab, base) in enumerate((("sust_did_h", "sustained runs/h, DiD (post hoc)", a["y_sust30"]["control_mean"] * 2),
                                    ("work_did_h", "work commits/h, DiD (post hoc)", a["y_work60"]["control_mean"]))):
    f = dd[k]["first"]
    ax.errorbar(f[0] / base, n + j, xerr=[[(f[0] - f[1]) / base], [(f[2] - f[0]) / base]], fmt="D", ms=3.5, color="#c0392b", lw=0.9)
ax.set_yticks(range(n + 2))
ax.set_yticklabels([x[0] for x in rows[::-1]] + ["sustained runs/h, DiD (post hoc)", "work commits/h, DiD (post hoc)"], fontsize=6.5)
ax.axvline(0, color="0.5", lw=0.7)
ax.set_xlabel("effect of a first nudge / control mean (95% CI; grey = placebo window)", fontsize=7)
ax.set_title("(a) G51: a nudge buys glances, not work", fontsize=8)
ax.tick_params(labelsize=7)
ax = axs[1]
lab = ["0", "1", "2-3", "4-9", "≥10"]
for k, col, name in (("y30", "k", "active min"), ("y_glance30", "#2a6f97", "glance"), ("y_sust30", "#e67e22", "sustained (matched)")):
    g = np.array(r["k_eff"][k]["g_shrunk"], float)
    ax.plot(range(5), g / np.nanmax(np.abs(g)), "o-", ms=3, lw=1, color=col, label=name)
g = np.array(dd["work_did_h"]["k_eff"]["g_shrunk"], float)
ax.plot(range(5), g / np.nanmax(np.abs(g)), "D--", ms=3, lw=1, color="#c0392b", label="work DiD (post hoc)")
sh = np.array(r["k_eff"]["y30"]["share_of_nudges"], float)
ax.bar(range(5), sh, color="#dddddd", zorder=0, label="share of nudges")
ax.set_xticks(range(5))
ax.set_xticklabels(lab, fontsize=7)
ax.set_xlabel("trap age k (pause-chain length)", fontsize=7)
ax.set_ylabel("response per nudge / max", fontsize=7)
ax.set_title("(b) response by trap age (shrunk)", fontsize=8)
ax.legend(fontsize=5.5, frameon=False, loc="lower left")
ax.tick_params(labelsize=7)
fig.tight_layout()
fig.savefig(ROOT / "hypotheses/H35-nudger-maxwell-demon/figures/r1b_outcomes.pdf", bbox_inches="tight")
print("wrote figures/r1b_outcomes.pdf")
