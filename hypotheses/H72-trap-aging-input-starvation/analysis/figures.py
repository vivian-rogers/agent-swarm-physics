"""H72 figures: figures/summary_obs.pdf (clock slopes per period) and figures/synthetic_validation.pdf."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h72lib as L  # noqa: E402

FIG = Path(__file__).resolve().parents[1] / "figures"
C_A0, C_A, C_S = "#7f7f7f", "#d0632b", "#2a78d6"


def load():
    out = []
    for d in sorted(L.OUT.glob("G*/results.json")):
        r = json.loads(d.read_text())
        if "beta_a0" in r["primary"] and r["primary"]["n"] >= 500:
            out.append(r)
    return out


def summary_obs():
    rs = load()
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [1.6, 1]})
    y = np.arange(len(rs))
    labs = [f"{r['period']} ({r['regime']})" for r in rs]
    for k, (key, ci, col, nm, off) in enumerate((("beta_a0", "ci_a0", C_A0, r"$\beta_{a0}$ (age only)", -0.22),
                                                   ("beta_a", "ci_a", C_A, r"$\beta_a$ (age | $s$)", 0.0),
                                                   ("beta_s", "ci_s", C_S, r"$\beta_s$ (starvation | $a$)", 0.22))):
        v = np.array([r["primary"][key] for r in rs])
        lo = np.array([r["primary"][ci][0] for r in rs])
        hi = np.array([r["primary"][ci][1] for r in rs])
        ax[0].errorbar(np.clip(v, -2.5, 2.5), y + off, xerr=[np.clip(v - lo, 0, 3), np.clip(hi - v, 0, 3)], fmt="o",
                       ms=3, color=col, lw=0.8, label=nm)
    ax[0].axvline(0, color="k", lw=0.5)
    ax[0].set_yticks(y, labs, fontsize=6.5)
    ax[0].set_xlim(-2.5, 2.5)
    ax[0].set_xlabel("slope per ln-minute (logit, agent FE)", fontsize=7)
    ax[0].legend(fontsize=6, loc="lower right", frameon=False)
    ax[0].set_title("(a) clock slopes, periods with ≥ 500 gates", fontsize=7.5)
    ax[0].tick_params(labelsize=6.5)
    # (b) G51 by s variant
    g51 = json.loads((L.OUT / "G51/results.json").read_text())
    rows = [("novel", g51["primary"])] + [(k, v) for k, v in g51["variants"].items()]
    if "any" in g51:
        rows.append(("novel, any esc.", g51["any"]))
    yy = np.arange(len(rows))
    for i, (nm, r) in enumerate(rows):
        ax[1].errorbar(r["beta_a"], i - 0.12, xerr=[[r["beta_a"] - r["ci_a"][0]], [r["ci_a"][1] - r["beta_a"]]], fmt="o",
                       ms=3, color=C_A, lw=0.8)
        ax[1].errorbar(r["beta_s"], i + 0.12, xerr=[[r["beta_s"] - r["ci_s"][0]], [r["ci_s"][1] - r["beta_s"]]], fmt="s",
                       ms=3, color=C_S, lw=0.8)
        ax[1].plot([r["beta_a0"]], [i - 0.12], "|", color=C_A0, ms=7)
    ax[1].axvline(0, color="k", lw=0.5)
    ax[1].set_yticks(yy, [r[0] for r in rows], fontsize=6.5)
    ax[1].set_title("(b) G51 by input variant", fontsize=7.5)
    ax[1].set_xlabel(r"$\beta_a$ (orange), $\beta_s$ (blue); | = $\beta_{a0}$", fontsize=7)
    ax[1].tick_params(labelsize=6.5)
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "summary_obs.pdf")


def synthetic():
    s = json.loads((L.OUT / "synthetic/synthetic_results.json").read_text())
    worlds = ["aging", "starve", "both", "null"]
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.6))
    for j, per in enumerate(("51", "38", "18")):
        for i, w in enumerate(worlds):
            r = s[per][w]
            x = i + (j - 1) * 0.22
            ax[0].errorbar(x, r["mean_beta_a"], yerr=r["sd_beta_a"], fmt="o", ms=3, color=C_A, alpha=1 - 0.25 * j)
            ax[0].errorbar(x + 0.08, r["mean_beta_s"], yerr=r["sd_beta_s"], fmt="s", ms=3, color=C_S, alpha=1 - 0.25 * j)
            ax[0].plot([x - 0.08, x + 0.16], [r["truth"][0]] * 2, color=C_A, lw=0.6)
            ax[0].plot([x - 0.08, x + 0.16], [r["truth"][1]] * 2, color=C_S, lw=0.6, ls=":")
    ax[0].set_xticks(range(4), worlds, fontsize=7)
    ax[0].set_ylabel("recovered slope (mean ± SD)", fontsize=7)
    ax[0].set_title("(a) recovery on G51, G38, G18 designs", fontsize=7.5)
    ax[0].tick_params(labelsize=6.5)
    cats = ["supported", "supported (starvation without aging)", "failed", "mixed", "descriptive (no aging to explain)"]
    cols = ["#0ca30c", "#7ccf7c", "#d03b3b", "#fab219", "#86b6ef"]
    xt = []
    k = 0
    for w in worlds:
        for per in ("51", "38", "18"):
            v = s[per][w]["verdicts"]
            b = 0
            for c, cc in zip(cats, cols):
                ax[1].bar(k, v.get(c, 0), bottom=b, color=cc, width=0.8, label=c if k == 0 else None)
                b += v.get(c, 0)
            xt.append(f"{w}\nG{per}")
            k += 1
    ax[1].set_xticks(range(k), xt, fontsize=5)
    ax[1].set_ylabel("share of replicates", fontsize=7)
    ax[1].set_title("(b) verdict rule by planted world", fontsize=7.5)
    ax[1].legend(fontsize=5, loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=3, frameon=False)
    ax[1].tick_params(labelsize=6)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic_validation.pdf")


if __name__ == "__main__":
    summary_obs()
    synthetic()
