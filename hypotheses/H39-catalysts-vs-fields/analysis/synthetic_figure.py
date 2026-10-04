"""Figure for the H39 synthetic validation: class recovery (Amendment A1 rule) and the transient fallacy.

Usage: uv run python hypotheses/H39-catalysts-vs-fields/analysis/synthetic_figure.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h39lib as L  # noqa: E402

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
KINDS = ["null", "field_half", "field_dest", "cat_uniform", "cat_edge", "escape"]
KLAB = ["null", "field (θ=½)", "field (dest.)", "catalyst (unif.)", "catalyst (edge)", "escape-only"]
CLS = ["neither", "field", "catalyst", "both"]


def recompute(p):
    if p.get("p_F") is None:
        return "n/a"
    f = p["p_F"] < 0.05 and p["phi_exc"] >= L.THR
    c = (p["K_ci"][0] > 0 or p["K_ci"][1] < 0) and abs(p["K"]) >= L.THR
    return L.classify(f, c)


def main():
    d = json.loads((L.OUT / "synthetic" / "synthetic_results.json").read_text())
    pts = d["point"]
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                         "ytick.color": INK2, "font.family": "DejaVu Sans"})
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.9), gridspec_kw=dict(width_ratios=[1, 1, 1.15]))
    for ax, size, title in ((axs[0], "large", "a  G51-like (≈500–1,500 kicks)"), (axs[1], "small", "   5-day period (≈30–100 kicks)")):
        M = np.zeros((len(KINDS), 4))
        for i, k in enumerate(KINDS):
            rr = [p for p in pts if p["kind"] == k and p["size"] == size]
            for p in rr:
                c = recompute(p)
                if c in CLS:
                    M[i, CLS.index(c)] += 1
            M[i] /= max(len(rr), 1)
        ax.imshow(M, cmap="Blues", vmin=0, vmax=1, aspect="auto")
        for i in range(len(KINDS)):
            for j in range(4):
                if M[i, j] > 0:
                    ax.text(j, i, f"{M[i, j]:.2f}".lstrip("0"), ha="center", va="center", fontsize=7,
                            color="white" if M[i, j] > 0.55 else INK)
        ax.set_xticks(range(4), CLS, rotation=30)
        ax.set_yticks(range(len(KINDS)), KLAB if size == "large" else [])
        ax.set_title(title, fontsize=8, color=INK, loc="left")
        ax.set_xlabel("recovered class")
        for s in ax.spines.values():
            s.set_visible(False)
    # transient fallacy: large runs, both variants
    ax = axs[2]
    y = np.arange(len(KINDS))
    st = [np.mean([p["dpi_idle"] for p in pts if p["kind"] == k and p["size"] == "large"]) for k in KINDS]
    tr = [np.mean([p["docc_idle"] for p in pts if p["kind"] == k and p["size"] == "large"]) for k in KINDS]
    ax.axvline(0, color=INK2, lw=0.8)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.scatter(st, y + 0.12, s=28, color=BLUE, zorder=3, edgecolor="white", lw=1.5, label="stationary Δπ_idle (field effect)")
    ax.scatter(tr, y - 0.12, s=28, color=ORANGE, zorder=3, edgecolor="white", lw=1.5, marker="s", label="transient Δocc_idle, 30-min window")
    ax.set_yticks(y, [])
    ax.set_ylim(len(KINDS) - 0.5, -0.5)
    ax.set_xlabel("idle share: kicked − control")
    ax.set_title("b  G51-like, rows as in a", fontsize=8, color=INK, loc="left")
    ax.legend(frameon=False, fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    out = L.HDIR / "figures" / "synthetic_validation.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    fig.savefig(out.with_suffix(".png"), dpi=150)
    print(out)


if __name__ == "__main__":
    main()
