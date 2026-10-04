"""H15 one-page summary figure (figures/summary_obs.pdf, ~4.3 x 2.6 in), from existing outputs only.

Left: write rate per turn around consolidations, relative to turns -20..-11 (forced = exogenous 41-turn cap vs
voluntary), pooled over the non-holdout regime III periods. Right: day-scale value of information on V* (meta ΔV,
SD of the same-day residual, kal counterfactual) for memory loss, newcomers, rewrites (control) and chat cuts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h15common import FIG, OUT  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

plt.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 7.5, "axes.labelsize": 7})
res = json.loads((OUT / "results.json").read_text())
prof = pl.read_parquet(OUT / "consolidation_profile.parquet")

fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [1.25, 1]})
g = prof.group_by("kind", "off").agg(((pl.col("w_rate") * pl.col("n")).sum() / pl.col("n").sum()).alias("w")).sort("off")
for kind, c, lab in (("CF", "#b2182b", "forced (41-turn cap)"), ("CV", "#2166ac", "voluntary")):
    d = g.filter(pl.col("kind") == kind)
    off, w = d["off"].to_numpy(), d["w"].to_numpy()
    ref = w[(off >= -20) & (off <= -11)].mean()
    a.plot(off, w / ref, "-", lw=1.2, color=c, label=lab)
a.axvline(0, color="k", lw=0.5)
a.axhline(1, color="#999999", lw=0.5, ls=":")
a.axvspan(0.5, 10.5, color="#eeeeee", zorder=0)
ph = res["CTX"]
dips = [ph[u]["posthoc_rd"]["CF"]["rel_dip"] for u in ph if "CF" in ph[u].get("posthoc_rd", {})]
a.text(11.5, 0.08, f"forced:\n−{-np.median(dips) * 100:.0f}% writes\nin turns 1–10\n(8/9 periods)", ha="left",
       va="bottom", fontsize=5.8, color="#b2182b")
a.set_xlabel("turn relative to context erasure")
a.set_ylabel("write rate / rate at turns −20…−11")
a.set_title("context window: erased every 41 turns")
a.set_ylim(0, 2.0)
a.legend(frameon=False, fontsize=5.8, loc="upper left")

vm = res["vstar_meta"]
rows = [("memory loss", "ML"), ("newcomer\n(empty memory)", "MN"), ("rewrite\n(control)", "MR"), ("chat cut", "CC")]
for i, (lab, t) in enumerate(rows):
    m = vm[t]["meta"]
    n = sum(x["n"] for x in vm[t]["units"].values())
    b.errorbar([m["mu"]], [i], xerr=[[m["mu"] - m["lo"]], [m["hi"] - m["mu"]]], fmt="o", ms=3.5,
               color="#444444" if t != "MR" else "#999999", capsize=2, lw=1)
    b.text(1.62, i, f"n={n}", va="center", fontsize=5.8, color="#666666")
b.axvline(0, color="k", lw=0.5)
b.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=6.3)
b.invert_yaxis()
b.set_xlim(-2.0, 1.9)
b.set_xlabel("day-scale ΔV on V* (SD)")
b.set_title("day scale (1–3 days)")
fig.tight_layout(pad=0.4, w_pad=0.8)
FIG.mkdir(exist_ok=True)
fig.savefig(FIG / "summary_obs.pdf")
print("wrote", FIG / "summary_obs.pdf")
