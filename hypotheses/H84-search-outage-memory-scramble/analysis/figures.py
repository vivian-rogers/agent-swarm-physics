"""H84 summary figures (static PDFs for the RevTeX page).

figures/summary_obs.pdf   (a) first stage: daily median answer length of the searchers, 03-24 -> 04-10 (log scale);
                          (b) dose x outage beta for V1 (continuity) and V3 (earlier-goal references) against the 38
                          placebo pairs and the kickoff-matched pairs.
figures/summary_obsb.pdf  (a) synthetic power of the V1 and V3 tests vs planted dip; (b) replication: I_Q per period.
Palette: reference categorical slots 1-3 (blue, orange, aqua), validated in the dataviz reference palette.
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
import h84lib as L  # noqa: E402

BLUE, ORANGE, AQUA, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "legend.frameon": False, "pdf.fonttype": 42})
FIG = L.ROOT / "hypotheses/H84-search-outage-memory-scramble/figures"


def main():
    res = json.loads((L.DATA / "results/results.json").read_text())
    syn = json.loads((L.DATA / "synthetic/synthetic.json").read_text())
    srch = pl.read_parquet(L.DATA / "search_events.parquet")
    panel = L.load_panel()
    dose = L.dose_table(panel, L.DOSE_DAYS)
    pan = panel.filter(pl.col("agent").is_in(dose["agent"].implode()))
    excl = L.DOSE_DAYS + L.OUTAGE + L.RECOVERY
    pairs, pairs_k = L.placebo_pairs(pan, excl), L.placebo_pairs(pan, excl, kickoff_matched=True)
    FIG.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(1, 2, figsize=(4.2, 2.0), gridspec_kw={"width_ratios": [1.25, 1]})
    a = ax[0]
    days = sorted(d for d in srch["pt_date"].unique().to_list() if "2026-03-24" <= d <= "2026-04-10")
    xi = {d: i for i, d in enumerate(days)}
    a.axvspan(xi["2026-03-31"] - 0.5, xi["2026-04-01"] + 0.5, color=GRID, lw=0)
    srt = sorted(res["G37"]["dose"].items(), key=lambda kv: -kv[1])[:2]
    for (ag, dv), col in zip(srt, (BLUE, ORANGE)):
        s = (srch.filter((pl.col("agent") == int(ag)) & pl.col("pt_date").is_in(days)).group_by("pt_date")
             .agg(pl.col("ans_chars").median()).sort("pt_date"))
        a.plot([xi[d] for d in s["pt_date"]], s["ans_chars"].to_list(), "-o", color=col, ms=3, lw=1.2,
               label=f"agent {ag} (dose {dv:.1f})")
    a.set_yscale("log")
    a.set_xticks([xi[d] for d in days[::3]], [d[5:] for d in days[::3]], rotation=45)
    a.set_ylabel("median answer (chars)")
    a.text(xi["2026-03-31"], 9e3, "outage", ha="left", color=MUTED, fontsize=6.5)
    a.legend(fontsize=6, loc="lower left")
    a.set_title("(a) first stage", fontsize=7.5, loc="left")
    a = ax[1]
    for j, (k, lab) in enumerate((("V1_continuity", "V1 continuity"), ("V3_earlier_goal_refs", "V3 old refs"))):
        f = L.frame(pan, k, dose)
        pb = np.array([L.beta(f, p, [L.OUTAGE, L.RECOVERY]) for p in pairs])
        pk = np.array([L.beta(f, p, [L.OUTAGE, L.RECOVERY]) for p in pairs_k])
        rng = np.random.default_rng(j)
        a.scatter(pb, j + rng.uniform(-0.15, 0.15, len(pb)), s=6, color=MUTED, alpha=0.6, lw=0,
                  label="placebo pairs" if j == 0 else None)
        a.scatter(pk, np.full(len(pk), j + 0.3), s=10, marker="s", color=AQUA, lw=0,
                  label="kickoff-matched" if j == 0 else None)
        b = res["G37"]["tests"][k]["beta"]
        a.scatter([b], [j], s=36, color=ORANGE, zorder=3, edgecolor="white", lw=0.8, label="outage" if j == 0 else None)
    a.axvline(0, color=MUTED, lw=0.6)
    a.set_yticks([0, 1], ["V1", "V3"])
    a.set_xlabel(r"$\beta$ (per search / 100 calls)")
    a.set_ylim(-0.5, 2.2)
    a.legend(fontsize=5.6, loc="upper center", ncol=3, handletextpad=0.1, columnspacing=0.6)
    a.set_title("(b) dose × day", fontsize=7.5, loc="left")
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(4.2, 1.85))
    a = ax[0]
    for k, col, lab in (("G37_V1", BLUE, "V1"), ("G37_V3", ORANGE, "V3")):
        pw = syn[k]["power"]
        dl = [0.0, 0.1, 0.2, 0.3, 0.5]
        mid = [pw[f"s_e=0.6|delta={-d if d else 0.0}"] for d in dl]
        lo = [min(pw[f"s_e={s}|delta={-d if d else 0.0}"] for s in (0.3, 0.6, 1.0)) for d in dl]
        hi = [max(pw[f"s_e={s}|delta={-d if d else 0.0}"] for s in (0.3, 0.6, 1.0)) for d in dl]
        a.fill_between(dl, lo, hi, color=col, alpha=0.18, lw=0)
        a.plot(dl, mid, "-o", color=col, ms=3, lw=1.2, label=lab)
    a.axhline(0.8, color=MUTED, lw=0.6, ls="--")
    a.set_xlabel("planted dip at mean searcher dose")
    a.set_ylabel("power")
    a.legend(fontsize=6, loc="lower right")
    a.set_title("(a) synthetic", fontsize=7.5, loc="left")
    a = ax[1]
    rep = {k: v for k, v in res["replication"].items() if not k.startswith("_")}
    ks = list(rep)
    for i, k in enumerate(ks):
        v = rep[k]
        col = BLUE if v["p_perm"] < 0.05 else MUTED
        a.errorbar(i, v["I"], yerr=[[v["I"] - v["I_ci"][0]], [v["I_ci"][1] - v["I"]]], fmt="o", color=col, ms=3.5,
                   lw=1, capsize=0)
    a.axhline(0, color=MUTED, lw=0.6)
    a.set_xticks(range(len(ks)), ks, rotation=45)
    a.set_ylabel(r"$I_Q$ (bits)")
    a.set_title("(b) search information", fontsize=7.5, loc="left")
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "summary_obsb.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
