"""H22 cross-unit synthesis: random-effects summaries over counted #51 units, pair listings (no text), summary_obs figure.

Usage: uv run python hypotheses/H22-private-goals-spin-glass/analysis/summarize.py
Writes data/processed/H22-private-goals-spin-glass/summary.json and figures/summary_obs.pdf.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h22lib as L  # noqa: E402
import role_relations as RR  # noqa: E402
from figures import BLUE, ORANGE, AQUA, VIOLET, NULL, INK2, GRID, DATA, FIG, PERIOD, g, plt  # noqa: E402

COUNTED = ["51b", "51c", "51d"]


def main():
    R = {u: json.loads((DATA / PERIOD[u] / u / "results.json").read_text()) for u in PERIOD if (DATA / PERIOD[u] / u / "results.json").exists()}
    out = {"meta": {}, "pairs": {}}
    for cls in ("SR", "OP", "K", "SY", "NC"):
        est = [g(R[u], "content", "treatment", "family_adjusted", cls, "T") for u in COUNTED]
        se = [g(R[u], "content", "treatment", "family_adjusted", cls, "null_sd") for u in COUNTED]
        out["meta"][f"T_{cls}_content"] = {**L.dl_meta(est, se), "per_unit": dict(zip(COUNTED, est))}
        est = [g(R[u], "talk", "treatment", "family_adjusted", cls, "T") for u in COUNTED]
        se = [g(R[u], "talk", "treatment", "family_adjusted", cls, "null_sd") for u in COUNTED]
        out["meta"][f"T_{cls}_talk"] = {**L.dl_meta(est, se), "per_unit": dict(zip(COUNTED, est))}
    for key in ("tau3", "tau3_dc", "kappa", "rho_split"):
        est = [g(R[u], "content", "moments", key) for u in COUNTED]
        ci = [g(R[u], "content", "moments", key + "_ci90", default=[np.nan, np.nan]) for u in COUNTED]
        se = [(c[1] - c[0]) / (2 * 1.645) for c in ci]  # CI-based SE (bootstrap SDs are heavy-tailed for ratios)
        out["meta"][key] = {**L.dl_meta(est, se), "per_unit": dict(zip(COUNTED, est))}
    for key in ("W", "M", "q_inf", "q_self", "q_lag1"):
        out["meta"]["overlap_" + key] = {u: g(R[u], "overlap", key) for u in COUNTED}
    # same-role / opposed pairs that enter the pairwise test (model names only)
    ro = pl.read_parquet(DATA.parents[0] / "shared/roster.parquet")
    name = dict(zip(ro["agent"].to_list(), ro["name"].to_list()))
    for u in ("51a", "51b", "51c", "51d"):
        m = np.load(DATA / "G51" / u / "matrices.npz")
        ag = pl.read_parquet(DATA / "G51" / u / "agents.parquet")
        role = dict(zip(ag["agent"].to_list(), ag["role"].to_list()))
        J, codes = m["Jc_pair"], m["Jc_pair_agents"]
        rows = []
        for i in range(len(codes)):
            for j in range(i + 1, len(codes)):
                c = RR.pair_class(role.get(int(codes[i])), role.get(int(codes[j])))
                if c in (1, 2):
                    rows.append({"class": RR.CLASS_NAMES[c], "a": name[int(codes[i])], "b": name[int(codes[j])],
                                 "role_a": role.get(int(codes[i])), "role_b": role.get(int(codes[j])),
                                 "J": None if not np.isfinite(J[i, j]) else float(J[i, j])})
        v = L.triu_vals(J); v = v[np.isfinite(v)]
        out["pairs"][u] = {"listed": rows, "all_pairs_mean": float(v.mean()), "all_pairs_q": [float(np.quantile(v, q)) for q in (0.1, 0.5, 0.9)],
                           "frac_negative": float(np.mean(v < 0)), "n_pairs": int(len(v))}
    (DATA / "summary.json").write_text(json.dumps(out, indent=1, default=float))
    figure(R, out)
    print(json.dumps(out["meta"], indent=1, default=float)[:3000])
    print(json.dumps(out["pairs"], indent=1)[:4000])


def figure(R, out):
    syn = json.loads((DATA / "synthetic/results.json").read_text())
    fig, axs = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [1.25, 1]})
    ax = axs[0]
    for k, u in enumerate(COUNTED):
        m = np.load(DATA / "G51" / u / "matrices.npz")
        v = L.triu_vals(m["Jc_pair"]); v = v[np.isfinite(v)]
        y = k + (np.random.default_rng(k).random(len(v)) - 0.5) * 0.5
        ax.scatter(v, y, s=3, color=NULL, alpha=0.5, lw=0)
        for p in out["pairs"][u]["listed"]:
            if p["J"] is not None:
                ax.scatter(p["J"], k, s=22, marker="D" if p["class"] == "SR" else "v",
                           color=BLUE if p["class"] == "SR" else ORANGE, edgecolor="white", lw=0.6, zorder=3)
    ax.axvline(0, color=INK2, lw=0.6)
    ax.set_yticks(range(len(COUNTED))); ax.set_yticklabels(COUNTED); ax.set_ylim(-0.6, 3.1)
    ax.set_xlabel("content coupling $J^c_{ij}$ (all eligible pairs)", fontsize=6.5)
    ax.scatter([], [], s=18, marker="D", color=BLUE, label="same-role rivals")
    ax.scatter([], [], s=18, marker="v", color=ORANGE, label="opposed (prankster)")
    ax.legend(fontsize=5.5, loc="upper left", handletextpad=0.2, frameon=True, framealpha=0.92, edgecolor="none", borderpad=0.3)
    ax.set_title("A  couplings are mostly positive;\n    rivals sit high, not low", loc="left", fontsize=7)
    ax.tick_params(labelsize=6)
    ax = axs[1]
    ref = {m: [r for r in syn["E3"] if r["model"] == m and r["unit"] == "51b"][0]["W_med"] for m in ("rf", "drift", "glass")}
    for k, u in enumerate(COUNTED):
        o = R[u]["overlap"]
        ax.scatter(k, o["W"], s=22, color=BLUE, zorder=3)
        ax.annotate(f"M={o['M']:.2f}", (k, o["W"]), fontsize=5.5, color=INK2, xytext=(4, 2), textcoords="offset points")
    ax.axhspan(0.8, 1.25, color=GRID, alpha=0.8, lw=0)
    ax.axhline(ref["glass"], color=VIOLET, lw=0.8, ls="--")
    ax.text(2.4, ref["glass"] * 0.8, f"synthetic glass\n(median W={ref['glass']:.0f})", fontsize=5.5, color=VIOLET, ha="right", va="top")
    ax.text(2.4, 1.3, "independent agents\n(rf / drift)", fontsize=5.5, color=INK2, ha="right", va="bottom")
    ax.set_yscale("log"); ax.set_ylim(0.4, 25)
    ax.set_xticks(range(len(COUNTED))); ax.set_xticklabels(COUNTED); ax.set_xlim(-0.5, 2.5)
    ax.set_ylabel("overlap synchrony W", fontsize=6.5); ax.tick_params(labelsize=6)
    ax.set_title("B  no collective\n    metastable states", loc="left", fontsize=7)
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)


if __name__ == "__main__":
    main()
