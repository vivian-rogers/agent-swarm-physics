"""H145 round-1 figures: figures/r1_synth.pdf (synthetic size and power) and figures/r1_obs.pdf (real #51 results)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h145lib as L  # noqa: E402

FIG = L.CARD / "figures"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
PASS, FAIL, NEUT = "#1f8a3a", "#c0392b", "#9a9893"   # verdict colors: green / red / gray
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "font.family": "serif"})


def synth():
    s = json.loads((L.OUT / "synthetic/summary.json").read_text())
    worlds = ["W0", "W_field", "W_field_noisy", "W_prior", "W_hub", "W_sticky", "W_egr_0.2", "W_egr_0.4"]
    names = ["W0", "field", "field (noisy E)", "prior", "hub", "sticky", "egr ρ0.2", "egr ρ0.4"]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.7))
    y = np.arange(len(worlds))
    card = [s["disc"][w]["card_qual"] for w in worlds]
    a1 = [s["disc"][w]["A1_qual"] for w in worlds]
    ax[0].barh(y + 0.2, card, 0.38, color=NEUT, label="card rules")
    ax[0].barh(y - 0.2, a1, 0.38, color=S1, label="A1 rules")
    ax[0].set_yticks(y, names)
    ax[0].invert_yaxis()
    ax[0].set_xlabel("qualifying hub-free memeplexes per world")
    ax[0].legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2)
    ax[0].grid(axis="x", color=GRID, lw=0.5)
    ax[0].set_title("discovery (planted: 1 in field/hub/prior/sticky, 3 in egr)", fontsize=7.5, color=INK)

    def get(w, key):
        tgt = "discovered" if w in ("W_hub", "W_sticky") else "planted"
        d = s["tests"].get(f"{w}|{tgt}")
        return np.nan if d is None or d.get(key) is None else d[key]["rate"]
    tw = [w for w in worlds if w != "W0"]
    y2 = np.arange(len(tw))
    p2 = [get(w, "P2_D") for w in tw]
    p3 = [get(w, "P3_A") for w in tw]
    ax[1].barh(y2 + 0.2, p2, 0.38, color=S2, label="P2 D (A4)")
    ax[1].barh(y2 - 0.2, p3, 0.38, color=S3, label="P3a A z≥2 (A5)")
    ax[1].axvline(0.8, color=INK2, lw=0.8, ls="--")
    ax[1].axvline(0.1, color=INK2, lw=0.8, ls=":")
    ax[1].set_yticks(y2, [names[worlds.index(w)] + (" (end-to-end)" if w in ("W_hub", "W_sticky") else "") for w in tw])
    ax[1].invert_yaxis()
    ax[1].set_xlim(0, 1)
    ax[1].set_xlabel("pass rate (20 reps; 60 patterns in egr)")
    ax[1].legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2)
    ax[1].grid(axis="x", color=GRID, lw=0.5)
    ax[1].set_title("size (rivals) and power (egr); lines 0.1 and 0.8", fontsize=7.5, color=INK)
    fig.tight_layout()
    fig.savefig(FIG / "r1_synth.pdf")
    fig.savefig(FIG / "r1_synth.png", dpi=150)


def obs():
    t = json.loads((L.OUT / "results/tests.json").read_text())
    ms = t["memeplexes"]
    lab = [f"{m['id']} {m['candidate'][:10]}" for m in ms]
    d = [m["P2"]["D"]["obs"] - m["P2"]["D"]["thr"] for m in ms]
    az = [m["P3"]["A_z"] for m in ms]
    p2 = [m["P2"]["pass"] for m in ms]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8), sharey=True)
    y = np.arange(len(ms))
    ax[0].barh(y, d, 0.6, color=[PASS if p else NEUT for p in p2])
    ax[0].axvline(0, color=INK2, lw=0.8)
    ax[0].set_yticks(y, lab)
    ax[0].invert_yaxis()
    ax[0].set_xlabel("D_K(5) − pseudo-pattern 95th pct.")
    ax[0].set_title("P2: host renewal (green = pass)", fontsize=7.5, color=INK)
    ax[0].grid(axis="x", color=GRID, lw=0.5)
    col = [(PASS if (a >= 2 and p) else (FAIL if p else NEUT)) for a, p in zip(az, p2)]
    ax[1].scatter(az, y, s=18, color=col, zorder=3, edgecolor="white", linewidth=0.8)
    ax[1].axvline(2, color=INK2, lw=0.8, ls="--")
    ax[1].set_xlabel("colonial A excess z (2 h, E = e1–e4)")
    ax[1].set_title("P3a (green: P2 + z≥2; red: P2, z<2)", fontsize=7.5, color=INK)
    ax[1].grid(axis="x", color=GRID, lw=0.5)
    fig.tight_layout()
    fig.savefig(FIG / "r1_obs.pdf")
    fig.savefig(FIG / "r1_obs.png", dpi=150)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    synth()
    obs()
