"""H48 figures (static PDFs for the card, the period READMEs and the RevTeX summary).

  uv run python hypotheses/H48-settling-mixing-time/analysis/figures.py
Palette: reference categorical slots (blue, orange, aqua) validated with the dataviz validator (light surface);
regime is also encoded by marker shape, and points carry period labels (aqua is below 3:1 contrast)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h48lib as L  # noqa: E402
from h48lib import hc  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

BLUE, ORANGE, AQUA, INK, INK2, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e4e3df"
REG = {"I": (BLUE, "o"), "II": (ORANGE, "s"), "III": (AQUA, "^")}
FIG = hc.HDIR / "figures"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "lines.linewidth": 1.5,
                     "legend.frameon": False, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb"})


def save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def summary_obs():
    S = pl.read_parquet(hc.OUT / "settling_period.parquet")
    X = pl.read_parquet(hc.OUT / "readout_period.parquet")
    T = S.filter((pl.col("model") == "bge_small") & (pl.col("estimator") == "S1") & pl.col("detected").fill_null(False))
    D = X.join(T.select("goal_no", "tau"), on="goal_no").filter(pl.col("goal_no").is_in(hc.REPLICATION))
    lp = pl.read_parquet(hc.OUT / "compare_lopo.parquet").filter(~pl.col("regime_intercepts"))
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.6), gridspec_kw={"width_ratios": [1, 1.15]})
    a = ax[0]
    lim = [0.01, 60]
    a.plot(lim, lim, color=INK2, lw=0.8, ls="--")
    a.text(0.013, 0.02, "τ = coverage time", color=INK2, fontsize=6, rotation=33)
    for r in D.iter_rows(named=True):
        c, m = REG[r["regime"]]
        a.scatter(r["k1_room_T90"], r["tau"], s=22, color=c, marker=m, edgecolor="#fcfcfb", linewidth=0.6, zorder=3)
        a.scatter(r["k5_room_T90"], r["tau"], s=22, facecolor="none", edgecolor=c, marker=m, linewidth=0.9, zorder=3)
        a.plot([r["k1_room_T90"], r["k5_room_T90"]], [r["tau"]] * 2, color=GRID, lw=0.8, zorder=1)
        a.annotate(f"#{r['goal_no']}", (r["k5_room_T90"], r["tau"]), xytext=(3, 1), textcoords="offset points",
                   fontsize=5.5, color=INK2)
    a.set_xscale("log"); a.set_yscale("log"); a.set_xlim(lim); a.set_ylim(0.2, 60)
    a.set_xlabel("read-out coverage time T90 (active h)\nfilled: read ≥ 1 message · hollow: ≥ 5 messages")
    a.set_ylabel("settling time τ_S1 (active h, bge)")
    for k, (c, m) in REG.items():
        a.scatter([], [], color=c, marker=m, s=18, label=f"regime {k}")
    a.legend(loc="lower right", fontsize=6, handletextpad=0.2)
    a.set_title("(a) settling vs coverage, 11 detected periods", loc="left", fontsize=7.5)
    b = ax[1]
    preds = [("T90_k1_room", "coverage T90 (k = 1) ★"), ("tmix_batch_bulk", "bulk mixing t_mix ★"),
             ("T90_k5_room", "coverage T90 (k = 5)"), ("reading_rate", "1 / reading rate"),
             ("l2_sym_min", "1 / λ₂ (w,sym, ledger)"), ("h31_l2_sym_min", "1 / λ₂ (H31 published)"),
             ("n_rooms", "room count"), ("N", "N agents"), ("hours_per_day", "hours per day")]
    yy = np.arange(len(preds))[::-1]
    for off, model, col in ((0.18, "bge_small", BLUE), (-0.18, "gte_modernbert", ORANGE)):
        g = []
        for p, _ in preds:
            s = lp.filter((pl.col("model") == model) & (pl.col("predictor") == p))
            g.append(float(s["gain"][0]) if s.height else np.nan)
        b.barh(yy + off, np.clip(g, -0.5, None), height=0.34, color=col, label=model.split("_")[0])
    b.axvline(0, color=INK, lw=0.8)
    b.axvline(0.10, color=INK2, lw=0.8, ls=":")
    b.set_yticks(yy); b.set_yticklabels([lab for _, lab in preds], fontsize=6)
    b.set_xlim(-0.5, 0.35)
    b.set_xlabel("LOPO gain vs constant (1 − RMSE/RMSE₀); dotted = 10% bar")
    b.legend(loc="lower right", fontsize=6)
    b.set_title("(b) leave-one-period-out prediction (★ primary)", loc="left", fontsize=7.5)
    b.grid(axis="y", visible=False)
    fig.tight_layout()
    save(fig, FIG / "H48_summary_obs.pdf")


def synthetic():
    preds = [("T90_k1_room", "T90 k1"), ("T90_k5_room", "T90 k5"), ("tmix_batch_bulk", "t_mix bulk"),
             ("reading_rate", "1/reading"), ("l2_sym_min", "1/λ₂"), ("n_rooms", "rooms")]
    sets = [("synthetic/summary.json", "(a) as pre-registered (S1 detected 93–100%)"),
            ("synthetic/realistic/summary.json", "(b) real-like noise (S1 detected 37–70%)")]
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.1), sharey=True)
    for a, (path, title) in zip(ax, sets):
        p = hc.OUT / path
        if not p.exists():
            continue
        s = hc.load_json(p)
        x = np.arange(len(preds))
        for k, (truth, col, lab) in enumerate((("RD", BLUE, "RD read-out DeGroot"), ("RC", ORANGE, "RC coverage"),
                                                ("FD", AQUA, "FD field clock"))):
            if truth not in s["truths"]:
                continue
            v = [s["truths"][truth]["predictors"].get(pp, {}).get("pass_rate", np.nan) for pp, _ in preds]
            a.bar(x + (k - 1) * 0.27, v, width=0.25, color=col, label=lab)
        a.set_xticks(x); a.set_xticklabels([lab for _, lab in preds], fontsize=6)
        a.set_ylim(0, 1.05)
        a.set_title(title, loc="left", fontsize=7.5)
        a.grid(axis="x", visible=False)
    ax[0].set_ylabel("pass rate (gain ≥ 10%, p < 0.05)")
    ax[1].legend(loc="upper right", fontsize=6)
    fig.tight_layout()
    save(fig, FIG / "H48_synthetic.pdf")


def series():
    periods = [4, 12, 38, 40]
    fig, ax = plt.subplots(1, 5, figsize=(7.0, 1.8))
    a = ax[0]
    for g, col in zip(periods, (BLUE, ORANGE, AQUA, INK2)):
        c = pl.read_parquet(hc.OUT / f"G{g:02d}" / "coverage_curves.parquet")
        a.plot(np.maximum(c["a"].to_numpy(), 0.01), c["k1_room"].to_numpy(), color=col, lw=1.2, label=f"#{g}")
    a.set_xscale("log"); a.set_xlabel("active h since kickoff"); a.set_ylabel("share of room pairs read")
    a.set_title("coverage C₁(t)", loc="left", fontsize=7)
    a.legend(fontsize=5.5, loc="lower right")
    S = pl.read_parquet(hc.OUT / "settling_period.parquet")
    for a, g in zip(ax[1:], periods):
        s = pl.read_parquet(hc.OUT / f"G{g:02d}" / "s1_series_bge_small.parquet")
        a.plot(s["a"], s["excess"], color=BLUE, lw=0.9, marker="o", ms=1.8)
        f = S.filter((pl.col("goal_no") == g) & (pl.col("model") == "bge_small") & (pl.col("estimator") == "S1")).row(0, named=True)
        if f.get("tau") is not None and np.isfinite(f["tau"]):
            t = np.linspace(s["a"].min(), s["a"].max(), 200)
            a.plot(t, f["A_inf"] + (f["A_0"] - f["A_inf"]) * np.exp(-(t - s["a"].min()) / f["tau"]), color=ORANGE, lw=1.2)
        a.set_title(f"#{g}: τ {f['tau']:.1f} h ({'detected' if f['detected'] else 'not detected'})", loc="left", fontsize=6.5)
        a.set_xlabel("active h")
    ax[1].set_ylabel("kickoff excess")
    fig.tight_layout()
    save(fig, FIG / "H48_coverage_and_settling.pdf")


def natives():
    p = hc.OUT / "NE42" / "blocks.parquet"
    if p.exists():
        d = pl.read_parquet(p)
        fig, a = plt.subplots(figsize=(3.0, 2.2))
        for r in d.iter_rows(named=True):
            for model, col, m in (("bge_small", BLUE, "o"), ("gte_modernbert", ORANGE, "s")):
                a.scatter(r["T90"], r[f"tau_{model}"], color=col, marker=m, s=20)
            a.annotate(f"#{r['goal_no']} r{r['room']} (N {r['N']})", (r["T90"], r["tau_bge_small"]), xytext=(3, 2),
                       textcoords="offset points", fontsize=5.5, color=INK2)
        a.set_xscale("log"); a.set_yscale("log")
        a.scatter([], [], color=BLUE, marker="o", label="bge"); a.scatter([], [], color=ORANGE, marker="s", label="gte")
        a.legend(fontsize=6)
        a.set_xlabel("room-block coverage T90 (active h)"); a.set_ylabel("τ_S1 (active h)")
        save(fig, hc.HDIR / "goalperiod-subhypotheses/NE42/figures/ne42_blocks.pdf")
    p = hc.OUT / "G51" / "newcomer_series.parquet"
    if p.exists():
        d = pl.read_parquet(p).filter((pl.col("model") == "bge_small") & (pl.col("clock") != "ne32_fine"))
        fig, a = plt.subplots(figsize=(3.0, 2.2))
        for ag, sub in d.group_by("agent"):
            a.plot(sub["t"], sub["gap"], color=GRID if True else INK2, lw=0.8)
        med = d.group_by("t").agg(pl.col("gap").median()).sort("t")
        a.plot(med["t"], med["gap"], color=BLUE, lw=1.6, label="median over newcomers")
        a.axhline(0, color=INK2, lw=0.6)
        a.set_xlabel("active h since join (merge for isolated)"); a.set_ylabel("assimilation gap b − s_n")
        a.legend(fontsize=6)
        save(fig, hc.HDIR / "goalperiod-subhypotheses/G51/figures/newcomer_gaps.pdf")
    fig, a = plt.subplots(figsize=(3.0, 2.2))
    ok = False
    for b, col in ((2, BLUE), (3, ORANGE)):
        p = hc.OUT / "G38" / f"s1_room{b}_bge_small.parquet"
        if p.exists():
            s = pl.read_parquet(p)
            a.plot(s["a"], s["excess"], color=col, lw=0.8, label=f"room {b} ({'#best' if b == 2 else '#rest'})")
            ok = True
    if ok:
        a.set_xlabel("active h since kickoff"); a.set_ylabel("kickoff excess (bge)")
        a.legend(fontsize=6)
        save(fig, hc.HDIR / "goalperiod-subhypotheses/G38/figures/g38_rooms.pdf")
    else:
        plt.close(fig)


if __name__ == "__main__":
    summary_obs()
    synthetic()
    series()
    natives()
