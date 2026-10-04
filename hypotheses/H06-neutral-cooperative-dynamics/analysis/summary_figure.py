"""One focused observables figure for the H06 summary page: figures/summary_obs.pdf.

(a) Simpson lambda per period (intention clusters km24): observed vs the 95% predictive intervals of the three fitted
    copying models and the independent-agents (day-shift) null mean. (b) copy-consistency: share of non-novel switches
    to a project another agent holds; every copying model predicts ~1.
Usage: uv run python hypotheses/H06-neutral-cooperative-dynamics/analysis/summary_figure.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figures as F  # noqa: E402

plt.rcParams.update({"font.size": 7.5, "axes.spines.top": False, "axes.spines.right": False})


def main():
    order = F.ORDER
    fig, axes = plt.subplots(2, 1, figsize=(4.4, 3.1), sharex=True, gridspec_kw={"height_ratios": [1.15, 1]})
    for ax, st in zip(axes, ("lam", "copyfrac")):
        for i, s in enumerate(order):
            r = F.load(s)
            v = r["sets"].get("km24", {}) if r else {}
            if not v.get("testable"):
                continue
            for j, m in enumerate(("ncd", "hubbell", "conformist")):
                pr = v["fits"][m]["pred"][st]
                ax.plot([i - 0.22 + j * 0.13] * 2, [pr[1], pr[2]], color=F.COL[m], lw=2.4, alpha=0.8, solid_capstyle="butt")
            obs = v["copyfrac"] if st == "copyfrac" else v["obs"][st]
            nul = v.get("null_ind", {}).get("lam_mean" if st == "lam" else "copy_mean")
            if nul is not None:
                ax.plot(i + 0.24, nul, "x", color="#52514e", ms=4, mew=1, zorder=4)
            ax.plot(i + 0.24, obs, "*", color="#0b0b0b", ms=6.5, zorder=5)
        for x in (4.5, 8.5):
            ax.axvline(x, color="#c9c7c0", lw=0.6)
    axes[0].set_ylabel("Simpson λ̄")
    axes[1].set_ylabel("copy-consistency")
    axes[0].text(-0.5, 0.95, "(a)", fontsize=8, fontweight="bold")
    axes[1].text(-0.5, 1.02, "(b)", fontsize=8, fontweight="bold")
    axes[1].set_ylim(0, 1.08)
    axes[1].set_xticks(range(len(order)))
    axes[1].set_xticklabels([F.name(s).replace("#51", "#51") for s in order], fontsize=6.3, rotation=0)
    for x, lab in ((2, "free weeks"), (6.5, "shared goal"), (10, "#51 private goals")):
        axes[1].text(x, -0.42, lab, ha="center", fontsize=6.5, color="#52514e", transform=axes[1].get_xaxis_transform())
    axes[0].legend(handles=[Line2D([], [], color=F.COL[m], lw=2.4, label=lab) for m, lab in
                            (("ncd", "NCD"), ("hubbell", "Hubbell"), ("conformist", "herding"))] +
                   [Line2D([], [], marker="*", ls="", color="#0b0b0b", label="observed"),
                    Line2D([], [], marker="x", ls="", color="#52514e", label="independent agents")],
                   ncol=5, fontsize=5.8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.2), handlelength=1.2, columnspacing=0.8)
    fig.tight_layout(h_pad=0.4)
    fig.savefig(F.FIG / "summary_obs.pdf", bbox_inches="tight")
    print("summary_obs.pdf written")


if __name__ == "__main__":
    main()
