"""H103 figures: figures/summary_obs.pdf (clock comparison per period; night step per unit) and
figures/summary_synthetic.pdf (clock-selection accuracy and the O3 night step under each planted truth)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
H = HERE.parent
DATA = H.parents[1] / "data/processed/H103-nights-demagnetize"
FIG = H / "figures"
C = {"I": "#2a78d6", "II": "#eb6834", "III": "#1baf7a", "ink": "#3d3d3a", "grid": "#d9d8d2", "gte": "#e87ba4"}
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": C["ink"], "axes.labelcolor": C["ink"],
                     "xtick.color": C["ink"], "ytick.color": C["ink"], "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False})


def main():
    FIG.mkdir(exist_ok=True)
    o1 = json.loads((DATA / "results/o1_bge_small_style_resid.json").read_text())
    o1g = json.loads((DATA / "results/o1_gte_modernbert_style_resid.json").read_text())
    o3 = json.loads((DATA / "results/o3_bge_small_style_resid.json").read_text())
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.4), gridspec_kw={"width_ratios": [1.6, 1]})
    names = list(o1)
    for i, n in enumerate(names):
        r = o1[n]
        y = np.log(r["sse"]["H"] / r["sse"]["N"])
        mk = "o" if r["verdict"] != "descriptive" else "x"
        a.plot(i, y, mk, ms=3.5, color=C[r["regime"]], mfc=C[r["regime"]] if mk == "o" else "none")
        if n in o1g:
            g = o1g[n]
            a.plot(i + 0.2, np.log(g["sse"]["H"] / g["sse"]["N"]), "D", ms=2.4, mfc="white", mec=C["gte"], mew=0.8)
    a.axhline(0, color=C["ink"], lw=0.7, ls="--")
    a.set_xticks(range(len(names))); a.set_xticklabels([n[1:] for n in names], rotation=90, fontsize=5.5)
    a.set_ylabel("ln SSE(active h) / SSE(night)")
    a.text(0.01, 0.97, "(a) > 0: night clock fits better; dots: decay present; x: none; diamonds: gte",
           transform=a.transAxes, va="top", fontsize=6.3)
    units = list(o3)
    for i, u in enumerate(units):
        r = o3[u]
        lo, hi, e = (np.clip(r["beta_N"][k], -0.4, 0.4) for k in ("lo", "hi", "est"))
        b.plot([lo, hi], [i, i], color=C[r["regime"]], lw=1.0)
        b.plot(e, i, "o" if abs(r["beta_N"]["est"]) <= 0.4 else ">", ms=2.8, color=C[r["regime"]])
    b.axvline(0, color=C["ink"], lw=0.7, ls="--")
    b.set_xlim(-0.42, 0.42)
    b.set_yticks(range(len(units))); b.set_yticklabels(units, fontsize=5)
    b.set_xlabel("night step β_N (self-overlap)")
    b.text(0.02, 0.99, "(b) clipped at ±0.4", transform=b.transAxes, va="top", fontsize=6.5)
    fig.tight_layout(); fig.savefig(FIG / "summary_obs.pdf")

    syn = json.loads((DATA / "synthetic/synthetic.json").read_text())
    sel = syn["o1_selection"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(3.4, 1.9))
    truths = ["N", "H", "W", "R", "0", "ToD"]
    M = np.array([[sel[t]["winner_share"][c] for c in ["N", "H", "W", "R"]] for t in truths])
    a.imshow(M, cmap="Greys", vmin=0, vmax=1, aspect="auto")
    for i in range(M.shape[0]):
        for k in range(M.shape[1]):
            a.text(k, i, f"{M[i, k]:.2f}", ha="center", va="center", fontsize=5, color="white" if M[i, k] > 0.5 else C["ink"])
    a.set_xticks(range(4)); a.set_xticklabels(["N", "H", "W", "R"]); a.set_yticks(range(len(truths))); a.set_yticklabels(truths)
    a.set_xlabel("winning clock"); a.set_ylabel("planted truth")
    o3s = syn["o3"]
    ts = [t for t in ("H", "ToD", "N", "W") if t in o3s]
    for i, t in enumerate(ts):
        v = [x["beta_N"]["est"] for x in o3s[t]["rows"]]
        b.plot(v, np.full(len(v), i) + np.random.default_rng(i).uniform(-0.15, 0.15, len(v)), "o", ms=2, color=C["ink"])
    b.axvline(0, color=C["grid"], lw=0.8)
    b.set_yticks(range(len(ts))); b.set_yticklabels(ts); b.set_xlabel("β_N (O3)")
    fig.tight_layout(); fig.savefig(FIG / "summary_synthetic.pdf")


if __name__ == "__main__":
    main()
