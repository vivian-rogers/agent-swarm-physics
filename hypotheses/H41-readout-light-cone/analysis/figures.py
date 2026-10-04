"""H41 figures (matplotlib -> PDF/PNG in ../figures and per-period folders).

  uv run python hypotheses/H41-readout-light-cone/analysis/figures.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
HDIR = HERE.parent
FIG = HDIR / "figures"
DATA = HDIR.parents[1] / "data/processed/H41-readout-light-cone"
RES = DATA / "results"
REG = {"I": "#2a78d6", "II": "#eb6834", "III": "#1baf7a"}  # categorical slots 1-3 (validated all-pairs)
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
                     "legend.frameon": False, "font.family": "DejaVu Sans"})


def _clip(x, lo=0.2, hi=60):
    return np.clip(np.where(np.isfinite(x), x, hi), lo, hi)


def jump_panel(ax, t, syn):
    t = t.sort("goal")
    x = np.arange(t.height)
    for i, r in enumerate(t.iter_rows(named=True)):
        c = REG.get(r["regime"], INK2)
        j, lo, hi = r["J_mh"], r["J_mh_lo"], r["J_mh_hi"]
        if j is not None and np.isfinite(lo or np.nan):
            ax.plot([i, i], _clip(np.array([lo, hi])), color=c, lw=1.0, alpha=0.8)
        if j is not None:
            if np.isfinite(j):
                ax.plot(i, _clip(np.array([j]))[0], "o", ms=3.6, color=c, mec="white", mew=0.5, zorder=3)
            else:  # no in-flight adoptions at matched delays: estimate unbounded
                ax.plot(i, 50, "^", ms=3.8, color=c, mec="white", mew=0.5, zorder=3)
        ji = r["J_in"]
        if ji is not None:
            ax.plot(i + 0.28, _clip(np.array([ji]))[0], "o", ms=3.0, mfc="none", mec=c, mew=0.7, zorder=3)
    ax.axhline(1, color=INK2, lw=0.6, ls="--")
    if syn is not None:
        f = syn.filter(pl.col("truth") == "T2")
        if f.height and "J_mh" in f.columns:
            lo, hi = np.nanquantile(f["J_mh"].to_numpy().astype(float), [0.1, 0.9])
            ax.axhspan(max(lo, 0.2), hi, color=GRID, zorder=0, lw=0)
            ax.text(t.height - 0.3, max(lo, 0.2) * 0.93, "shared-field synthetic (10-90%)", ha="right", va="top",
                    color=INK2, fontsize=5.5)
    ax.set_yscale("log")
    ax.set_ylim(0.2, 200)
    ax.set_xticks(x)
    ax.set_xticklabels([str(g) for g in t["goal"].to_list()], fontsize=5.2, rotation=90)
    ax.set_xlabel("goal period")
    ax.set_ylabel("jump J at the cone boundary")
    for k, c in REG.items():
        ax.plot([], [], "o", color=c, ms=3.5, label=f"regime {k}")
    ax.plot([], [], "o", mfc="none", mec=INK2, ms=3, label="unmatched (pre-registered)")
    ax.plot([], [], "o", color=INK2, ms=3.5, label="delay-matched (post hoc)")
    ax.plot([], [], "^", color=INK2, ms=3.5, label="matched, unbounded")
    ax.legend(fontsize=5.2, ncol=3, loc="upper left", handletextpad=0.2, columnspacing=0.6)
    ax.set_title("(a) adoption hazard: first call that read the item vs call in flight", fontsize=6.8, loc="left")


def acaus_panel(ax, t):
    t = t.sort("goal")
    two = t.filter(pl.col("share_cross") > 0.01)
    x = np.arange(t.height)
    g2i = {g: i for i, g in enumerate(t["goal"].to_list())}
    for r in t.iter_rows(named=True):
        ax.plot(g2i[r["goal"]], max(r["acaus_rob_within"] or 0, 1e-3), "o", ms=3.2, color=REG.get(r["regime"], INK2),
                mec="white", mew=0.4)
    for r in two.iter_rows(named=True):
        if r["acaus_rob_cross"] is not None and np.isfinite(r["acaus_rob_cross"]):
            ax.plot(g2i[r["goal"]], r["acaus_rob_cross"], "s", ms=3.6, mfc="none", mec=REG.get(r["regime"], INK2), mew=0.8)
    ax.set_yscale("log")
    ax.set_ylim(8e-4, 1.5)
    ax.set_xticks(x)
    ax.set_xticklabels([str(g) for g in t["goal"].to_list()], fontsize=5.2, rotation=90)
    ax.set_xlabel("goal period")
    ax.set_ylabel("share outside the logged cone\n(0 drawn at 10$^{-3}$)", fontsize=6)
    ax.plot([], [], "o", color=INK2, ms=3, label="adopter in the source's room")
    ax.plot([], [], "s", mfc="none", mec=INK2, ms=3.4, label="adopter in another room")
    ax.legend(fontsize=5.5, loc="center left")
    ax.set_title("(b) robust acausal share of adoptions", fontsize=6.8, loc="left")


def summary_obs(t, syn):
    fig, axs = plt.subplots(2, 1, figsize=(4.0, 4.3))
    jump_panel(axs[0], t, syn)
    acaus_panel(axs[1], t)
    fig.tight_layout(h_pad=0.6)
    fig.savefig(FIG / "summary_obs.pdf")
    fig.savefig(FIG / "summary_obs.png", dpi=200)
    plt.close(fig)


def synthetic_fig(syn):
    if syn is None:
        return
    fig, axs = plt.subplots(1, 2, figsize=(4.0, 1.95))
    order = [("T1", 0.15, "relay"), ("T1d", 0.4, "relay, decaying"), ("T4", 0.15, "relay + timing error"),
             ("T3", 0.15, "relay + hidden channel"), ("T2", 0.0, "shared field")]
    sk_col = {"31": REG["I"], "38": "#4a3aa7", "51": REG["III"]}
    for k, (tr, q, lab) in enumerate(order):
        for j, skn in enumerate(["31", "38", "51"]):
            d = syn.filter((pl.col("truth") == tr) & (pl.col("q") == q) & (pl.col("skel") == skn))
            if d.height == 0:
                continue
            for col, ax, mk in [("J_in", axs[0], "o"), ("J_mh", axs[0], "s")]:
                if col not in d.columns:
                    continue
                y = _clip(d[col].to_numpy().astype(float), 0.2, 200)
                ax.plot(np.full(len(y), k + (j - 1) * 0.18 + (0.06 if mk == "s" else -0.06)), y, mk, ms=2.4,
                        color=sk_col[skn], mfc=sk_col[skn] if mk == "s" else "none", mew=0.6)
            y = d["A_early"].to_numpy().astype(float)
            axs[1].plot(np.full(len(y), k + (j - 1) * 0.18), np.maximum(y, 1e-3), "o", ms=2.4, color=sk_col[skn])
    axs[0].axhline(1, color=INK2, lw=0.6, ls="--")
    axs[0].set_yscale("log")
    axs[0].set_ylabel("jump J (∞ drawn at 200)", fontsize=6)
    axs[0].set_title("(a) J: open unmatched, filled matched", fontsize=6.3, loc="left")
    axs[1].set_yscale("log")
    axs[1].set_ylabel("share (0 drawn at 10$^{-3}$)", fontsize=6)
    axs[1].set_title("(b) acausal share, early adoptions", fontsize=6.3, loc="left")
    for ax in axs:
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels([o[2] for o in order], rotation=40, ha="right", fontsize=5.2)
    for skn, c in sk_col.items():
        axs[1].plot([], [], "o", color=c, ms=3, label={"31": "#31 (I, one room)", "38": "#38 (two rooms)",
                                                       "51": "#51 segment"}[skn])
    axs[1].legend(fontsize=5, loc="upper left")
    fig.tight_layout(w_pad=0.6)
    fig.savefig(FIG / "summary_obs2.pdf")
    fig.savefig(FIG / "summary_obs2.png", dpi=200)
    plt.close(fig)


def hazard_delay_fig(periods=(31, 38, 51)):
    fig, axs = plt.subplots(1, len(periods), figsize=(5.5, 1.8), sharey=True)
    edges = ["<30 s", "30–60 s", "1–2 min", "2–5 min", "5–15 min", ">15 min"]
    for ax, g in zip(axs, periods):
        p = DATA / f"G{g:02d}/hazard.parquet"
        if not p.exists():
            continue
        hz = pl.read_parquet(p).filter(pl.col("in_room0"))
        for grp, mk, lab in [("pre_in", "s", "call in flight at t0"), ("o1", "o", "first call after the item was read")]:
            x = hz.filter(pl.col("group") == grp).group_by("dbin").agg(pl.col("at_risk").sum(), pl.col("adopt").sum()).sort("dbin")
            x = x.filter(pl.col("at_risk") >= 20)
            h = (x["adopt"] / x["at_risk"]).to_numpy()
            ax.plot(x["dbin"].to_numpy(), np.maximum(h, 1e-4), marker=mk, ms=3, lw=1.2,
                    color=REG["II"] if grp == "pre_in" else REG["I"], label=lab)
        ax.set_yscale("log")
        ax.set_xticks(range(6))
        ax.set_xticklabels(edges, rotation=45, ha="right", fontsize=5)
        ax.set_title(f"G{g}", fontsize=7)
    axs[0].set_ylabel("adoption hazard per talk call")
    axs[0].legend(fontsize=5, loc="lower left")
    fig.tight_layout(w_pad=0.4)
    fig.savefig(FIG / "hazard_by_delay.pdf")
    fig.savefig(FIG / "hazard_by_delay.png", dpi=200)
    plt.close(fig)


def native_figs(nat):
    pdir = HDIR / "goalperiod-subhypotheses"
    # NE42: cross-group hazard per talk call across the A-B-A
    ne = nat.get("NE42")
    if ne:
        fig, ax = plt.subplots(figsize=(2.6, 1.8))
        for k, g in enumerate(["G39", "G40", "G41"]):
            r = ne[g]
            ax.bar(k - 0.18, r["h_cross"] or 0, 0.34, color=REG["II"], label="cross-group" if k == 0 else None)
            ax.bar(k + 0.18, r["h_within"] or 0, 0.34, color=REG["I"], label="within-group" if k == 0 else None)
        ax.set_xticks(range(3))
        ax.set_xticklabels(["#39 split", "#40 merged", "#41 split"])
        ax.set_ylabel("adoption hazard per talk call (2 h)", fontsize=6)
        ax.legend(fontsize=5.5)
        fig.tight_layout()
        (pdir / "NE42/figures").mkdir(parents=True, exist_ok=True)
        fig.savefig(pdir / "NE42/figures/ne42_hazard.pdf")
        fig.savefig(pdir / "NE42/figures/ne42_hazard.png", dpi=200)
        plt.close(fig)
    g = nat.get("G38")
    if g:
        fig, ax = plt.subplots(figsize=(2.6, 1.8))
        ax.bar([0, 1], [g["h_in"], g["h_out"]], 0.5, color=[REG["I"], REG["II"]])
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["source's room", "other room"])
        ax.set_ylabel("adoption hazard per talk call (2 h)", fontsize=6)
        ax.set_title(f"G38: ratio {g['b_ratio']:.3f}", fontsize=7)
        fig.tight_layout()
        fig.savefig(pdir / "G38/figures/g38_cage.pdf")
        fig.savefig(pdir / "G38/figures/g38_cage.png", dpi=200)
        plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    t = pl.read_parquet(RES / "period_table.parquet")
    sp = DATA / "synthetic/runs_v2.parquet"
    syn = pl.read_parquet(sp) if sp.exists() else (pl.read_parquet(DATA / "synthetic/runs.parquet")
                                                    if (DATA / "synthetic/runs.parquet").exists() else None)
    summary_obs(t, syn)
    synthetic_fig(syn)
    hazard_delay_fig()
    if (RES / "native.json").exists():
        native_figs(json.loads((RES / "native.json").read_text()))
    print("figures written")


if __name__ == "__main__":
    main()
