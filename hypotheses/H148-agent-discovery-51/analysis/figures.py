"""H148 round-1 figures.
  figures/synthetic.pdf   synthetic validation on the #51 skeleton: size and recovery per world and setting
  figures/g51.pdf         #51: single-atom individuality per agent, and the discovered systems (written after the run)
Run: uv run python hypotheses/H148-agent-discovery-51/analysis/figures.py [--real]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h148lib as L  # noqa: E402

FIG = HERE.parent / "figures"
RED, GRAY, GREEN, BLUE = "#b2182b", "#7f7f7f", "#1a9850", "#2166ac"


def synthetic():
    S = json.loads((L.OUT / "synthetic" / "summary.json").read_text())
    rows = []
    for f, ws in S.items():
        tag = f.replace("synthetic_w30_", "")
        if "za2.5" in tag:          # stopped variant (5 replicates), not used
            continue
        for w, d in ws.items():
            rows.append((tag, w, d))
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
    labs = []
    for i, (tag, w, d) in enumerate(rows):
        short = {"el0": "agents", "el0_rho0.9": "agents ρ.9", "el140_elonly": "elements",
                 "el140_elonly_d": "elements"}.get(tag, tag)
        lab = f"{w.replace('W_', '')}\n{short}\nn={d['n_reps']}"
        labs.append(lab)
        k, n = d["worlds_with_false_multi"], d["n_reps"]
        lo, hi = d["worlds_with_false_multi_ci"]
        ax[0].errorbar(i, k / n, yerr=[[k / n - max(lo, 0)], [hi - k / n]], fmt="o", color=RED, ms=4)
        if "rec_pair" in d:
            lo, hi = d["rec_pair_ci"]
            ax[1].errorbar(i - 0.1, d["rec_pair"], yerr=[[d["rec_pair"] - max(lo, 0)], [hi - d["rec_pair"]]],
                           fmt="s", color=BLUE, ms=4, label="planted pair (both directions)" if i == 0 or
                           "rec" not in str(labs[:-1]) else None)
        ax[1].plot(i, d.get("p1_share", np.nan), "^", color=GREEN, ms=4)
        ax[1].plot(i + 0.1, d.get("p2_share", np.nan), "x", color=GRAY, ms=5)
    for a in ax:
        a.set_xticks(range(len(labs)), labs, fontsize=6)
        a.set_ylim(-0.02, 1.02)
    ax[0].axhline(0.05, color="k", lw=0.6, ls="--")
    ax[0].set_ylabel("worlds with a false\nmulti-atom discovery", fontsize=8)
    ax[0].set_title("(a) size (Wilson 95% CI)", fontsize=9)
    ax[1].axhline(0.8, color="k", lw=0.6, ls="--")
    ax[1].set_ylabel("recovery", fontsize=8)
    ax[1].set_title("(b) recovery", fontsize=9)
    ax[1].text(0.02, 0.5, "blue: planted pair, both directions\ngreen: P1 share (all agents planted)\n"
               "gray: P2 own-repo closure", transform=ax[1].transAxes, fontsize=6, va="center")
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "synthetic.pdf")
    print("wrote", FIG / "synthetic.pdf")


def real(level: str = "agents"):
    R = json.loads((L.OUT / "results" / f"{level}_w30.json").read_text())
    sg = [r for r in R["singles"] if r["kind"] == "agent"]
    sg = [r for r in sg if np.isfinite(r["z_h0"] if r["z_h0"] is not None else np.nan)]   # agents with >= 40 transitions
    sg.sort(key=lambda r: -(np.nan_to_num(r["z_h0"]) + np.nan_to_num(r["z_h1"])))
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [1.4, 1]})
    x = np.arange(len(sg))
    col = [GREEN if r["individual"] else GRAY for r in sg]
    ax[0].scatter(x - 0.15, [r["z_h0"] for r in sg], c=col, marker="o", s=10, label="odd days")
    ax[0].scatter(x + 0.15, [r["z_h1"] for r in sg], c=col, marker="s", s=10, label="even days")
    ax[0].axhline(2, color="k", lw=0.6, ls="--")
    ax[0].set_xticks(x, [r["name"][:14] for r in sg], rotation=90, fontsize=5)
    ax[0].set_ylabel("single-atom z (colonial A vs permutation)", fontsize=7)
    ax[0].set_title("(a) agents as single-atom individuals (green: both halves p ≤ 0.025)", fontsize=7)
    ax[0].legend(fontsize=6)
    ax[1].axis("off")
    lines = []
    for lv, lab in (("agents", "agent level (32 agents, 33 repos, 2 rooms)"), ("elements", "element level (140 elements)")):
        f = L.OUT / "results" / f"{lv}_w30.json"
        if not f.exists():
            continue
        Rv = json.loads(f.read_text())
        p7 = Rv["predictions"]["P7"]
        lines += [lab,
                  f"  discovered (both directions): {len(Rv['discovered'])}",
                  f"  local maxima: real {p7['real_local_maxima']}, rotated {p7['rotated_local_maxima_mean']:.1f}",
                  f"  held out of sample: real {p7['real_held_maxima']}, rotated {p7['rotated_held_maxima_mean']:.1f}",
                  ""]
        for d in Rv["discovered"]:
            lines.append("  " + d["scale"] + ": " + " + ".join(n[:16] for n in d["names"]))
    ax[1].text(0, 1, "\n".join(lines), va="top", fontsize=6, family="monospace")
    ax[1].set_title("(b) the search on #51 (30-min bins)", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "g51.pdf")
    print("wrote", FIG / "g51.pdf")


if __name__ == "__main__":
    synthetic()
    if "--real" in sys.argv:
        real("agents")
