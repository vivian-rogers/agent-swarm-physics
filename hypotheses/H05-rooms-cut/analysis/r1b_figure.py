"""H05 round 1b page-2 figure: (a) HH248 talk coupling on co-location with/without ledger reads; (b) NE42 stay pairs."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[3]
d = json.loads((ROOT / "data/processed/H05-rooms-cut/r1b/r1b_reads.json").read_text())
plt.rcParams.update({"font.family": "serif", "font.size": 7, "axes.linewidth": 0.5, "pdf.fonttype": 42})
fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.2))
labs, vals, ses, cols = [], [], [], []
for m, c in (("none", "#3f6fb5"), ("trim", "#c2662d")):
    t = d[f"HH248_{m}"]["talk"]["all_III"]["kappa_x"]
    for nm, (mdl, k) in (("room only", ("M0_coloc", "coloc")), ("room | reads", ("M1_coloc_plus_lreads", "coloc")),
                         ("reads | room", ("M1_coloc_plus_lreads", "lreads"))):
        labs.append(f"{nm}\n{'fixed' if m == 'none' else 'trim'}"); vals.append(t[mdl][k]["beta"]); ses.append(1.96 * t[mdl][k]["se"]); cols.append(c)
ax[0].bar(range(len(vals)), vals, yerr=ses, color=cols, capsize=2)
ax[0].axhline(0, color="k", lw=0.5); ax[0].set_xticks(range(len(vals))); ax[0].set_xticklabels(labs, fontsize=5)
ax[0].set_ylabel(r"TWFE coefficient on talk $\kappa_x$")
n = d["NE42_none"]["talk"]["kappa_x"]; r = d["NE42_none"]["talk"]["reads"]
ax[1].plot([39, 40, 41], [n["level_39"], n["level_40"], n["level_41"]], "o-", color="#3f6fb5", label=r"talk $\kappa_x$")
ax[1].set_xticks([39, 40, 41]); ax[1].set_xticklabels(["#39 split", "#40 merged", "#41 split"]); ax[1].set_ylabel(r"stay pairs' talk $\kappa_x$")
a2 = ax[1].twinx(); a2.plot([39, 40, 41], [r["level_39"], r["level_40"], r["level_41"]], "s--", color="0.5"); a2.set_ylabel("ledger reads / pair-day", color="0.4")
fig.tight_layout(); fig.savefig(ROOT / "hypotheses/H05-rooms-cut/figures/r1b_summary_obs2.pdf")
