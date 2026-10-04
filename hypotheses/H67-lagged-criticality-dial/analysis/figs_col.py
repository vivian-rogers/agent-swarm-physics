"""Column-width summary figures for H67 (summary page)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

import h67lib as L

FIG = L.ROOT / "hypotheses/H67-lagged-criticality-dial/figures"
P = pl.read_parquet(L.OUT / "results/periods.parquet")
u = pl.read_parquet(L.OUT / "results/units.parquet").filter(pl.col("ok").fill_null(False))
col = {"I": "#2c7fb8", "II": "#7f8c8d", "III": "#c0392b"}
plt.rcParams.update({"font.size": 7})
fig, ax = plt.subplots(figsize=(3.4, 2.3))
for reg in ("I", "II", "III"):
    s = P.filter(pl.col("regime") == reg)
    ax.errorbar(s["g_eq"], s["g"], yerr=[s["g"] - s["g_lo"], s["g_hi"] - s["g"]], fmt="o", ms=3, color=col[reg],
                lw=0.6, label=f"regime {reg} ({s.height})")
ax.plot([-0.1, 0.45], [-0.1, 0.45], "k--", lw=0.6)
ax.axhline(0, color="k", lw=0.4)
ax.set_xlabel("equal-time talk dial $g_{eq}$ (same calls)")
ax.set_ylabel("read-out loop gain $g_{lag}$")
ax.legend(frameon=False, fontsize=6, loc="upper left")
fig.tight_layout()
fig.savefig(FIG / "summary_obs_col.pdf")
plt.close(fig)
s3 = u.filter(pl.col("regime") == "III").sort("N")
fig, ax = plt.subplots(figsize=(3.4, 1.9))
x = np.arange(s3.height)
ax.bar(x, s3["g_named"], color="#c0392b", label="messages naming the recipient")
ax.bar(x, s3["g_unnamed"], bottom=s3["g_named"], color="#f1948a", label="other messages")
ax.errorbar(x, s3["g"], yerr=[s3["g"] - s3["g_lo"], s3["g_hi"] - s3["g"]], fmt="k.", ms=2.5, lw=0.5)
ax.set_xticks(x, s3["unit_id"].to_list(), rotation=90, fontsize=5)
ax.set_ylabel("$g_{lag}$ (regime III units)")
ax.legend(frameon=False, fontsize=5.5, loc="upper left")
fig.tight_layout()
fig.savefig(FIG / "decomposition_col.pdf")
plt.close(fig)
