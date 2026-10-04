"""H54 round-1 figures.

  uv run python hypotheses/H54-kickoff-quench-target/analysis/figures.py
Writes figures/summary_obs.pdf (P1 target identification + P2 naming), figures/summary_obs_b.pdf (G51 private goals +
NE38 re-quench), figures/remanence.pdf (HH182 / HH180), figures/synthetic_validation.pdf, and per-native-period figures.
"""
from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h54lib as L  # noqa: E402

FIG = L.HYP / "figures"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, BAND = "#0b0b0b", "#52514e", "#e6e5e0", "#d9d8d2"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "legend.frameon": False,
                     "font.family": "DejaVu Sans"})
FREEISH = {3, 5, 7, 11, 16, 31, 37, 44, 51}   # free / own-goal kickoffs (mode F, #44 #rest, #51 private)


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def panel_pi(ax):
    d = pl.read_parquet(L.OUT / "NE34" / "periods.parquet")
    syn = json.loads((L.OUT / "synthetic" / "results.json").read_text())["S1_S2"]
    ax.axhspan(0.05, 0.95, color=BAND, alpha=0.45, lw=0, zorder=0)
    ax.text(54.5, 0.62, "no-target\nnull 90%", fontsize=6, color=INK2, va="center", ha="right")
    for reg, col, lab in (("I", C1, "regime I"), ("III", C2, "regime II/III")):
        m = (d["regime"] == "I") if reg == "I" else (d["regime"] != "I")
        x = d.filter(m)
        for r in x.iter_rows(named=True):
            free = r["goal_no"] in FREEISH
            mk = "s" if r["top1"] == 1 else "o"
            ax.scatter(r["goal_no"], r["pi"], s=26, marker=mk, facecolor="white" if free else col, edgecolor=col, lw=1.1, zorder=3)
        ax.scatter([], [], s=26, color=col, label=lab)
    ax.scatter([], [], s=26, marker="s", color=INK2, label="own kickoff ranked first")
    ax.scatter([], [], s=26, facecolor="white", edgecolor=INK2, label="free / own-goal kickoff")
    for g in (3, 16, 44, 51):
        r = d.filter(pl.col("goal_no") == g).row(0, named=True)
        ax.annotate(f"#{g}", (g, r["pi"]), xytext=(4, -2), textcoords="offset points", fontsize=6.5, color=INK2)
    ax.set_ylim(-0.05, 1.08)
    ax.set_xlim(1, 56)
    ax.set_xlabel("goal period")
    ax.set_ylabel("own-kickoff percentile $\\pi_p$")
    ax.legend(loc="upper center", fontsize=6.0, ncol=2, handletextpad=0.3, columnspacing=0.9, bbox_to_anchor=(0.5, -0.25))
    ax.set_title("(a) day-1 centroid identifies its own kickoff", fontsize=7.5, loc="left")


def panel_naming(ax):
    pr = pl.read_parquet(L.OUT / "projects.parquet").filter(pl.col("src") == "H31")
    cls = [("kickoff_frozen", "frozen at\nkickoff"), ("instant", "instant\nwave"), ("gradual", "gradual"), ("none", "no\nconsensus")]
    x = np.arange(len(cls))
    w = 0.38
    base = pr["named_goal"].mean()
    for j, (c, lab) in enumerate(cls):
        s = pr.filter(pl.col("cls") == c)
        n = s.height
        a, b = s["named_goal"].mean(), s["pre_existing"].mean()
        ax.bar(j - w / 2 - 0.01, a, w, color=C1, edgecolor="white", lw=0.8)
        ax.bar(j + w / 2 + 0.01, b, w, color=C2, edgecolor="white", lw=0.8)
        ax.text(j - w / 2, a + 0.02, f"{int(round(a * n))}", ha="center", fontsize=6.3, color=INK)
        ax.text(j + w / 2, b + 0.02, f"{int(round(b * n))}", ha="center", fontsize=6.3, color=INK)
    ax.axhline(base, color=C1, lw=1, ls="--")
    ax.text(1.0, base + 0.015, "named: base rate", fontsize=6.3, color=INK2, ha="center")
    from matplotlib.patches import Patch
    hd = [Patch(color=C1, label="named by the goal text"), Patch(color=C2, label="pre-existing project (rival)")]
    ax.set_xticks(x, [f"{c[1]}\n(n = {pr.filter(pl.col('cls') == c[0]).height})" for c in cls], fontsize=6.5)
    ax.set_ylim(0, 0.85)
    ax.set_ylabel("share of H31 projects")
    ax.legend(handles=hd, loc="upper right", fontsize=6.5)
    ax.set_title("(b) frozen projects carry the goal's name", fontsize=7.5, loc="left")


def fig_summary():
    fig, axs = plt.subplots(2, 1, figsize=(3.6, 4.3), gridspec_kw={"height_ratios": [1.15, 1]})
    panel_pi(axs[0])
    panel_naming(axs[1])
    fig.tight_layout(h_pad=0.6)
    save(fig, "summary_obs")


def fig_natives():
    g51 = json.loads((L.OUT / "G51" / "native.json").read_text())
    syn = json.loads((L.OUT / "synthetic" / "results.json").read_text())["S4_g51"]["fp0.0_cg0.5"]
    fig, axs = plt.subplots(1, 2, figsize=(3.45, 1.75), gridspec_kw={"width_ratios": [1, 1.15]})
    ax = axs[0]
    wk = g51["weekly"]
    ax.axhspan(syn["acc_q05"], syn["acc_q95"], color=BAND, alpha=0.5, lw=0)
    ax.text(4, 0.5, "no private field", fontsize=5.6, color=INK2, ha="center", va="center")
    ax.plot([w["week"] + 1 for w in wk], [w["swap_accuracy"] for w in wk], color=C1, lw=1.6, marker="o", ms=3.5)
    ax.set_ylim(0.3, 1.02)
    ax.set_xlabel("week of #51 head", fontsize=6.5)
    ax.set_ylabel("role-swap accuracy", fontsize=6.5)
    ax.tick_params(labelsize=6)
    ax.set_title("(a) #51: own private goal", fontsize=6.8, loc="left")
    ax = axs[1]
    ne = g51["NE38"]
    me = pl.DataFrame(ne["series_opus5"]).group_by("pt_date").agg(pl.col("new").mean(), pl.col("old").mean()).sort("pt_date")
    ct = pl.DataFrame(ne["series_control"]).group_by("pt_date").agg(pl.col("new").mean()).sort("pt_date")
    import datetime as dt
    d0 = dt.date(2026, 7, 29)
    xm = [(dt.date.fromisoformat(x) - d0).days for x in me["pt_date"].to_list()]
    xc = [(dt.date.fromisoformat(x) - d0).days for x in ct["pt_date"].to_list()]
    ax.axvline(0, color=INK2, lw=0.8, ls=":")
    ax.plot(xm, me["new"], color=C1, lw=1.5, marker="o", ms=3, label="new (math) goal")
    ax.plot(xm, me["old"], color=C2, lw=1.5, marker="s", ms=3, label="old (game-dev) goal")
    ax.plot(xc, ct["new"], color=INK2, lw=1.0, ls="--", label="others vs new goal")
    ax.set_xlabel("days from reassignment (07-29)", fontsize=6.5)
    ax.set_ylabel("Opus 5 alignment", fontsize=6.5)
    ax.tick_params(labelsize=6)
    ax.text(xm[-1] + 0.3, float(me["new"][-1]), "new\ngoal", fontsize=5.4, color=C1, va="center")
    ax.text(xm[-1] + 0.3, float(me["old"][-1]) - 0.16, "old\ngoal", fontsize=5.4, color=C2, va="center")
    ax.text(xc[-1] + 0.3, float(ct["new"][-1]) + 0.17, "others,\nnew goal", fontsize=5.4, color=INK2, va="center")
    ax.set_xlim(-5.5, 12.5)
    ax.set_title("(b) NE38 re-quench", fontsize=6.8, loc="left")
    fig.tight_layout(w_pad=0.6)
    save(fig, "summary_obs_b")


def fig_remanence():
    R = pl.read_parquet(L.OUT / "NE34" / "remanence.parquet").with_columns(pl.col("ex_prev_kick").fill_nan(None))
    TR = pl.read_parquet(L.OUT / "NE34" / "human_traj.parquet")
    H = pl.read_parquet(L.OUT / "NE34" / "human.parquet")
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.3))
    ax = axs[0]
    q = R.filter(pl.col("day") <= 12).group_by("day").agg(pl.col("ex_kick").median().alias("m"), pl.col("ex_kick").quantile(0.25).alias("lo"),
                                                         pl.col("ex_kick").quantile(0.75).alias("hi"), pl.len()).sort("day")
    ax.fill_between(q["day"], q["lo"], q["hi"], color=C1, alpha=0.18, lw=0)
    ax.plot(q["day"], q["m"], color=C1, lw=1.8, marker="o", ms=3.5, label="kickoff excess (median, IQR)")
    qp = R.filter(pl.col("day") <= 12).group_by("day").agg(pl.col("ex_prev_kick").median().alias("m")).sort("day")
    ax.plot(qp["day"], qp["m"], color=C2, lw=1.3, ls="--", marker="s", ms=3, label="previous kickoff")
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set_xlabel("active day of the goal period")
    ax.set_ylabel("alignment excess over decoys")
    ax.legend(fontsize=6.5)
    ax.set_title("(a) kickoff remanence (HH182)", fontsize=8, loc="left")
    ax = axs[1]
    qq = TR.group_by("mid_h").agg(pl.col("ex").median().alias("m"), pl.col("ex").quantile(0.25).alias("lo"), pl.col("ex").quantile(0.75).alias("hi")).sort("mid_h")
    ax.fill_between(qq["mid_h"], qq["lo"], qq["hi"], color=C3, alpha=0.18, lw=0)
    ax.plot(qq["mid_h"], qq["m"], color=C3, lw=1.8, marker="o", ms=3.5, label=f"human message (n = {H.height})")
    per = pl.read_parquet(L.OUT / "NE34" / "periods.parquet")
    ax.axhline(float(per["jump"].median()), color=C1, lw=1.2, ls=":", label="kickoff day-1 jump (median)")
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set_xlabel("hours after the message")
    ax.set_ylabel("re-quench excess over decoys")
    ax.legend(fontsize=6.5)
    ax.set_title("(b) human messages: small, short pulses (HH180)", fontsize=8, loc="left")
    fig.tight_layout()
    save(fig, "remanence")


def fig_synthetic():
    syn = json.loads((L.OUT / "synthetic" / "results.json").read_text())["S1_S2"]
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.2))
    ax = axs[0]
    fs = [0.05, 0.15, 0.3]
    for ck, col in ((0.3, C2), (0.5, C1), (0.7, C3)):
        ax.plot(fs, [syn[f"H54_f{f}_ck{ck}_g0.5_J0.3"]["P1_pass_rate"] for f in fs], color=col, lw=1.8, marker="o", ms=3.5,
                label=f"text proxy fidelity {ck}")
    for key, lab, mk in (("R0_f0.15_ck0.5_g0.5_J0.3", "R0 no target", "x"), ("R1_f0.15_ck0.5_g0.5_J0.3", "R1 inertia", "+")):
        ax.scatter([0.15], [syn[key]["P1_pass_rate"]], color=INK, marker=mk, s=40, zorder=4, label=lab)
    ax.set_xlabel("day-1 target share f")
    ax.set_ylabel("P1 pass rate (200 runs)")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=6.3)
    ax.set_title("(a) target identification: power and calibration", fontsize=8, loc="left")
    ax = axs[1]
    s3 = json.loads((L.OUT / "synthetic" / "results.json").read_text())["S3"]
    labs = ["no naming\neffect", "naming\neffect", "naming x\nspecificity"]
    keys = ["T0_no_naming", "T1_naming", "T2_naming_x_spec"]
    x = np.arange(3)
    ax.bar(x - 0.27, [s3[k]["P2_pass_rate"] for k in keys], 0.26, color=C1, edgecolor="white", label="P2 pass")
    ax.bar(x, [s3[k]["period_frac_vs_spec_sig_rate"] for k in keys], 0.26, color=C2, edgecolor="white", label="per-period frozen fraction ~ spec.")
    ax.bar(x + 0.27, [s3[k]["per_project_spec_effect_sig_rate"] for k in keys], 0.26, color=C3, edgecolor="white", label="per-project spec. effect")
    ax.axhline(0.05, color=INK2, lw=0.8, ls=":")
    ax.set_xticks(x, labs, fontsize=7)
    ax.set_ylabel("rejection rate")
    ax.legend(fontsize=6.0, loc="upper left")
    ax.set_title("(b) naming layer: power and the counting artifact", fontsize=8, loc="left")
    fig.tight_layout()
    save(fig, "synthetic_validation")


def fig_g44_g38():
    for p in (44, 38):
        n = json.loads((L.OUT / f"G{p}" / "native.json").read_text())
        fig, ax = plt.subplots(figsize=(3.4, 2.0))
        for room, col, lab in (("2", C1, "#best"), ("3", C2, "#rest")):
            y = n["projections"][room]
            ax.scatter(y, np.full(len(y), 0 if room == "2" else 1) + np.random.default_rng(1).uniform(-0.12, 0.12, len(y)), color=col, s=22, label=lab)
        ax.set_yticks([0, 1], ["#best", "#rest"])
        ax.set_xlabel("day-1 position along $\\hat k_{best} - \\hat k_{rest}$")
        ax.set_title(f"#{p}: rooms on the room-kickoff axis", fontsize=8, loc="left")
        fig.tight_layout()
        out = L.HYP / "goalperiod-subhypotheses" / f"G{p}" / "figures"
        out.mkdir(parents=True, exist_ok=True)
        fig.savefig(out / "rooms_axis.pdf", bbox_inches="tight")
        plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    fig_summary()
    fig_natives()
    fig_remanence()
    fig_synthetic()
    fig_g44_g38()
    print("figures written")


def _late_main():
    fig_summary_compact()


if __name__ == "__main__":
    main()


def fig_summary_compact():
    """Column-width page figure (template limit: 1.7 in tall at column width)."""
    d = pl.read_parquet(L.OUT / "NE34" / "periods.parquet")
    pr = pl.read_parquet(L.OUT / "projects.parquet").filter(pl.col("src") == "H31")
    with plt.rc_context({"font.size": 6, "axes.titlesize": 6.3}):
        fig, axs = plt.subplots(1, 2, figsize=(3.5, 1.72), gridspec_kw={"width_ratios": [1.65, 1]})
        ax = axs[0]
        ax.axhspan(0.05, 0.95, color=BAND, alpha=0.45, lw=0, zorder=0)
        ax.text(30, 0.68, "no-target null 90%", fontsize=5, color=INK2, ha="center", va="center")
        for r in d.iter_rows(named=True):
            col = C1 if r["regime"] == "I" else C2
            free = r["goal_no"] in FREEISH
            ax.scatter(r["goal_no"], r["pi"], s=12, marker="s" if r["top1"] == 1 else "o",
                       facecolor="white" if free else col, edgecolor=col, lw=0.8, zorder=3)
        for g in (3, 16, 44, 51):
            rr = d.filter(pl.col("goal_no") == g).row(0, named=True)
            ax.annotate(f"#{g}", (g, rr["pi"]), xytext=(3, -1.5), textcoords="offset points", fontsize=5, color=INK2)
        ax.scatter([], [], s=12, color=C1, label="regime I")
        ax.scatter([], [], s=12, color=C2, label="II/III")
        ax.scatter([], [], s=12, facecolor="white", edgecolor=INK2, label="no shared target")
        ax.legend(fontsize=4.8, loc="lower left", bbox_to_anchor=(0.36, 0.03), handletextpad=0.1, borderaxespad=0.2, labelspacing=0.2)
        ax.set_ylim(-0.05, 1.07)
        ax.set_xlim(1, 56)
        ax.set_xlabel("goal period", labelpad=1)
        ax.set_ylabel("own-kickoff percentile", labelpad=1)
        ax.set_title("(a) target identified (squares: top-1)", loc="left")
        ax = axs[1]
        kf = pr.filter(pl.col("cls") == "kickoff_frozen")
        ot = pr.filter(pl.col("cls") != "kickoff_frozen")
        x = np.arange(2)
        a = [kf["named_goal"].mean(), ot["named_goal"].mean()]
        b = [kf["pre_existing"].mean(), ot["pre_existing"].mean()]
        ax.bar(x - 0.2, a, 0.38, color=C1, edgecolor="white", lw=0.6, label="goal-named")
        ax.bar(x + 0.2, b, 0.38, color=C2, edgecolor="white", lw=0.6, label="pre-existing")
        for xi, v, n in ((0 - 0.2, a[0], kf.height), (1 - 0.2, a[1], ot.height), (0 + 0.2, b[0], kf.height), (1 + 0.2, b[1], ot.height)):
            ax.text(xi, v + 0.02, f"{int(round(v * n))}", ha="center", fontsize=5, color=INK)
        ax.set_xticks(x, [f"frozen at\nkickoff (n={kf.height})", f"other\n(n={ot.height})"])
        ax.set_ylim(0, 0.9)
        ax.set_ylabel("share", labelpad=1)
        ax.legend(fontsize=4.8, loc="upper right", handlelength=1.0, borderaxespad=0.2)
        ax.set_title("(b) frozen projects", loc="left")
        fig.tight_layout(w_pad=0.4, pad=0.3)
        save(fig, "summary_obs_page")


if __name__ == "__main__":
    _late_main()
