"""H29 figures: the one-page figure summary (figures/h29_summary.pdf) and the summary-page observables figure
(figures/h29_obs.pdf). Palette: validated reference slots 1-3 (blue, orange, aqua) + ink/grid tokens (as H18).

  uv run python hypotheses/H29-driver-nodes/analysis/figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h29lib as L  # noqa: E402
from explore import COUNTED, DESCRIPTIVE  # noqa: E402

INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
                     "font.family": "sans-serif", "pdf.fonttype": 42})
UNITS = ["G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51a", "G51b", "G51c", "G51d", "G51e"]
DT_EDGES = [0, 10, 20, 40, 80, 160, 320, 640, 1280, 1e9]


def dt_curve(unit: str):
    emb = L.Emb()
    U = L.attach_vectors(L.load_unit(unit), emb)
    R = L.add_timing(U, L.row_stats(U)).filter(pl.col("yu_x").is_not_nan() & (pl.col("kind") == 0))
    out = {}
    for lab, flt in (("visible", pl.col("vis")), ("invisible, call ≤ 30 s", ~pl.col("vis") & (pl.col("c") <= 30)),
                     ("'invisible', call > 30 s", ~pl.col("vis") & (pl.col("c") > 30))):
        xs, ys, ns = [], [], []
        for lo, hi in zip(DT_EDGES[:-1], DT_EDGES[1:]):
            s = R.filter(flt & (pl.col("dt_talk") >= lo) & (pl.col("dt_talk") < hi))
            if s.height < 40:
                continue
            xs.append(np.sqrt(max(lo, 3) * min(hi, 3000)))
            ys.append(s["yu"].sum() / s["uu"].sum() - s["yu_x"].sum() / s["uu_x"].sum())
            ns.append(s.height)
        out[lab] = (np.array(xs), np.array(ys), np.array(ns))
    return out


def load(u, kind):
    return json.loads((L.OUT / u / ("results.json" if kind == "pre" else "results_posthoc.json")).read_text())


def panel_dt(ax, unit="G51b"):
    cur = dt_curve(unit)
    cols = {"visible": C1, "invisible, call ≤ 30 s": C2, "'invisible', call > 30 s": C3}
    for lab, (x, y, n) in cur.items():
        ax.plot(x, y, "-o", color=cols[lab], ms=3, lw=1.2, label=lab, mec="white", mew=0.5)
    ax.set_xscale("log")
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_xlabel("time from message to the reply (s)")
    ax.set_ylabel("field-corrected pull per message")
    ax.legend(fontsize=6, loc="upper right")
    ax.set_title(f"a  Pull toward a message vs its age ({unit})", loc="left", fontsize=7.5, color=INK)


def panel_named(ax, post):
    x = np.arange(len(UNITS))
    for off, key, col, lab in ((-0.17, "rd_named_ll", C1, "named recipient"), (0.17, "rd_unnamed_ll", C2, "unnamed recipient")):
        y = np.array([post[u][key]["jump"] for u in UNITS], dtype=float)
        lo = np.array([post[u][key]["ci"][0] if post[u][key]["ci"] else np.nan for u in UNITS])
        hi = np.array([post[u][key]["ci"][1] if post[u][key]["ci"] else np.nan for u in UNITS])
        ax.errorbar(x + off, y, yerr=[y - lo, hi - y], fmt="o", ms=3, color=col, lw=0.9, capsize=0, label=lab)
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels([u[1:] for u in UNITS], fontsize=6)
    ax.set_xlabel("unit (goal period / #51 segment)")
    ax.set_ylabel("visibility jump (post hoc, like-for-like)")
    ax.set_ylim(-0.25, 0.3)
    ax.legend(fontsize=6, loc="upper left")
    ax.set_title("b  Seen vs unseen messages at matched age", loc="left", fontsize=7.5, color=INK)


def panel_reliability(ax, pre, post):
    x = np.arange(len(UNITS))
    ax.axhspan(0.3, 0.85, color=GRID, alpha=0.5, lw=0)
    ax.text(-0.4, 0.31, "range for a true model (synthetic)", fontsize=5.5, color=INK2, ha="left", va="bottom")
    for off, src, key, col, lab in ((-0.2, pre, "D", C1, "driver score, pre-registered"),
                                    (0.0, post, "D", C3, "driver score, post hoc"),
                                    (0.2, pre, "vol", C2, "message volume")):
        y = np.array([(src[u].get("split_half") or {}).get(key, np.nan) or np.nan for u in UNITS], dtype=float)
        ax.plot(x + off, y, "o", ms=3.2, color=col, label=lab, mec="white", mew=0.4)
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels([u[1:] for u in UNITS], fontsize=6)
    ax.set_ylabel("split-half Spearman (even vs odd days)")
    ax.set_ylim(-0.7, 1.05)
    ax.legend(fontsize=6, loc="lower left", ncol=1)
    ax.set_title("c  Is the ranking reproducible?", loc="left", fontsize=7.5, color=INK)


def panel_validation(ax, pre, post):
    x = np.arange(len(UNITS))
    for off, src, key, col, lab in ((-0.2, post, "V2_D", C3, "driver score (post hoc)"),
                                    (0.0, pre, "V2_vol", C2, "message volume"),
                                    (0.2, pre, "V2_out", C1, "out-strength")):
        y = np.array([((src[u].get("V") or {}).get(key)) for u in UNITS], dtype=float)
        ax.plot(x + off, y, "o", ms=3.2, color=col, label=lab, mec="white", mew=0.4)
    hs = np.array([pre[u].get("H_split_half", np.nan) or np.nan for u in UNITS], dtype=float)
    ax.bar(x, hs, width=0.75, color=GRID, zorder=0, label="observed spread: split-half")
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels([u[1:] for u in UNITS], fontsize=6)
    ax.set_ylabel("Spearman with held-out 2-h swarm spread")
    ax.set_ylim(-0.7, 0.8)
    ax.legend(fontsize=5.8, loc="upper left", ncol=2)
    ax.set_title("d  Does any ranking predict observed spread?", loc="left", fontsize=7.5, color=INK)


def panel_scaling(ax, pre, post, S):
    N = np.array([post[u]["n_agents"] for u in UNITS], float)
    Es = np.array([post[u]["E_star"] for u in UNITS])
    Em = np.array([post[u]["E_med"] for u in UNITS])
    two = np.array([not u.startswith("G51") for u in UNITS])
    for m, lab in ((two, "two-room era"), (~two, "#51 (one room)")):
        mk = "o" if lab.startswith("two") else "s"
        ax.plot(N[m], Em[m], mk, color=C1, ms=3.5, mec="white", mew=0.4, label=f"median agent, {lab}")
        ax.plot(N[m], Es[m], mk, color=C2, ms=3.5, mec="white", mew=0.4, label=f"best driver, {lab}")
    xs = np.linspace(9, 28, 20)
    ax.plot(xs, 250 * (xs / 13) ** 2, ls="--", color=INK2, lw=0.8)
    ax.text(9.2, 250 * (9.2 / 13) ** 2 * 0.62, "∝ N²", fontsize=6, color=INK2, ha="left")
    ax.plot(xs, 60 * (xs / 13) ** 1.2, ls=":", color=INK2, lw=0.8)
    ax.text(27, 60 * (27 / 13) ** 1.2 * 0.7, "∝ N^1.2 (HH110)", fontsize=6, color=INK2, ha="right", va="top")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([10, 15, 20, 25])
    ax.set_xticklabels(["10", "15", "20", "25"])
    ax.set_xlabel("N (agents in the network)")
    ax.set_ylabel("energy to shift the swarm mean (post hoc model)")
    ax.set_ylim(25, 6000)
    ax.legend(fontsize=5.5, loc="upper left", ncol=1)
    e1, e2 = S["P8"]["post_Emed"], S["P8"]["post_Estar"]
    ax.set_title(f"e  Steering cost vs N (η med {e1['eta']:.1f}, best {e2['eta']:.1f})", loc="left", fontsize=7.5, color=INK)


def panel_synth(ax, S):
    syn = S["synthetic"]
    conds = [("G38/lin03", "G38 lin"), ("G38/nl03", "G38 nonlin"), ("G41/lin03", "G41 lin"), ("G41/nl03", "G41 nonlin"),
             ("G51b/lin01", "G51b lin"), ("G51b/nl03", "G51b nonlin")]
    x = np.arange(len(conds))
    for off, key, col, lab in ((-0.2, "rho_D", C3, "driver score D̂"), (0.0, "rho_out", C1, "out-strength"),
                               (0.2, "rho_vol", C2, "message volume")):
        y = [syn[c]["marginal"][key] for c, _ in conds]
        ax.plot(x + off, y, "o", ms=3.4, color=col, label=lab, mec="white", mew=0.4)
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels([l for _, l in conds], fontsize=5.8, rotation=20)
    ax.set_ylabel("Spearman with true injection ranking")
    ax.set_ylim(-0.3, 1.0)
    ax.legend(fontsize=6, loc="lower left")
    ax.set_title("f  Synthetic: who should you inject into?", loc="left", fontsize=7.5, color=INK)


def main():
    pre = {u: load(u, "pre") for u in UNITS}
    post = {u: load(u, "post") for u in UNITS}
    S = json.loads((L.OUT / "summary.json").read_text())
    L.FIG.mkdir(parents=True, exist_ok=True)
    fig, axs = plt.subplots(3, 2, figsize=(7.2, 9.0))
    panel_dt(axs[0, 0])
    panel_named(axs[0, 1], post)
    panel_reliability(axs[1, 0], pre, post)
    panel_validation(axs[1, 1], pre, post)
    panel_scaling(axs[2, 0], pre, post, S)
    panel_synth(axs[2, 1], S)
    fig.suptitle("H29 driver nodes, round 1: influence is real but address-gated; no validated 'where to inject' ranking",
                 fontsize=8.5, color=INK, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    fig.savefig(L.FIG / "h29_summary.pdf")
    fig.savefig(L.FIG / "h29_summary.png", dpi=150)
    plt.close(fig)
    # summary-page observables figure: two panels
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.5))
    panel_named(axs[0], post)
    panel_reliability(axs[1], pre, post)
    axs[0].set_title("a  Seen vs unseen messages at matched age", loc="left", fontsize=7.5)
    axs[1].set_title("b  Is the driver ranking reproducible?", loc="left", fontsize=7.5)
    fig.tight_layout()
    fig.savefig(L.FIG / "h29_obs.pdf")
    fig.savefig(L.FIG / "h29_obs.png", dpi=150)
    plt.close(fig)
    # page-2 figure (column width, <= 2.1 in tall): synthetic recovery + held-out validation
    with plt.rc_context({"font.size": 5.6}):
        fig, axs = plt.subplots(1, 2, figsize=(3.45, 2.0), gridspec_kw=dict(width_ratios=[1, 1.5]))
        syn = S["synthetic"]
        conds = [("G38/lin03", "G38"), ("G41/lin03", "G41"), ("G51b/lin01", "G51b"), ("G38/nl03", "G38nl")]
        x = np.arange(len(conds))
        for off, key, col, lab in ((-0.2, "rho_D", C3, "driver score"), (0.0, "rho_out", C1, "out-strength"),
                                   (0.2, "rho_vol", C2, "volume")):
            axs[0].plot(x + off, [syn[c]["marginal"][key] for c, _ in conds], "o", ms=2.6, color=col, label=lab,
                        mec="white", mew=0.3)
        axs[0].axhline(0, color=INK2, lw=0.5)
        axs[0].set_xticks(x)
        axs[0].set_xticklabels([l for _, l in conds], fontsize=5)
        axs[0].set_ylim(-0.3, 1.0)
        axs[0].set_ylabel("ρ with true injection ranking")
        axs[0].legend(fontsize=4.8, loc="lower left", handletextpad=0.2)
        axs[0].set_title("a  synthetic recovery", loc="left", fontsize=6)
        xu = np.arange(len(UNITS))
        hs = np.array([pre[u].get("H_split_half", np.nan) or np.nan for u in UNITS], dtype=float)
        axs[1].bar(xu, hs, width=0.75, color=GRID, zorder=0, label="spread split-half")
        for off, src, key, col, lab in ((-0.15, post, "V2_D", C3, "driver score"), (0.15, pre, "V2_vol", C2, "volume")):
            y = np.array([((src[u].get("V") or {}).get(key)) for u in UNITS], dtype=float)
            axs[1].plot(xu + off, y, "o", ms=2.6, color=col, label=lab, mec="white", mew=0.3)
        axs[1].axhline(0, color=INK2, lw=0.5)
        axs[1].set_xticks(xu)
        axs[1].set_xticklabels([u[1:] for u in UNITS], fontsize=4.4, rotation=90)
        axs[1].set_ylim(-0.6, 0.98)
        axs[1].set_ylabel("ρ with held-out 2-h spread")
        axs[1].legend(fontsize=4.8, loc="upper right", ncol=2, handletextpad=0.2, columnspacing=0.6)
        axs[1].set_title("b  real data: held-out validation", loc="left", fontsize=6)
        fig.tight_layout(pad=0.3)
        fig.savefig(L.FIG / "h29_obsb.pdf")
        fig.savefig(L.FIG / "h29_obsb.png", dpi=200)
        plt.close(fig)
    print("figures written")


if __name__ == "__main__":
    main()
