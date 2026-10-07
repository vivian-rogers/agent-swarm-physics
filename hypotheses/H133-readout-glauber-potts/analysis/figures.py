"""H133 round-1 figures: figures/summary_obs.pdf (real data) and figures/summary_synth.pdf (synthetic validation)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
FIG = HERE.parent / "figures"
D = HERE.parents[2] / "data/processed/H133-readout-glauber-potts"
C_I, C_III, C_GREY = "#2a78d6", "#d03b3b", "#85847e"


def order_key(u):
    num = int("".join(ch for ch in u if ch.isdigit()))
    return (num, u)


def obs():
    res = json.loads((D / "results/units.json").read_text())
    summ = json.loads((D / "results/summary.json").read_text())
    units = sorted(res, key=order_key)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"width_ratios": [2.3, 1]})
    a = ax[0]
    for i, u in enumerate(units):
        r = res[u]["O4_nopt"]
        if not r.get("ok"):
            continue
        col = C_I if res[u]["regime"] == "I" else C_III
        a.plot([i, i], r["ci"], color=col, lw=1)
        a.plot(i, r["eta"], "o", color=col, ms=3)
    for key, col, lab in (("I", C_I, "regime I"), ("II_III", C_III, "regime II/III")):
        p = summ["eta_nopt"][key]
        if p["k"]:
            a.axhspan(p["ci"][0], p["ci"][1], color=col, alpha=0.15, lw=0)
            a.axhline(p["mean"], color=col, lw=0.8, ls="--", label=f"{lab} RE mean {p['mean']:+.2f}")
    a.axhline(0, color="k", lw=0.5)
    a.axhline(1, color=C_GREY, lw=0.5, ls=":")
    a.text(len(units) - 1, 0.97, "wall clock", ha="right", va="top", fontsize=6, color=C_GREY)
    a.set_xticks(range(len(units)))
    a.set_xticklabels(units, rotation=90, fontsize=5)
    a.set_ylabel(r"$\eta_\mathrm{sw}$ (background calls)", fontsize=7)
    a.tick_params(labelsize=6)
    a.legend(fontsize=6, frameon=False, loc="upper left")
    a.set_title("(a) switch-span elasticity per unit (A2 model, 95% CI)", fontsize=7)
    b = ax[1]
    labs, oe, lo, hi = [], [], [], []
    for grp, gl in (("II_III", "II/III"), ("I", "I")):
        for f, fl in (("nam", "nam."), ("un", "unn."), ("if", "infl.")):
            s = summ["EO_posthoc_sum"][grp][f]
            labs.append(f"{fl}\n{gl}")
            oe.append(s["OE"] if s["OE"] else np.nan)
            n_o = s["O"]
            # Poisson 95% interval of O over E (descriptive)
            from scipy import stats
            l_ = stats.chi2.ppf(0.025, 2 * n_o) / 2 if n_o > 0 else 0.0
            h_ = stats.chi2.ppf(0.975, 2 * n_o + 2) / 2
            lo.append(l_ / s["E"] if s["E"] else np.nan)
            hi.append(h_ / s["E"] if s["E"] else np.nan)
    x = np.arange(len(labs))
    cols = [C_III] * 3 + [C_I] * 3
    for i in x:
        b.plot([i, i], [lo[i], hi[i]], color=cols[i], lw=1)
        b.plot(i, oe[i], "s", color=cols[i], ms=4)
    b.axhline(1, color="k", lw=0.5)
    b.set_ylim(0, 3.6)
    b.set_xticks(x)
    b.set_xticklabels(labs, fontsize=5)
    b.tick_params(labelsize=6)
    b.set_ylabel("observed / expected hops (post hoc)", fontsize=7)
    b.set_title("(b) hops onto a project in a read", fontsize=7)
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "summary_obs.pdf")
    fig.savefig(FIG / "summary_obs.png", dpi=150)


def synth():
    c = json.loads((D / "synthetic/partC_eta.json").read_text())
    st = json.loads((D / "synthetic/partA_stacks.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.6))
    a = ax[0]
    worlds = ["W0", "W1", "W3", "W4", "W5"]
    sk = ["38a", "31a", "51c", "51h"]
    for j, u in enumerate(sk):
        for i, w in enumerate(worlds):
            s = c[u][w]["nopt"]
            x = i + (j - 1.5) * 0.15
            a.errorbar(x, s["median"], yerr=s["sd"] * 1.96, fmt="o", ms=3, lw=0.8,
                       color=[C_III, C_I, "#0ca30c", "#fab219"][j], label=u if i == 0 else None)
    a.axhline(0, color="k", lw=0.5)
    a.axhline(1, color=C_GREY, lw=0.5, ls=":")
    a.set_xticks(range(len(worlds)))
    a.set_xticklabels(["W0 null", "W1 H133", "W3 burst", "W4 wall", "W5 share"], fontsize=6)
    a.tick_params(labelsize=6)
    a.set_ylabel(r"$\hat\eta_\mathrm{sw}$ (median $\pm$ 1.96 sd)", fontsize=7)
    a.legend(fontsize=6, frameon=False, ncol=2)
    a.set_title(r"(a) $\eta_\mathrm{sw}$ recovery, 200 runs per world", fontsize=7)
    b = ax[1]
    g = [0.0, 0.5, 1.0, 2.0, 3.0]
    for name, col, lab in (("regime_II_III", C_III, "24 regime-II/III units"), ("G51_units", "#fab219", "12 #51 units"),
                           ("regime_I", C_I, "17 regime-I units")):
        b.plot(g, [st[name][f"g{x}"]["power_count_test"] for x in g], "o-", color=col, ms=3, lw=1, label=lab)
    b.axhline(0.8, color=C_GREY, lw=0.5, ls=":")
    b.axvline(1.0, color="k", lw=0.5, ls="--")
    b.set_xlabel(r"planted $\gamma_\mathrm{nam}$", fontsize=7)
    b.set_ylabel("power (stacked count test)", fontsize=7)
    b.tick_params(labelsize=6)
    b.legend(fontsize=6, frameon=False)
    b.set_title("(b) named-read power even when stacked", fontsize=7)
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "summary_synth.pdf")
    fig.savefig(FIG / "summary_synth.png", dpi=150)


if __name__ == "__main__":
    synth()
    obs()
