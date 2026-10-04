"""H70 figures: figures/summary_obs.pdf (per-period I_A and the pooled kappa table) and figures/summary_synthetic.pdf."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
H = HERE.parent
DATA = H.parents[1] / "data/processed/H70-artifact-store-semantic-info"
FIG = H / "figures"
C = {"call": "#2a78d6", "day": "#eb6834", "A": "#2a78d6", "M": "#eda100", "R": "#1baf7a", "C": "#e87ba4",
     "ink": "#3d3d3a", "grid": "#d9d8d2"}
plt.rcParams.update({"font.size": 7.5, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})


def ci(r, k):
    c = r.get(k + "_ci") or [None, None]
    return (np.nan, np.nan) if c[0] is None else tuple(c)


def main():
    per = json.loads((DATA / "results/periods.json").read_text())
    nat = json.loads((DATA / "results/natives.json").read_text())
    FIG.mkdir(exist_ok=True)
    fig = plt.figure(figsize=(7.0, 2.4))
    gs = fig.add_gridspec(1, 3, width_ratios=[2.0, 1, 1])
    a = fig.add_subplot(gs[0])
    names = list(per)
    for i, p in enumerate(names):
        for j, sc in enumerate(("call", "day")):
            r = per[p].get(sc, {}).get("A")
            if not r:
                continue
            lo, hi = ci(r, "I")
            x = i + (j - 0.5) * 0.3
            a.plot([x, x], [lo, hi], color=C[sc], lw=1.1)
            a.plot(x, r["I"], "o", ms=3, color=C[sc], label=sc + " scale" if i == 0 or (sc == "call" and p == "G36") else None)
    a.axhline(0, color=C["grid"], lw=0.8, zorder=0)
    a.set_xticks(range(len(names)))
    a.set_xticklabels([n[1:] for n in names], fontsize=6)
    a.set_xlabel("goal period")
    a.set_ylabel("I_A (bits beyond agent identity)")
    a.legend(fontsize=6, loc="upper left")
    a.set_title("(a) the own artifact predicts the next repo", fontsize=7, loc="left")
    t = nat["NE41"]["call_regime3"]
    chans = ["A", "M", "R", "C"]
    b = fig.add_subplot(gs[1])
    for k, ch in enumerate(chans):
        r = t[ch]
        lo, hi = ci(r, "I")
        b.bar(k, r["I"], color=C[ch], width=0.6)
        b.plot([k, k], [lo, hi], color=C["ink"], lw=1)
    b.set_xticks(range(4))
    b.set_xticklabels(["artifact", "memory", "room", "context\n(destroyed)"], fontsize=5.5, rotation=30)
    b.set_ylabel("I_c (bits)")
    b.set_title("(b) information", fontsize=7, loc="left")
    c = fig.add_subplot(gs[2])
    for k, ch in enumerate(chans):
        r = t[ch]
        lo, hi = ci(r, "dV_rel")
        c.bar(k, r["dV_rel"], color=C[ch], width=0.6)
        c.plot([k, k], [lo, hi], color=C["ink"], lw=1)
    c.axhline(0, color=C["grid"], lw=0.8)
    c.set_xticks(range(4))
    c.set_xticklabels(["artifact", "memory", "room", "context\n(lost)"], fontsize=5.5, rotation=30)
    c.set_ylabel("ΔV_rel (share of commits)")
    c.set_title("(c) value", fontsize=7, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    syn = json.loads((DATA / "synthetic/synthetic.json").read_text())
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.0))
    keys = list(syn)
    for wi, (w, col) in enumerate((("value", "#2a78d6"), ("reading_precedes_writing", "#eb6834"), ("null", "#8a8983"))):
        ys = [np.mean([syn[k][f"{w}|p{p}"]["dV_rel_mean"] for p in (0.0, 0.6)]) for k in keys]
        sd = [np.mean([syn[k][f"{w}|p{p}"]["dV_rel_sd"] for p in (0.0, 0.6)]) for k in keys]
        x = np.arange(len(keys)) + (wi - 1) * 0.25
        a.errorbar(x, ys, yerr=sd, fmt="o", ms=3, color=col, lw=1, label={"value": "planted +0.30",
                   "reading_precedes_writing": "reading ×1.3 both arms (0)", "null": "null (0)"}[w])
        rr = [np.mean([syn[k][f"{w}|p{p}"]["reject_rate"] for p in (0.0, 0.6)]) for k in keys]
        b.bar(x, rr, width=0.25, color=col)
    for ax in (a, b):
        ax.set_xticks(range(len(keys)))
        ax.set_xticklabels([k.replace(":", "\n") for k in keys], fontsize=5.5)
    a.axhline(0.3, color=C["grid"], lw=0.8, ls="--")
    a.axhline(0, color=C["grid"], lw=0.8)
    a.set_ylabel("recovered ΔV_rel")
    a.set_ylim(-0.6, 1.2)
    a.legend(fontsize=5.5, loc="upper left")
    a.set_title("(a) channel value recovered on real skeletons", fontsize=7, loc="left")
    b.axhline(0.05, color=C["grid"], lw=0.8, ls="--")
    b.set_ylabel("rejection rate")
    b.set_title("(b) power (blue) and size (orange, gray)", fontsize=7, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_synthetic.pdf")


if __name__ == "__main__":
    main()
