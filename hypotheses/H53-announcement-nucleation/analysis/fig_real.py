"""Round-1 real-data figures: event study around seeds, RR_timely across receptive windows, per-period forest, #26
ballots vs read-out, placebo AUCs and seed-model CV scores."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

from h53core import OUT, eligible_periods, load, prep  # noqa: E402

FIG = Path(__file__).resolve().parents[1] / "figures"
R1 = OUT / "round1"
NAT = OUT / "natives"
C1, C2, C3, C4, GR = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#85847e"
plt.rcParams.update({"font.size": 7.5, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#52514e",
                     "xtick.color": "#52514e", "ytick.color": "#52514e", "axes.linewidth": 0.6})
GRID = [("c0.5", "½ cycle"), ("c1", "1 cycle"), ("c2", "2 cycles"), ("c4", "4 cycles"), ("f60", "1 min"), ("f120", "2 min"),
        ("f300", "5 min"), ("f600", "10 min"), ("f1800", "30 min")]


def event_curves():
    s0, r0 = load()
    s, r = prep(s0, r0)
    g = eligible_periods(s)
    s = s.filter(pl.col("goal_no").is_in(g) & pl.col("eligible"))
    r = r.join(s.select("sid", "carried"), on="sid", how="inner").filter(pl.col("in_room"))
    r = r.filter(pl.col("a_label").is_null() | (pl.col("a_label") >= pl.col("a_seed") - 7200))
    d = r.filter(pl.col("a_label").is_not_null()).with_columns(((pl.col("a_label") - pl.col("a_seed")) // 900).cast(pl.Int32).alias("bin"))
    d = d.filter((pl.col("bin") >= -8) & (pl.col("bin") < 8))
    out = {}
    for lab, flt in (("new", ~pl.col("carried")), ("carried", pl.col("carried"))):
        c = d.filter(flt).group_by("bin").len()
        n = s.filter(flt).height
        m = dict(zip(c["bin"].to_list(), c["len"].to_list()))
        out[lab] = (np.arange(-8, 8), np.array([m.get(b, 0) for b in range(-8, 8)]) / n, n)
    return out


def panel_event(ax, ev):
    for lab, col in (("new", C1), ("carried", C2)):
        x, y, n = ev[lab]
        ax.step(x * 15 + 7.5, y, where="mid", color=col, lw=1.4, label=f"{'new' if lab == 'new' else 'carried-over'} projects (n={n})")
    ax.axvline(0, color=GR, lw=0.6)
    ax.set_xlabel("active minutes from the seed (first chat link)")
    ax.set_ylabel("adoptions per seed per 15 min")
    ax.legend(frameon=False, fontsize=6.5)
    ax.grid(axis="y", color="#e7e5df", lw=0.5)


def panel_grid(ax, d):
    xs, ys, los, his = [], [], [], []
    for i, (k, lab) in enumerate(GRID):
        v = d["grid"][f"{k}|u0|label"]["timely"]
        xs.append(i); ys.append(v["rr"]); los.append(v["lo"]); his.append(v["hi"])
    ys, los, his = map(np.array, (ys, los, his))
    ax.errorbar(xs, ys, yerr=[ys - los, his - ys], fmt="o", color=C1, ms=3.5, lw=1, capsize=0)
    ax.axhline(1, color=GR, lw=0.6); ax.axhline(1.5, color=C2, lw=0.6, ls="--")
    ax.text(8.4, 1.53, "P1 bar", fontsize=6, color="#52514e", ha="right")
    ax.set_xticks(xs); ax.set_xticklabels([lab for _, lab in GRID], rotation=40, ha="right", fontsize=6.5)
    ax.set_ylabel("RR$_{\\rm timely}$ (adopt within 60 min of read-out)")
    ax.set_xlabel("receptive window c")
    ax.grid(axis="y", color="#e7e5df", lw=0.5)


def panel_forest(ax, d):
    pp = d["P1_by_period"]
    rows = [(int(g), v["x_timely"]) for g, v in pp.items() if "x_timely" in v and v.get("n_adopt", 0) >= 15 and v["x_timely"]["se"] > 0.01]
    rows.sort()
    for i, (g, v) in enumerate(rows):
        col = C1 if v["lo"] > 1 else (C2 if v["hi"] < 1 else GR)
        ax.plot([v["lo"], v["hi"]], [i, i], color=col, lw=1)
        ax.plot(v["rr"], i, "o", color=col, ms=3)
    pv = d["P1"]["x_timely"]
    i = len(rows) + 0.8
    ax.plot([pv["lo"], pv["hi"]], [i, i], color="#0b0b0b", lw=1.5); ax.plot(pv["rr"], i, "D", color="#0b0b0b", ms=3.5)
    ax.set_yticks(list(range(len(rows))) + [i]); ax.set_yticklabels([f"G{g:02d}" for g, _ in rows] + ["pooled"], fontsize=6)
    ax.axvline(1, color=GR, lw=0.6); ax.set_xscale("log")
    ax.set_xlabel("RR$_{\\rm timely}$ (one cycle), 95% CI")
    ax.set_title("(c) per period (≥ 15 adoptions)", loc="left", fontsize=7.5)


def panel_g26(ax):
    t = pl.read_parquet(NAT / "g26_ballots_reads.parquet")
    g = json.loads((NAT / "g26.json").read_text())
    y0 = 0
    for rnd, col in (("runoff", C1), ("confirmatory", C3)):
        d = t.filter((pl.col("round") == rnd)).sort("t_read")
        seed = np.datetime64(g["rounds"][rnd]["seed_time"].replace("+00:00", ""))
        for i, r in enumerate(d.iter_rows(named=True)):
            yy = y0 + i
            if r["t_read"] is not None:
                tr = (np.datetime64(r["t_read"].replace(tzinfo=None)) - seed) / np.timedelta64(1, "s")
                ax.plot(tr, yy, "|", color=col, ms=6, mew=1.2)
            if r["t_ballot"] is not None and r["t_read"] is not None:
                tb = (np.datetime64(r["t_ballot"].replace(tzinfo=None)) - seed) / np.timedelta64(1, "s")
                ax.plot([tr, tb], [yy, yy], color=col, lw=0.6)
                ax.plot(tb, yy, "o", color=col, ms=3)
        if rnd == "runoff":
            ax.axvline(100.0, color=C1, lw=0.5, ls=":")
            ax.text(101, y0 + 0.2, "runoff closes", fontsize=5.5, color="#52514e")
        ax.text(118, y0 + len(d) - 1, rnd, va="center", ha="right", fontsize=6.5, color="#52514e")
        y0 += len(d) + 1.5
    ax.set_yticks([])
    ax.set_xlabel("seconds after the round's opening message")
    ax.set_title("(d) #26: read-out (|) → ballot (●) per voter", loc="left", fontsize=7.5)


def panel_auc(ax, d):
    keys = [("R", "receptive R"), ("U", "uncommitted U"), ("N_sus", "room size"), ("lstat", "poster status"), ("share", "current share"), ("tod", "time of day")]
    v = [d["P4"][k]["auc"] for k, _ in keys]
    ax.barh(range(len(keys)), v, color=[C1 if k == "R" else GR for k, _ in keys], height=0.6)
    ax.axvline(0.5, color="#0b0b0b", lw=0.6)
    ax.set_yticks(range(len(keys))); ax.set_yticklabels([lab for _, lab in keys], fontsize=6.5)
    ax.set_xlim(0.3, 0.8); ax.set_xlabel("AUC, herded vs never-herded seeds (within period)")
    ax.set_title(f"(e) placebo: {d['P4']['n_herded']} herded vs {d['P4']['n_never']} never", loc="left", fontsize=7.5)


def panel_cv(ax, d):
    keys = ["M_N", "M_U", "M_R", "M_status", "M_share", "M_tod", "M_full", "M_full+R"]
    base = d["P2_models"]["M0"]["cv_ll"]
    v = [d["P2_models"][k]["cv_ll"] - base for k in keys]
    ax.barh(range(len(keys)), v, color=[C1 if k == "M_R" else GR for k in keys], height=0.6)
    ax.axvline(0, color="#0b0b0b", lw=0.6)
    ax.set_yticks(range(len(keys))); ax.set_yticklabels(keys, fontsize=6.5)
    ax.set_xlabel("held-out log score vs M0 (nats, leave-one-day-out)")
    ax.set_title("(f) wave-size models (partial pooling)", loc="left", fontsize=7.5)


def main():
    d = json.loads((R1 / "round1.json").read_text())
    ev = event_curves()
    fig, axs = plt.subplots(3, 2, figsize=(7.2, 8.4))
    panel_event(axs[0, 0], ev); axs[0, 0].set_title("(a) adoptions around the seed (all eligible seeds)", loc="left", fontsize=7.5)
    panel_grid(axs[0, 1], d); axs[0, 1].set_title("(b) read-out timing effect across receptive windows", loc="left", fontsize=7.5)
    panel_forest(axs[1, 0], d)
    panel_g26(axs[1, 1])
    panel_auc(axs[2, 0], d)
    panel_cv(axs[2, 1], d)
    fig.tight_layout()
    fig.savefig(FIG / "round1_overview.pdf"); fig.savefig(FIG / "round1_overview.png", dpi=150)
    # page-1 figure: (a) event study, (b) RR grid
    fig, axs = plt.subplots(1, 2, figsize=(4.2, 2.0))
    for ax in axs:
        ax.tick_params(labelsize=6)
    panel_event(axs[0], ev)
    axs[0].set_xlabel("active min from seed", fontsize=6.5); axs[0].set_ylabel("adoptions/seed/15 min", fontsize=6.5)
    axs[0].legend(frameon=False, fontsize=5.3, loc="upper left")
    axs[0].set_title("(a) waves start at the link", loc="left", fontsize=7)
    panel_grid(axs[1], d)
    axs[1].set_ylabel("RR$_{\\rm timely}$", fontsize=6.5); axs[1].set_xlabel("receptive window", fontsize=6.5)
    axs[1].set_xticklabels([lab for _, lab in GRID], rotation=45, ha="right", fontsize=5.3)
    axs[1].set_title("(b) read-out timing: no effect", loc="left", fontsize=7)
    for t in axs[1].texts:
        t.set_fontsize(5)
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "summary_obs.pdf")
    print("written")


if __name__ == "__main__":
    main()
