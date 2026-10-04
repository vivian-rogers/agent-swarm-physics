"""H68 figures: figures/summary_obs.pdf (per-agent exponents by period) and summary_obs2.pdf (synthetic)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D = ROOT / "data/processed/H68-dilution-mixture"
FIG = HERE.parent / "figures"
LABC = {"Anthropic": "#c4642b", "OpenAI": "#2a2a2a", "Google": "#2a78d6", "xAI": "#7b4fd6", "DeepSeek": "#0ca30c",
        "Moonshot": "#e3a21a", "Zhipu": "#d03b8b", "Meta": "#18a5a5", "Alibaba": "#8a6d3b", "Mistral": "#999999"}


def main():
    FIG.mkdir(exist_ok=True)
    res = json.loads((D / "results.json").read_text())
    ag = pl.read_parquet(D / "agents_all.parquet")
    periods = list(res["periods"])
    fig, ax = plt.subplots(figsize=(4.8, 2.9))
    for i, p in enumerate(periods):
        t = ag.filter(pl.col("period") == p).sort("beta")
        n = t.height
        xs = i + (np.arange(n) - (n - 1) / 2) * min(0.8 / max(n, 1), 0.06)
        for x, b, s, lab in zip(xs, t["beta"], t["se"], t["lab"]):
            c = LABC.get(lab, "#999999")
            ax.plot([x, x], [b - 1.96 * s, b + 1.96 * s], color=c, lw=0.5, alpha=0.5)
            ax.plot(x, b, "o", ms=1.8, color=c)
        o = res["periods"][p]
        if o.get("mu") is not None:
            ax.plot([i - 0.4, i + 0.4], [o["mu"], o["mu"]], color="black", lw=1.0)
    ax.axhline(0, color="gray", lw=0.6, ls=":")
    ax.axhline(1, color="gray", lw=0.6, ls=":")
    ax.set_xticks(range(len(periods)))
    ax.set_xticklabels(periods, rotation=90, fontsize=6)
    ax.set_ylabel(r"per-agent exponent $\hat\beta_i$", fontsize=7)
    ax.set_ylim(-1.0, 2.0)
    ax.tick_params(axis="y", labelsize=7)
    for lab in sorted(set(ag["lab"].to_list())):
        ax.plot([], [], "o", ms=3, color=LABC.get(lab, "#999999"), label=lab)
    ax.legend(fontsize=5, ncol=5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.2))
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)

    w = pl.read_parquet(D / "synthetic/period_worlds.parquet").filter(pl.col("n_eligible") >= 6)
    fig, axs = plt.subplots(1, 2, figsize=(4.8, 1.9), gridspec_kw=dict(width_ratios=[1.1, 1]))
    names = {"W0": "one β", "W1": "spread 0.15", "W2": "H68 {0,1}", "W3": "{0.35, 0.95}"}
    worlds = ["W0", "W1", "W2", "W3"]
    p1 = [w.filter(pl.col("world") == x)["p1"].cast(pl.Float64).mean() for x in worlds]
    lt = [(w.filter(pl.col("world") == x)["tau_hi"] < 0.35).cast(pl.Float64).mean() for x in worlds]
    xs = np.arange(4)
    axs[0].bar(xs - 0.2, p1, 0.4, color="#2a78d6", label="P1 passes")
    axs[0].bar(xs + 0.2, lt, 0.4, color="#9aa0a6", label=r"$\tau$ upper CI < 0.35")
    axs[0].set_xticks(xs)
    axs[0].set_xticklabels([names[x] for x in worlds], fontsize=6, rotation=20)
    axs[0].set_ylabel("rate (periods ≥ 6 agents)", fontsize=6.5)
    axs[0].tick_params(axis="y", labelsize=6.5)
    axs[0].legend(fontsize=5.5, frameon=False)
    real = [res["periods"][p]["tau"] for p in periods if "tau" in res["periods"][p] and res["periods"][p]["n_eligible"] >= 6]
    for x, c in zip(worlds, ("#9aa0a6", "#e3a21a", "#2a78d6", "#7b4fd6")):
        t = w.filter(pl.col("world") == x)["tau"].to_numpy()
        axs[1].hist(t, bins=np.linspace(0, 0.8, 33), histtype="step", color=c, density=True, label=names[x])
    axs[1].hist(real, bins=np.linspace(0, 0.8, 33), color="black", alpha=0.35, density=True, label="village")
    axs[1].set_xlabel(r"$\hat\tau$ (between-agent SD)", fontsize=6.5)
    axs[1].tick_params(labelsize=6)
    axs[1].legend(fontsize=5, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs2.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
