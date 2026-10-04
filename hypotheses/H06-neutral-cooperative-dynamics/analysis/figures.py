"""H06 round-1 figures (reads data/processed/H06-neutral-cooperative-dynamics/*/round1_*.json and synthetic/).

  figures/synthetic_validation.pdf   P1-rule outcome rates by true model, mu and sampling (axis F)
  figures/llr_by_period.pdf          LLR(NCD - Hubbell) and LLR(NCD - conformist) per period and label set
  figures/lambda_copy_by_period.pdf  observed Simpson lambda, singleton fraction and copy-consistency vs predictions
  figures/pn_residence_free.pdf      P_n (observed vs model means) and residence vs max abundance, free weeks
  goalperiod-subhypotheses/<G>/figures/pn_<scope>.pdf   per-period P_n + scatter
Usage: uv run python hypotheses/H06-neutral-cooperative-dynamics/analysis/figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H06-neutral-cooperative-dynamics"
FIG = HYP / "figures"
SUB = HYP / "goalperiod-subhypotheses"
DATA = ROOT / "data/processed/H06-neutral-cooperative-dynamics"
COL = {"ncd": "#2a78d6", "hubbell": "#85847e", "conformist": "#d03b3b"}
LAB = {"ncd": "NCD (cooperative)", "hubbell": "Hubbell (neutral)", "conformist": "conformist (herding)"}
ORDER = ["G11", "G16", "G31", "G37", "G44", "G19", "G25", "G30", "G38", "G51a", "G51b", "G51c"]
ROLE = {"G11": "free", "G16": "free", "G31": "free", "G37": "free", "G44": "free", "G19": "shared", "G25": "shared",
        "G30": "shared", "G38": "shared", "G51a": "#51", "G51b": "#51", "G51c": "#51"}
CLUST = ["km8", "km24", "km64", "wd8", "wd24", "wd64"]
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 8.5})


def load(scope):
    folder = "G51" if scope.startswith(("G51", "NE33")) else scope
    p = DATA / folder / f"round1_{scope}.json"
    return json.loads(p.read_text()) if p.exists() else None


def name(s):
    return "#" + s[1:]


def fig_synthetic():
    p = DATA / "synthetic/p1_rule_rates.parquet"
    if not p.exists():
        return
    t = pl.read_parquet(p)
    cfgs = [("N7_D5W6_p85", "N = 7 (#11, #16)"), ("N13_D5W8_p85", "N = 13, p = 0.85 (#31 int)"),
            ("N13_D5W8_p50", "N = 13, p = 0.5 (#31 art)"), ("N12_D3W8_p85", "N = 12, 3 days (#37, #44)")]
    fig, axes = plt.subplots(1, 4, figsize=(7.4, 2.3), sharey=True)
    for ax, (c, title) in zip(axes, cfgs):
        x = 0
        ticks, tl = [], []
        for mu in ("0.01", "0.05", "0.2"):
            for tr in ("ncd", "hubbell", "conformist"):
                r = t.filter((pl.col("config") == f"{c}_mu{mu}") & (pl.col("truth") == tr))
                if r.height == 0:
                    continue
                s, f = r["supported"][0], r["failed"][0]
                ax.bar(x, s, color="#0ca30c", width=0.8)
                ax.bar(x, 1 - s - f, bottom=s, color="#ecebe6", width=0.8)
                ax.bar(x, f, bottom=1 - f, color="#d03b3b", width=0.8)
                ticks.append(x)
                tl.append({"ncd": "N", "hubbell": "H", "conformist": "C"}[tr])
                x += 1
            ax.text(x - 2, -0.2, f"μ = {mu}", ha="center", va="top", fontsize=6.5, transform=ax.get_xaxis_transform())
            x += 0.6
        ax.set_xticks(ticks)
        ax.set_xticklabels(tl, fontsize=5.5)
        ax.tick_params(axis="x", pad=1.5, length=0)
        ax.set_title(title, fontsize=7)
        ax.set_ylim(0, 1)
    axes[0].set_ylabel("share of synthetic datasets")
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color="#0ca30c", label="P1 supported"), Patch(color="#ecebe6", label="mixed"),
                        Patch(color="#d03b3b", label="P1 failed")], loc="upper center", ncol=3, frameon=False, fontsize=7,
               bbox_to_anchor=(0.5, 1.04))
    fig.text(0.5, -0.04, "true model: N = NCD, H = Hubbell, C = conformist (60 datasets each)", ha="center", fontsize=6.5)
    fig.tight_layout(rect=(0, 0.04, 1, 0.93))
    fig.savefig(FIG / "synthetic_validation.pdf", bbox_inches="tight")
    plt.close(fig)


def fig_llr():
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 3.6), sharex=True)
    for ax, key, lab in ((axes[0], "LLR_NH", "LLR NCD − Hubbell"), (axes[1], "LLR_NC", "LLR NCD − conformist")):
        for i, s in enumerate(ORDER):
            r = load(s)
            if not r:
                continue
            for k in CLUST:
                v = r["sets"].get(k, {})
                if v.get("testable"):
                    y = np.clip(v[key], -40, 40)
                    ax.plot(i + (CLUST.index(k) - 2.5) * 0.06, y, "o", ms=3.2 if k != "km24" else 5,
                            color="#2a78d6" if k == "km24" else "#9ec5f4", zorder=3, mec="none")
            for k, mk in (("art", "D"), ("art_nocarry", "d")):
                v = r["sets"].get(k, {})
                if v.get("testable"):
                    ax.plot(i + 0.25, np.clip(v[key], -40, 40), mk, ms=4, color="#fab219" if k == "art" else "#c9a227", zorder=3)
        ax.axhspan(-2, 2, color="#ecebe6", zorder=0)
        ax.axhline(0, color="#85847e", lw=0.6)
        ax.set_ylabel(lab)
        ax.set_ylim(-42, 42)
    axes[1].set_xticks(range(len(ORDER)))
    axes[1].set_xticklabels([name(s) + "\n" + ROLE[s] for s in ORDER], fontsize=6.5)
    for x in (4.5, 8.5):
        for ax in axes:
            ax.axvline(x, color="#c9c7c0", lw=0.6)
    from matplotlib.lines import Line2D
    axes[0].legend(handles=[Line2D([], [], marker="o", ls="", color="#2a78d6", label="intention km24 (primary)"),
                            Line2D([], [], marker="o", ls="", color="#9ec5f4", ms=3.2, label="other 5 clusterings"),
                            Line2D([], [], marker="D", ls="", color="#fab219", label="artifact labels"),
                            Line2D([], [], marker="d", ls="", color="#c9a227", label="artifact, no carry")],
                   ncol=4, fontsize=6.5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.22))
    fig.tight_layout()
    fig.savefig(FIG / "llr_by_period.pdf", bbox_inches="tight")
    plt.close(fig)


def fig_lambda_copy():
    stats = [("lam", "Simpson λ̄"), ("single", "singleton fraction"), ("beta", "frequency dependence β̂"), ("copyfrac", "copy-consistency")]
    fig, axes = plt.subplots(len(stats), 1, figsize=(7.4, 6.0), sharex=True)
    for ax, (st, lab) in zip(axes, stats):
        for i, s in enumerate(ORDER):
            r = load(s)
            if not r:
                continue
            v = r["sets"].get("km24", {})
            if not v.get("testable"):
                continue
            for j, m in enumerate(("ncd", "hubbell", "conformist")):
                pr = v["fits"][m]["pred"][st]
                ax.plot([i - 0.2 + j * 0.13] * 2, [pr[1], pr[2]], color=COL[m], lw=2.2, alpha=0.75, solid_capstyle="butt")
            obs = v["copyfrac"] if st == "copyfrac" else v["obs"][st]
            ax.plot(i + 0.22, obs, "k*", ms=6, zorder=4)
            if st == "lam" and v.get("null_ind"):
                ax.plot(i + 0.22, v["null_ind"]["lam_mean"], "x", color="#52514e", ms=4, zorder=4)
            if st == "copyfrac" and v.get("null_ind"):
                ax.plot(i + 0.22, v["null_ind"]["copy_mean"], "x", color="#52514e", ms=4, zorder=4)
        ax.set_ylabel(lab, fontsize=7)
        for x in (4.5, 8.5):
            ax.axvline(x, color="#c9c7c0", lw=0.6)
    axes[-1].set_xticks(range(len(ORDER)))
    axes[-1].set_xticklabels([name(s) + "\n" + ROLE[s] for s in ORDER], fontsize=6.5)
    from matplotlib.lines import Line2D
    axes[0].legend(handles=[Line2D([], [], color=COL[m], lw=2.2, label=LAB[m] + " 95%") for m in COL] +
                   [Line2D([], [], marker="*", ls="", color="k", label="observed (km24)"),
                    Line2D([], [], marker="x", ls="", color="#52514e", label="independent-agents null (mean)")],
                   ncol=3, fontsize=6.3, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.45))
    fig.tight_layout()
    fig.savefig(FIG / "lambda_copy_by_period.pdf", bbox_inches="tight")
    plt.close(fig)


def pn_panel(ax_pn, ax_sc, v, title):
    h = np.array(v["hist"])
    n = np.arange(len(h))
    tot = h[1:].sum()
    ax_pn.bar(n[1:], h[1:] / tot, color="#c9c7c0", width=0.8, label="observed")
    for m in ("ncd", "hubbell", "conformist"):
        hm = np.array(v["fits"][m]["hist_mean"])
        ax_pn.plot(n[1:], hm[1:] / max(hm[1:].sum(), 1e-9), "-o", ms=2, lw=1, color=COL[m], label=m)
    ax_pn.set_yscale("log")
    ax_pn.set_title(title, fontsize=7.5)
    ax_pn.set_xlabel("abundance n (agents per project)", fontsize=6.5)
    rm = np.array([[a, b] for a, b, _ in v["res_max"]], dtype=float)
    if len(rm):
        jit = np.random.default_rng(0).uniform(-0.15, 0.15, rm.shape)
        ax_sc.scatter(rm[:, 0] + jit[:, 0], rm[:, 1] + jit[:, 1], s=5, color="#2a78d6", alpha=0.6, lw=0)
        ax_sc.set_xscale("log")
    ax_sc.set_xlabel("residence (windows)", fontsize=6.5)


def fig_pn():
    free = ["G11", "G16", "G31", "G37", "G44"]
    fig, axes = plt.subplots(2, 5, figsize=(7.6, 3.4))
    for j, s in enumerate(free):
        r = load(s)
        if not r or not r["sets"].get("km24", {}).get("testable"):
            continue
        pn_panel(axes[0, j], axes[1, j], r["sets"]["km24"], name(s))
    axes[0, 0].set_ylabel("P_n (share of project-windows)", fontsize=6.5)
    axes[1, 0].set_ylabel("max abundance", fontsize=6.5)
    axes[0, -1].legend(fontsize=5.5, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "pn_residence_free.pdf", bbox_inches="tight")
    plt.close(fig)
    for s in ORDER:
        r = load(s)
        if not r:
            continue
        sets = [k for k in ("km24", "art") if r["sets"].get(k, {}).get("testable")]
        if not sets:
            continue
        fig, axes = plt.subplots(2, len(sets), figsize=(3.2 * len(sets), 3.6), squeeze=False)
        for j, k in enumerate(sets):
            pn_panel(axes[0, j], axes[1, j], r["sets"][k], f"{name(s)} · {k}")
        axes[0, 0].legend(fontsize=5.5, frameon=False)
        fig.tight_layout()
        folder = SUB / ("G51" if s.startswith("G51") else s) / "figures"
        folder.mkdir(parents=True, exist_ok=True)
        fig.savefig(folder / f"pn_{s}.pdf", bbox_inches="tight")
        plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    fig_synthetic()
    fig_llr()
    fig_lambda_copy()
    fig_pn()
    print("figures written")


if __name__ == "__main__":
    main()
