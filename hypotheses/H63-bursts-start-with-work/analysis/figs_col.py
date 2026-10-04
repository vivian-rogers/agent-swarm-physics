"""Column-width summary figures for H63 (summary page)."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

import h63lib as L

FIG = L.ROOT / "hypotheses/H63-bursts-start-with-work/figures"
plt.rcParams.update({"font.size": 7})
s = json.loads((L.OUT / "results/summary.json").read_text())
d = pl.read_parquet(L.OUT / "results/periods.parquet")
fig, ax = plt.subplots(figsize=(3.4, 2.1))
cats = [("S", "state\nchange"), ("R", "routine\ncommit"), ("L", "chat\nlink"), ("B", "project\nbirth")]
x = np.arange(4)
for k, (lab, c) in enumerate((("herding bursts (317)", "#c0392b"), ("1–2-agent clusters (5,470)", "#7f8c8d"))):
    v = [np.array(s[f"counts_{t}"])[k, 0] / np.array(s[f"counts_{t}"])[k].sum() for t, _ in cats]
    ax.bar(x + (k - 0.5) * 0.36, v, 0.36, color=c, label=lab)
ax.set_xticks(x, [c[1] for c in cats])
ax.set_ylabel("share with the event in the\n60 min before the follower onset")
ax.legend(frameon=False, fontsize=6, loc="upper left")
fig.tight_layout()
fig.savefig(FIG / "summary_obs_col.pdf")
plt.close(fig)
H = d.filter((pl.col("h_n_events") >= 50) & pl.col("h_dS_se").is_not_null()).sort("goal_no")
g = H["goal_no"].to_numpy()
fig, ax = plt.subplots(figsize=(3.4, 2.1))
for k, (c_, colr, lab) in enumerate((("dS", "#c0392b", "state change: last − next 60 min"),
                                     ("dL", "#2c7fb8", "chat link: last − next 60 min"))):
    e, lo, hi = H[f"h_{c_}"].to_numpy(), H[f"h_{c_}_lo"].to_numpy(), H[f"h_{c_}_hi"].to_numpy()
    yy = np.arange(len(g)) + (k - 0.5) * 0.3
    ax.errorbar(np.clip(e, -2.5, 3), yy, xerr=[np.clip(e - lo, 0, 2.5), np.clip(hi - e, 0, 2.5)], fmt="o", ms=2.5,
                color=colr, lw=0.6, label=lab)
for k, (c_, colr) in enumerate((("dS", "#c0392b"), ("dL", "#2c7fb8"))):
    p = s[f"re_{c_}"]
    ax.errorbar(p["mean"], len(g) + 0.5 + (k - 0.5) * 0.3, xerr=[[p["mean"] - p["lo"]], [p["hi"] - p["mean"]]],
                fmt="D", ms=3.5, color=colr, lw=1.2)
ax.axvline(0, color="k", lw=0.5)
ax.set_yticks(list(range(len(g))) + [len(g) + 0.5], [f"#{x}" for x in g] + ["pooled"], fontsize=6)
ax.set_xlabel("lead–lag contrast in arrival log-hazard")
ax.legend(frameon=False, fontsize=5.5, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
fig.tight_layout()
fig.savefig(FIG / "leadlag_col.pdf")
plt.close(fig)
