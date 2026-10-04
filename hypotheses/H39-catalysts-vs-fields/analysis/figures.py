"""H39 figures from summary.json: the lever plane (summary_obs.pdf) and per-period forests (cross_period.pdf).

Usage: uv run python hypotheses/H39-catalysts-vs-fields/analysis/figures.py
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

BLUE, ORANGE, AQUA, YELLOW, MAGENTA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#4a3aa7"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
RNG = np.random.default_rng(1)


def style():
    plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                         "ytick.color": INK2, "font.family": "DejaVu Sans", "axes.titlesize": 8})


def kickoff_point(S):
    ks = [x for x in S["steps"]["list"] if x["cls"] == "kickoff" and "b4" in x]
    ph = np.array([x["b4"]["phi_exc"] for x in ks])
    kk = np.array([x["b4"]["K"] - 0.5 * (x["b4"]["K_p025"] + x["b4"]["K_p975"]) for x in ks])
    bo = [(ph[i].mean(), kk[i].mean()) for i in (RNG.integers(0, len(ks), len(ks)) for _ in range(2000))]
    bo = np.array(bo)
    return dict(phi=ph.mean(), phi_ci=np.percentile(bo[:, 0], [2.5, 97.5]), K=kk.mean(), K_ci=np.percentile(bo[:, 1], [2.5, 97.5]), n=len(ks))


def main():
    style()
    S = json.loads((L.OUT / "summary.json").read_text())
    C, E = S["classes"], S["erasure"]
    pts = []
    for key, lab, col in (("N_tgt", "nudge", BLUE), ("H_any", "human message", ORANGE), ("A_men", "@-mention", AQUA)):
        pb = C[key]["pooled_boot"]
        pts.append((lab, pb["K"], pb["K_ci"], pb["phi_exc"], pb["phi_exc_ci"], col))
    for key, lab, col in (("CF_b4_nocons", "forced erasure", VIOLET),):
        u = [x for x in E[key]["units"] if x["status"] == "ok"]
        # pooled as in pooled_boot: precision weights; CI from the meta for K and a unit bootstrap for phi_exc
        w = np.array([1 / max((x["K_ci"][1] - x["K_ci"][0]) / 3.92, 1e-3) ** 2 for x in u])
        K = float(E[key]["K_meta"]["est"])
        ph = np.array([x["phi_exc"] for x in u])
        bo = [np.sum(w[i] * ph[i]) / w[i].sum() for i in (RNG.integers(0, len(u), len(u)) for _ in range(2000))]
        pts.append((lab, K, E[key]["K_meta"]["ci"], float(np.sum(w * ph) / w.sum()), np.percentile(bo, [2.5, 97.5]), col))
    kp = kickoff_point(S)
    pts.append(("goal kickoff (behavior,\nvs day-boundary placebo)", kp["K"], kp["K_ci"], kp["phi"], kp["phi_ci"], YELLOW))

    fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw=dict(width_ratios=[1.05, 1]))
    ax = axs[0]
    ax.axvspan(-L.THR, L.THR, color=GRID, alpha=0.5, lw=0)
    ax.axhline(L.THR, color=INK2, lw=0.8, ls="--")
    for lab, K, Kci, ph, phci, col in pts:
        ax.errorbar(K, ph, xerr=[[K - Kci[0]], [Kci[1] - K]], yerr=[[ph - phci[0]], [phci[1] - ph]], fmt="o", ms=6,
                    color=col, mec="white", mew=1.2, elinewidth=1.4, capsize=0, zorder=3)
        off = {"human message": (-0.015, -0.035, "right"), "nudge": (0.012, 0.012, "left"), "@-mention": (0.012, 0.01, "left"),
               "forced erasure": (-0.012, 0.015, "right")}.get(lab, (0.02, 0.03, "left"))
        ax.annotate(lab, (K, ph), xytext=(K + off[0], ph + off[1]), fontsize=6.8, color=INK, ha=off[2])
    ax.text(0.0, 0.47, "neither", ha="center", fontsize=6.5, color=INK2)
    ax.text(0.27, 0.47, "catalyst →", ha="center", fontsize=6.5, color=INK2)
    ax.text(-0.27, 0.47, "← anti-catalyst", ha="center", fontsize=6.5, color=INK2)
    ax.text(0.33, L.THR + 0.012, "field above", ha="right", fontsize=6.5, color=INK2)
    ax.set_xlim(-0.35, 0.35)
    ax.set_ylim(0, 0.5)
    ax.set_xlabel("catalytic effect K (escape at fixed occupancy, ln ratio)")
    ax.set_ylabel("field effect φ_exc (RMS shift of ln occupancy)")
    ax.set_title("a  each lever's two components (pooled, 95% CI)", loc="left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    # ---- panel b: direction of the field
    ax = axs[1]
    rows = []
    g51 = json.loads((L.OUT / "G51" / "results.json").read_text())["b4"]["N_tgt"]
    rows.append(("nudge (G51)", g51["dpi"][:3], np.array(g51["dpi_ci"])[:, :3]))
    for key, lab in (("H_any", "human message,\nregime I periods"), ("A_men", "@-mention (pooled)")):
        if key == "H_any":
            us = [u for u in C[key]["units"] if u["status"] == "ok" and int(u["period"][1:]) < 33]
            w = np.array([1.0 for _ in us])
            d = np.array([u["dpi"][:3] for u in us])
            m = d.mean(0)
            bo = np.array([d[i].mean(0) for i in (RNG.integers(0, len(us), len(us)) for _ in range(2000))])
            rows.append((lab, m, np.percentile(bo, [2.5, 97.5], axis=0)))
        else:
            dm = C[key]["dpi_meta"][:3]
            rows.append((lab, [x["est"] for x in dm], np.array([x["ci"] for x in dm]).T))
    dm = E["CF_b4_nocons"]["dpi_meta"][:3]
    rows.append(("forced erasure\n(no-consolidate chain)", [x["est"] for x in dm], np.array([x["ci"] for x in dm]).T))
    y = np.arange(len(rows))
    ax.axvline(0, color=INK2, lw=0.8)
    ax.grid(axis="x", color=GRID, lw=0.6)
    for j, (nm, col, mk) in enumerate((("work", BLUE, "o"), ("chat", ORANGE, "s"), ("idle", AQUA, "D"))):
        off = (j - 1) * 0.22
        for i, (lab, m, ci) in enumerate(rows):
            ax.errorbar(m[j], i + off, xerr=[[m[j] - ci[0][j]], [ci[1][j] - m[j]]], fmt=mk, ms=4.5, color=col, mec="white",
                        mew=0.8, elinewidth=1.2, capsize=0, label=nm if i == 0 else None, zorder=3)
    ax.set_yticks(y, [r[0] for r in rows])
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.set_xlabel("Δπ: stationary share, lever − matched control")
    ax.set_title("b  where the field points", loc="left")
    ax.legend(frameon=False, fontsize=6.5, ncol=3, loc="upper center", bbox_to_anchor=(0.45, -0.2))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    out = L.HDIR / "figures" / "summary_obs.pdf"
    fig.savefig(out)
    fig.savefig(out.with_suffix(".png"), dpi=150)
    print(out)

    # ---------------- cross-period forest
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 5.2), sharey=False)
    for ax, (key, lab, col) in zip(axs, (("N_tgt", "nudges", BLUE), ("H_any", "human messages", ORANGE), ("A_men", "@-mentions", AQUA))):
        us = [u for u in C[key]["units"] if u["n_ep"] and u["n_ep"] >= 10 and u.get("K") is not None]
        yy = np.arange(len(us))
        for i, u in enumerate(us):
            filled = u["status"] == "ok"
            ax.errorbar(u["K"], i, xerr=[[u["K"] - u["K_ci"][0]], [u["K_ci"][1] - u["K"]]], fmt="o", ms=4,
                        color=col if filled else "white", mec=col, ecolor=col, elinewidth=1, capsize=0)
            ax.text(0.98, i, f"{u['n_ep']}", transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=5.5, color=INK2)
            if u["cls"] in ("field", "both"):
                ax.text(-0.98, i, "F", transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=5.5, color=INK)
        ax.axvline(0, color=INK2, lw=0.8)
        ax.axvspan(-L.THR, L.THR, color=GRID, alpha=0.5, lw=0)
        ax.set_yticks(yy, [u["period"] for u in us])
        ax.set_ylim(len(us) - 0.5, -0.5)
        ax.set_xlim(-0.7, 0.9)
        ax.set_title(f"{lab}", loc="left")
        ax.set_xlabel("K (open = < 20 episodes)")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.suptitle("Catalytic effect K per goal period (95% day-bootstrap CI)", fontsize=8, x=0.01, ha="left")
    fig.text(0.01, 0.005, "Right margin: episodes. 'F' (left margin): field effect in that period (placebo p < 0.05 and φ_exc ≥ 0.10). Grey band: |K| < 0.10.",
             fontsize=6, color=INK2)
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    out = L.HDIR / "figures" / "cross_period.pdf"
    fig.savefig(out)
    fig.savefig(out.with_suffix(".png"), dpi=130)
    print(out)


if __name__ == "__main__":
    main()
