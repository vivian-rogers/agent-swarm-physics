"""H71 figures: figures/summary_obs.pdf (per-period phi+ and mixed phi; autocorrelation vs one loop) and
figures/summary_synthetic.pdf (synthetic recovery and the sampling artifact)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
H = HERE.parent
DATA = H.parents[1] / "data/processed/H71-memory-homeostat"
FIG = H / "figures"
C = {"I": "#2a78d6", "II": "#eb6834", "III": "#1baf7a", "mixed": "#e87ba4", "ink": "#3d3d3a", "grid": "#d9d8d2"}
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": C["ink"], "axes.labelcolor": C["ink"],
                     "xtick.color": C["ink"], "ytick.color": C["ink"], "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False})


def main():
    per = json.loads((DATA / "results/periods.json").read_text())
    ph = json.loads((DATA / "results/posthoc.json").read_text())
    FIG.mkdir(exist_ok=True)
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.4), gridspec_kw={"width_ratios": [2.2, 1]})
    names = list(per)
    for i, p in enumerate(names):
        r = per[p]
        a.plot([i, i], [r["phi"]["lo"], r["phi"]["hi"]], color=C[r["regime"]], lw=1.2)
        a.plot(i, r["phi"]["est"], "o", ms=3.2, color=C[r["regime"]])
        if r["regime"] == "III":
            a.plot(i, r["mixed_phi"], "D", ms=3.2, mfc="white", mec=C["mixed"], mew=1.0)
    for y in (0, 1):
        a.axhline(y, color=C["grid"], lw=0.8, zorder=0)
    a.set_xticks(range(len(names)))
    a.set_xticklabels([n[1:] for n in names], rotation=90, fontsize=5.5)
    a.set_ylabel("lag-1 persistence per compression cycle")
    a.set_ylim(-0.75, 1.05)
    from matplotlib.lines import Line2D
    a.legend(handles=[Line2D([], [], marker="o", ls="", color=C[k], ms=3.5, label=f"φ⁺ regime {k}") for k in ("I", "II", "III")]
             + [Line2D([], [], marker="D", ls="", mfc="white", mec=C["mixed"], ms=3.5, label="mixed-phase φ (H09)")],
             loc="lower left", fontsize=6, ncol=2)
    a.set_title("(a) post-compression size reverts (0 < φ⁺ < 1); mixed series looks like overshoot", fontsize=7, loc="left")
    # (b) autocorrelation, pooled over periods: rho_k vs rho_1^k
    ks = np.arange(1, 4)
    for reg in ("I", "III"):
        rows = [ph[p] for p in ph if per[p]["regime"] == reg]
        rho = np.array([[q["rho1"], q["rho2"], q["rho3"]] for q in rows]).mean(0)
        b.plot(ks, rho, "o-", color=C[reg], ms=3.5, lw=1.4, label=f"observed, regime {reg}")
        b.plot(ks, rho[0] ** ks, "--", color=C[reg], lw=1.0, label=f"one loop ρ₁ᵏ, regime {reg}")
    b.set_xticks(ks)
    b.set_xlabel("lag k (compression cycles)")
    b.set_ylabel("autocorrelation of x⁺")
    b.set_ylim(0, 1)
    b.legend(fontsize=5.5, loc="lower left")
    b.set_title("(b) slower decay than one loop", fontsize=7, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    # synthetic
    syn = json.loads((DATA / "synthetic/synthetic.json").read_text())
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.1))
    cols = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
    for j, (sk, v) in enumerate(syn.items()):
        ws = v["worlds"]
        pl_ = [w["planted_phi"] for w in ws.values()]
        a.plot(pl_, [w["phi_hpj_mean"] for w in ws.values()], "o", ms=3, color=cols[j % 6], label=sk)
        b.plot(pl_, [w["mixed_mean"] for w in ws.values()], "o-", ms=3, lw=1, color=cols[j % 6], label=sk)
    a.plot([-0.4, 1.05], [-0.4, 1.05], color=C["grid"], lw=0.8, zorder=0)
    a.set_xlabel("planted φ⁺")
    a.set_ylabel("recovered φ⁺ (mean)")
    a.set_title("(a) φ⁺ recovered at real counts (bias ≤ 0.02)", fontsize=7, loc="left")
    a.legend(fontsize=5.5, ncol=2)
    b.axhline(0, color=C["grid"], lw=0.8, zorder=0)
    b.set_xlabel("planted φ⁺")
    b.set_ylabel("mixed-phase φ")
    b.set_title("(b) regime-III skeletons (one append per cycle) give φ < 0", fontsize=7, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_synthetic.pdf")


if __name__ == "__main__":
    main()
