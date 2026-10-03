"""Summary figures for H04 from the exploratory JSON outputs: mean-field forward check and Hawkes parameters."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h04lib import FIG, OUT  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def err(t):
    return t[0], [[t[0] - t[1]], [t[2] - t[0]]]


def fig_mf(k):
    labs = [l for l in ("I", "II", "III", "III_4h", "III_8h") if l in k]
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 3.4))
    x = np.arange(len(labs))
    for j, lab in enumerate(labs):
        m = k[lab]["mf"]
        y, e = err(m["tau_pred"]); axs[0].errorbar(j - 0.2, y, yerr=e, fmt="ks", ms=4, label="τ_pred = τ₀/(1−K)" if j == 0 else None)
        y, e = err(m["tau_m"]); axs[0].errorbar(j - 0.07, y, yerr=e, fmt="o", color="0.5", ms=4, label="τ_m (collective autocorr.)" if j == 0 else None)
        for dx, (kk, col, nm) in zip((0.07, 0.2, 0.33), (("human_all_iso", "#1f77b4", "τ_G human → room"),
                                                       ("nudge_target_iso", "#d62728", "τ_G nudge → target"),
                                                       ("human_mentioned_iso", "#2ca02c", "τ_G human → mentioned"))):
            v = m["kernels"].get(kk)
            if v and v["tau_G_relax"][0] is not None and v["tau_G_relax"][1] is not None:
                y, e = err(v["tau_G_relax"]); axs[0].errorbar(j + dx, y, yerr=e, fmt="D", color=col, ms=4, label=nm if lab == "III" else None)
        y, e = err(m["K"]); axs[1].errorbar(j, y, yerr=e, fmt="ko", ms=4)
    axs[0].set_yscale("log"); axs[0].set_xticks(x, labs); axs[0].set_ylabel("time (min)")
    axs[0].set_title("H04-MF: predicted vs measured decay", fontsize=9); axs[0].legend(fontsize=6, frameon=False)
    axs[1].set_xticks(x, labs); axs[1].set_ylabel("K = βJ₀(1−m²)"); axs[1].set_title("mean-field loop gain (detrended)", fontsize=9)
    fig.tight_layout(); fig.savefig(FIG / "mf_forward.pdf"); plt.close(fig)


def fig_hawkes(h):
    labs = [l for l in ("I", "II", "III", "III_4h", "III_8h", "NE10_pre", "NE10_post") if l in h]
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.2))
    for j, lab in enumerate(labs):
        r = h[lab]
        for ax, key in zip(axs, ("n", "eh", "en")):
            t = r.get(f"{key}_ci")
            if t:
                y, e = err(t); ax.errorbar(j, y, yerr=e, fmt="o", color="k", ms=4)
    for ax, t in zip(axs, ("branching ratio n", "η_human (msgs per human msg)", "η_nudge (msgs per nudge)")):
        ax.set_xticks(range(len(labs)), labs, rotation=35, fontsize=7); ax.set_title(t, fontsize=9)
    axs[0].axhline(1, color="k", lw=0.5, ls=":")
    fig.tight_layout(); fig.savefig(FIG / "hawkes.pdf"); plt.close(fig)


if __name__ == "__main__":
    k = json.loads((OUT / "explore_kernels.json").read_text())
    fig_mf(k)
    hp = OUT / "explore_hawkes.json"
    if hp.exists():
        fig_hawkes(json.loads(hp.read_text()))
    print("ok")
