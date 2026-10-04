"""Synthetic-validation figure: agent-level RR_timely and receptive interaction by world, shared-field diagnostics,
and decision-rule-v2 labels."""
from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from h53core import OUT  # noqa: E402
from pathlib import Path  # noqa: E402

FIG = Path(__file__).resolve().parents[1] / "figures"
SYN = OUT / "synthetic"
WORLDS = ["W0", "WF0", "WFpre", "WS", "WN2", "WN4"]
NAMES = {"W0": "activity\nnull", "WF0": "field at\nseed", "WFpre": "field\nbefore", "WS": "poster\nstatus", "WN2": "receptive\n×2", "WN4": "receptive\n×4"}
C1, C2, C3, C4, GR = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#85847e"
LABC = {"nucleation": C1, "read-out (no timing)": "#9fc3ee", "status": C2, "field": GR, "seed-locked field": "#c9c7c0", "null": "#e7e5df"}
plt.rcParams.update({"font.size": 7.5, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#52514e",
                     "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e", "ytick.color": "#52514e", "axes.linewidth": 0.6})


def load():
    return json.loads((SYN / "synthetic_results.json").read_text())["results"]


def panel_rr(ax, res, key="agent", var="x_timely", title="(a) read-out timing effect, RR$_{\\rm timely}$"):
    for j, w in enumerate(WORLDS):
        for t, mk, col in ((0.3, "o", "#9fc3ee"), (1.0, "o", C1)):
            v = [r[key].get(var, {}).get("rr", np.nan) for r in res if r["world"] == w and r["target"] == t]
            x = j + (-0.15 if t == 0.3 else 0.15) + np.random.default_rng(j).uniform(-0.05, 0.05, len(v))
            ax.scatter(x, v, s=6, color=col, lw=0, zorder=3, label=f"mean wave {t}" if j == 0 else None)
    ax.axhline(1, color=GR, lw=0.6, zorder=1)
    ax.axhline(1.5, color=C2, lw=0.6, ls="--", zorder=1)
    ax.text(-0.4, 1.52, "1.5 (P1 bar)" if var == "x_timely" else "1.5", color="#52514e", ha="left", va="bottom", fontsize=6.5)
    ax.set_xticks(range(len(WORLDS))); ax.set_xticklabels([NAMES[w] for w in WORLDS], fontsize=6.5)
    ax.set_title(title, loc="left", fontsize=7.5)
    ax.grid(axis="y", color="#e7e5df", lw=0.5)
    ax.legend(frameon=False, fontsize=6.5, loc="upper center", handletextpad=0.2)


def panel_labels(ax, res):
    order = ["nucleation", "read-out (no timing)", "status", "seed-locked field", "field", "null"]
    for j, w in enumerate(WORLDS):
        for t, xo in ((0.3, -0.18), (1.0, 0.18)):
            labs = [r["label_v2"] for r in res if r["world"] == w and r["target"] == t]
            b = 0
            for lab in order:
                n = labs.count(lab)
                if n:
                    ax.bar(j + xo, n, bottom=b, width=0.32, color=LABC[lab], edgecolor="#fcfcfb", lw=0.6)
                    b += n
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=LABC[lab], label=lab) for lab in order]
    ax.set_xticks(range(len(WORLDS))); ax.set_xticklabels([NAMES[w] for w in WORLDS], fontsize=6.5)
    ax.set_ylabel("runs (of 20)")
    ax.set_title("(b) decision rule v2 (left bar: mean wave 0.3, right: 1.0)", loc="left", fontsize=7.5)
    ax.legend(handles=handles, frameon=False, fontsize=6, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.28))


def panel_field(ax, res):
    for j, w in enumerate(WORLDS):
        f1 = [r["field"]["F1"]["ratio"] for r in res if r["world"] == w]
        f1 = [min(x, 40) if x is not None else np.nan for x in f1]
        f4 = [r["field"]["F4"].get("ratio", np.nan) or np.nan for r in res if r["world"] == w]
        ax.scatter(j - 0.15 + np.zeros(len(f1)), f1, s=6, color=C1, lw=0, label="F1 step (post/pre 30 min)" if j == 0 else None)
        ax.scatter(j + 0.15 + np.zeros(len(f4)), f4, s=6, color=C3, lw=0, label="F4 read-locking" if j == 0 else None)
    ax.set_yscale("log")
    ax.axhline(3, color=C1, lw=0.5, ls="--"); ax.axhline(2, color=C3, lw=0.5, ls=":")
    ax.set_xticks(range(len(WORLDS))); ax.set_xticklabels([NAMES[w] for w in WORLDS], fontsize=6.5)
    ax.set_title("(c) shared-field diagnostics (F1 capped at 40)", loc="left", fontsize=7.5)
    ax.legend(frameon=False, fontsize=6.5, loc="upper left")


def main():
    res = load()
    FIG.mkdir(exist_ok=True)
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 4.6))
    panel_rr(axs[0, 0], res)
    panel_rr(axs[0, 1], res, key="agent_int", var="x_recept", title="(b) receptive interaction RR (timely × uncommitted)")
    panel_field(axs[1, 0], res)
    panel_labels(axs[1, 1], res)
    axs[1, 1].set_title("(d) decision rule v2 (left bar: wave 0.3, right: 1.0)", loc="left", fontsize=7.5)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic_validation.pdf"); fig.savefig(FIG / "synthetic_validation.png", dpi=160)
    # compact 2-panel version for the summary page 2
    fig, axs = plt.subplots(1, 2, figsize=(3.4, 1.95), gridspec_kw=dict(width_ratios=[1, 1]))
    for ax in axs:
        ax.tick_params(labelsize=5.5)
    panel_rr(axs[0], res, title="(a) RR$_{\\rm timely}$ per run")
    axs[0].set_xticklabels([NAMES[w].replace("\n", " ").replace("receptive ", "rec") .replace("activity null", "null").replace("field at seed", "F-seed")
                            .replace("field before", "F-pre").replace("poster status", "status") for w in WORLDS], fontsize=5, rotation=40, ha="right")
    axs[0].legend(frameon=False, fontsize=5, loc="upper left", handletextpad=0.1, markerscale=0.8)
    for t in axs[0].texts:
        t.set_fontsize(5)
    panel_labels(axs[1], res)
    axs[1].set_title("(b) rule-v2 labels", loc="left", fontsize=6.5)
    axs[0].set_title("(a) RR$_{\\rm timely}$ per run", loc="left", fontsize=6.5)
    axs[1].set_xticklabels([NAMES[w].replace("\n", " ").replace("receptive ", "rec").replace("activity null", "null").replace("field at seed", "F-seed")
                            .replace("field before", "F-pre").replace("poster status", "status") for w in WORLDS], fontsize=5, rotation=40, ha="right")
    axs[1].set_ylabel("runs", fontsize=5.5)
    from matplotlib.patches import Patch
    axs[1].legend(handles=[Patch(facecolor=LABC[l], label=l) for l in ["nucleation", "read-out (no timing)", "status", "seed-locked field", "field"]],
                  frameon=False, fontsize=4.5, ncol=2, loc="upper center", bbox_to_anchor=(0.45, 1.02), handlelength=0.8, columnspacing=0.5)
    axs[1].set_ylim(0, 34)
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "summary_synth.pdf")
    print("written", FIG)


if __name__ == "__main__":
    main()
