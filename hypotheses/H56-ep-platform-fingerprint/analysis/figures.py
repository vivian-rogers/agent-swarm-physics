"""H56 figures (static PDFs for the RevTeX summary and the period folders).

Run after synthetic.py, event_study.py and native.py:
  OMP_NUM_THREADS=2 uv run python hypotheses/H56-ep-platform-fingerprint/analysis/figures.py
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
import h56lib as L  # noqa: E402

HYP = Path(__file__).resolve().parents[1]
FIG = HYP / "figures"
GP = HYP / "goalperiod-subhypotheses"
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4",
                                                          "#008300", "#4a3aa7", "#e34948")
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "font.family": "serif",
                     "axes.titlesize": 7.5, "axes.titlecolor": INK, "legend.frameon": False})
CLS_ORDER = ["scaffold_tool", "scaffold_prompt", "scaffold_family", "goal", "roster", "room", "operator",
             "operator_schedule", "goal_prompt"]
CLS_LABEL = {"scaffold_tool": "scaffold\ntool", "scaffold_prompt": "scaffold\nprompt", "scaffold_family": "scaffold\nfamily (DiD)",
             "goal": "goal\nkickoff", "roster": "roster", "room": "room", "operator": "operator", "operator_schedule": "hours",
             "goal_prompt": "goal\nprompt"}


def synthetic_fig():
    s = json.loads((L.DATA / "synthetic/summary.json").read_text())
    fine = s["fine"]["scen"]
    rows = [("null", "no change"), ("occ", "occupancy only"), ("occ_mix", "occ. + task mix"),
            ("count2", "2x transitions"), ("count05", "0.5x transitions"), ("roster", "3 newcomers"),
            ("single", "one agent x3"), ("aff_up25", "affinity +25%"), ("aff_up50", "affinity +50%"),
            ("aff_dn50", "affinity -50%")]
    fig, axes = plt.subplots(1, 2, figsize=(3.4, 2.05), gridspec_kw={"width_ratios": [3, 1.25]})
    ax = axes[0]
    y = np.arange(len(rows))[::-1]
    for k, (est, col, lab) in enumerate((("newton", BLUE, "Newton (primary)"), ("cfx", AQUA, "cfx"),
                                         ("plugin", ORANGE, "plug-in (matched)"))):
        ax.barh(y + (1 - k) * 0.26, [fine[r][est] for r, _ in rows], height=0.24, color=col, label=lab)
    ax.axvline(0.05, color=INK2, lw=0.7, ls="--")
    ax.axvline(0.10, color=MUTED, lw=0.5, ls=":")
    ax.set_yticks(y)
    ax.set_yticklabels([lb for _, lb in rows], fontsize=5.6)
    ax.set_xlabel("share of runs above the null 95th pct.")
    ax.set_xlim(0, 1)
    ax.set_title("(a) alarm rate, fine chain", loc="left")
    ax.legend(fontsize=5.3, loc="upper right", bbox_to_anchor=(1.0, 1.0))
    ax.grid(axis="x", color=GRID, lw=0.4)
    ax = axes[1]
    sc = fine["scaffold"]
    vals = [sc["with_scaffold"]["newton"], sc["agent_cut"]["newton"], 0.05]
    ax.bar([0, 1, 2], vals, color=[BLUE, ORANGE, AQUA], width=0.6)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=5.5, color=INK)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["with\nscaffold", "agent\ncut", "cut +\nburn-in"], fontsize=5.2)
    ax.set_ylim(0, 1.12)
    ax.axhline(0.05, color=INK2, lw=0.7, ls="--")
    ax.set_title("(b) resets x2", loc="left")
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "synthetic_validation.pdf")
    plt.close(fig)


def event_fig(variants=("act_all", "act_agent_b3")):
    es = pl.read_parquet(L.DATA / "replication/events.parquet")
    tday = pl.read_parquet(L.DATA / "replication/tday.parquet")
    fig, axes = plt.subplots(1, len(variants), figsize=(3.4, 2.1), sharey=True)
    for ax, v in zip(np.atleast_1d(axes), variants):
        e = es.filter((pl.col("variant") == v) & pl.col("newton_t").is_not_nan())
        all_t = np.abs(tday.filter(pl.col("variant") == v)["newton_t"].drop_nans().to_numpy())
        q95 = np.percentile(all_t, 95)
        ax.axhspan(0, q95, color="#f1f0ec", zorder=0)
        ax.axhline(q95, color=MUTED, lw=0.6, ls="--", zorder=1)
        rng = np.random.default_rng(1)
        for i, c in enumerate(CLS_ORDER):
            vv = e.filter(pl.col("cls") == c)
            if vv.height == 0:
                continue
            t = np.abs(vv["newton_t"].to_numpy())
            conf = vv["confounded"].to_numpy()
            x = i + rng.uniform(-0.18, 0.18, len(t))
            col = BLUE if c.startswith("scaffold") else "#9b9a95"
            ax.scatter(x[~conf], t[~conf], s=9, color=col, edgecolor="white", linewidth=0.4, zorder=3)
            ax.scatter(x[conf], t[conf], s=9, facecolor="white", edgecolor=col, linewidth=0.7, zorder=3)
            for xx, tt, rf in zip(x, t, vv["ref"].to_list()):
                if rf in ("NE14b", "NE43") or (rf == "CL:2026-04-20" and c == "scaffold_tool"):
                    ax.annotate({"CL:2026-04-20": "NE18/NE40"}.get(rf, rf), (xx, tt), xytext=(3, 0), textcoords="offset points",
                                fontsize=4.8, color=INK2, va="center")
        ax.set_ylim(0, 4.2)
        ax.text(len(CLS_ORDER) - 0.6, q95 + 0.08, "95% of all days", fontsize=4.8, color=INK2, ha="right")
        ax.set_xticks(range(len(CLS_ORDER)))
        ax.set_xticklabels([CLS_LABEL[c] for c in CLS_ORDER], fontsize=4.6, rotation=90)
        ax.set_title({"act_all": "(a) all records (V1)", "act_agent_b3": "(b) agent-only, burn-in (V5)",
                      "act_agent": "agent-only (V2)"}[v], loc="left")
        ax.grid(axis="y", color=GRID, lw=0.4)
    np.atleast_1d(axes)[0].set_ylabel("|t| of within-agent EP change")
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)


def daily_fig():
    dd = pl.read_parquet(L.DATA / "replication/daily.parquet")
    ev = pl.read_parquet(L.DATA / "event_catalog.parquet").filter(pl.col("cls").is_in(["scaffold_tool"]) & ~pl.col("holdout0").fill_null(True))
    fig, axes = plt.subplots(2, 1, figsize=(7.0, 3.0), sharex=True)
    import datetime as dt
    for ax, v, ttl in ((axes[0], "act_all", "V1 all records"), (axes[1], "act_agent_b3", "V5 agent-only chain, burn-in 3")):
        d = dd.filter((pl.col("variant") == v) & (pl.col("n_agents") >= 3)).sort("pt_date")
        x = [dt.date.fromisoformat(s) for s in d["pt_date"].to_list()]
        ax.scatter(x, d["ep"].to_numpy(), s=3, color=BLUE)
        for s in ev["day0"].to_list():
            ax.axvline(dt.date.fromisoformat(s), color=ORANGE, lw=0.4, alpha=0.6)
        ax.axvline(dt.date(2026, 3, 24), color=RED, lw=0.8)
        ax.set_ylabel("EP (nats/transition)")
        ax.set_title(ttl + " (mean over agents; n0 = 120 per agent-day; orange = scaffold-tool events; red = NE14b)", loc="left")
        ax.grid(color=GRID, lw=0.4)
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "daily_series.pdf")
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    which = sys.argv[1:] or ["synthetic", "events", "daily"]
    if "synthetic" in which:
        synthetic_fig()
    if "events" in which:
        event_fig()
    if "daily" in which:
        daily_fig()


def native_figs():
    import datetime as dt
    nat = L.DATA / "native"
    # NE14: per-agent pre/post
    r = json.loads((nat / "NE14.json").read_text())
    (GP / "NE14/figures").mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(3.4, 1.9))
    for ax, v, ttl in ((axes[0], "act_all", "fine, all records (V1)"), (axes[1], "coarse_all", "coarse, all records (V3)")):
        rows = r["variants"][v]["agents"]
        for x in rows:
            col = BLUE if x["post"] < x["pre"] else ORANGE
            ax.plot([0, 1], [x["pre"], x["post"]], color=col, lw=0.8, marker="o", ms=2.5)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["03-19..03-23\n(regime II)", "03-24..03-25\n(regime III)"], fontsize=5.5)
        ax.set_title(ttl, loc="left")
        ax.grid(axis="y", color=GRID, lw=0.4)
    axes[0].set_ylabel("EP (nats/transition)")
    fig.tight_layout(pad=0.3)
    fig.savefig(GP / "NE14/figures/ne14_agents.pdf")
    plt.close(fig)
    # NE43: Friday placebos
    r = json.loads((nat / "NE43.json").read_text())
    (GP / "NE43/figures").mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(3.4, 1.6))
    for i, (nm, v) in enumerate([("k3", "act_all"), ("k3", "act_agent_b3"), ("fri_only", "act_all"), ("k5", "act_all")]):
        d = r["designs"][nm][v]
        ax.scatter(np.full(len(d["placebo_t"]), i) + np.linspace(-0.12, 0.12, len(d["placebo_t"])), d["placebo_t"], s=8,
                   color="#9b9a95", zorder=2)
        ax.scatter([i], [d["t"]], s=22, color=RED, zorder=3, marker="D")
    ax.axhline(0, color=MUTED, lw=0.5)
    ax.set_xticks(range(4))
    ax.set_xticklabels(["3+3 days, V1", "3+3 days, V5", "Fri only, V1", "5+5 days, V1"], fontsize=5.6)
    ax.set_ylabel("t (within-agent EP change)")
    ax.set_title("08-21 (red) vs other #51 Fridays (grey)", loc="left")
    fig.tight_layout(pad=0.3)
    fig.savefig(GP / "NE43/figures/ne43_placebo.pdf")
    plt.close(fig)
    # NE40: stylometry
    r = json.loads((nat / "NE40.json").read_text())
    (GP / "NE40/figures").mkdir(parents=True, exist_ok=True)
    sty = pl.DataFrame(r["stylometric"]["daily"]).filter(pl.col("pt_date") >= "2026-02-01")
    x = [dt.date.fromisoformat(s) for s in sty["pt_date"].to_list()]
    fig, ax = plt.subplots(figsize=(3.4, 1.7))
    ax.plot(x, sty["star3"].to_numpy(), "o", ms=2.5, color=BLUE, label="answers with \"*   \" bullets")
    ax.plot(x, sty["dash"].to_numpy(), "s", ms=2.5, color=ORANGE, label="answers with \"- \" bullets")
    ax.axvline(dt.date(2026, 4, 20), color=RED, lw=0.8)
    ax.axvline(dt.date(2026, 3, 24), color=MUTED, lw=0.6, ls="--")
    ax.set_ylabel("share of answers per day")
    ax.legend(fontsize=5.5, loc="upper right")
    ax.set_title("history-search answers; red: 04-20 (NE18 deploy)", loc="left")
    fig.autofmt_xdate()
    fig.tight_layout(pad=0.3)
    fig.savefig(GP / "NE40/figures/ne40_stylometry.pdf")
    plt.close(fig)
    # G51: t(d)
    r = json.loads((nat / "G51.json").read_text())
    (GP / "G51/figures").mkdir(parents=True, exist_ok=True)
    tday = pl.read_parquet(L.DATA / "replication/tday.parquet").filter(pl.col("goal_no") == 51)
    ev = pl.read_parquet(L.DATA / "event_catalog.parquet").filter((pl.col("goal0") == 51) & pl.col("cls").is_in(["roster", "room", "operator"]))
    fig, ax = plt.subplots(figsize=(7.0, 1.9))
    for v, col, lab in (("act_all", BLUE, "V1 all records"), ("act_agent_b3", ORANGE, "V5 agent-only")):
        t = tday.filter(pl.col("variant") == v).sort("nidx")
        ax.plot([dt.date.fromisoformat(s) for s in t["pt_date"].to_list()], t["newton_t"].to_numpy(), "-o", ms=2, lw=0.8, color=col, label=lab)
    for s, c in zip(ev["day0"].to_list(), ev["cls"].to_list()):
        ax.axvline(dt.date.fromisoformat(s), color={"roster": "#9b9a95", "room": GREEN, "operator": RED}[c], lw=0.6)
    ax.axvline(dt.date(2026, 7, 29), color=VIOLET, lw=0.8, ls="--")
    ax.axhline(0, color=MUTED, lw=0.5)
    ax.set_ylabel("t (within-agent EP change)")
    ax.set_title("G51: grey roster joins, green room changes, red operator (NE38 07-29, NE43 08-21), violet dashed: search-tool schema change 07-29 (undocumented)", loc="left", fontsize=6)
    ax.legend(fontsize=5.5, loc="lower left", ncol=2)
    fig.tight_layout(pad=0.3)
    fig.savefig(GP / "G51/figures/g51_tday.pdf")
    plt.close(fig)


if __name__ == "__main__" and "native" in sys.argv[1:]:
    native_figs()
