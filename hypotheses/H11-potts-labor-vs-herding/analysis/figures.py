"""H11 figures: synthetic validation, per-period results, trajectories, one-page summary.

Usage: uv run python analysis/figures.py [--synthetic] [--real] [--summary]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h11common as HC  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import potts_core as P  # noqa: E402

# reference palette (dataviz skill, light mode; first three slots validate all-pairs)
C_AF, C_FM, C_NONE = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, NULLC = "#0b0b0b", "#52514e", "#e4e3df", "#9a9993"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "legend.frameon": False, "lines.linewidth": 2, "pdf.fonttype": 42})
SYN = HC.OUT / "synthetic"


def cls_color(c):
    return C_AF if c == "AF" else (C_FM if str(c).startswith("FM") else C_NONE)


# ------------------------------------------------------------------------------------------- synthetic


def synthetic_tables():
    s1 = pl.read_parquet(SYN / "S1_power.parquet")
    s1 = s1.with_columns(
        (pl.col("sig_cw") & (pl.col("bj_cw").sign() == pl.col("bj").sign())).alias("hit_cw"),
        (pl.col("sig_cw") & (pl.col("bj_cw").sign() != pl.col("bj").sign()) & (pl.col("bj") != 0)).alias("wrong_cw"),
        ((pl.col("z_shift").abs() > 1.96) & (pl.col("z_shift").sign() == pl.col("bj").sign())).alias("hit_pl"),
        ((pl.col("z_pday").abs() > 1.96) & (pl.col("z_pday").sign() == pl.col("bj").sign())).alias("hit_pld"),
        (pl.col("z_shift").abs() > 1.96).alias("sig_pl"), (pl.col("z_pday").abs() > 1.96).alias("sig_pld"))
    g = s1.group_by("bj", "N", "days", "p_obs", "sigma_h").agg(
        pl.len().alias("reps"), pl.col("bj_cw").mean().alias("bj_cw_mean"), pl.col("bj_cw").std().alias("bj_cw_sd"),
        pl.col("bj_pl").mean().alias("bj_pl_mean"), pl.col("bj_pl").std().alias("bj_pl_sd"),
        pl.col("hit_cw").mean().alias("pow_cw"), pl.col("sig_cw").mean().alias("sig_cw"), pl.col("wrong_cw").mean().alias("wrong_cw"),
        pl.col("hit_pl").mean().alias("pow_pl"), pl.col("sig_pl").mean().alias("sig_pl"),
        pl.col("hit_pld").mean().alias("pow_pld"), pl.col("sig_pld").mean().alias("sig_pld"),
        pl.col("z_shift").std().alias("z_shift_sd")).sort("N", "days", "p_obs", "sigma_h", "bj")
    s2 = pl.read_parquet(SYN / "S2_confounds.parquet")
    g2 = s2.group_by("conf", "sigma_h", "drift").agg(
        pl.len().alias("reps"), pl.col("bj_cw").mean().alias("bj_cw_mean"), pl.col("sig_cw").mean().alias("sig_cw"),
        (pl.col("sig_cw") & (pl.col("bj_cw") < 0)).mean().alias("sig_neg_cw"), (pl.col("sig_cw") & (pl.col("bj_cw") > 0)).mean().alias("sig_pos_cw"),
        pl.col("bj_pl").mean().alias("bj_pl_mean"), (pl.col("z_shift") > 1.96).mean().alias("pos_pl_N2"),
        (pl.col("z_shift") < -1.96).mean().alias("neg_pl_N2"), (pl.col("z_pday") > 1.96).mean().alias("pos_pl_N1d")).sort("conf", "sigma_h", "drift")
    s3 = pl.read_parquet(SYN / "S3_jumps.parquet")
    g3 = s3.group_by("kind", "bj").agg(
        pl.len().alias("reps"), (pl.col("verdict") == "jump").mean().alias("p_jump"), (pl.col("verdict") == "gradual").mean().alias("p_gradual"),
        (pl.col("verdict") == "none").mean().alias("p_none"), pl.col("tau").median().alias("tau_med"), pl.col("bj_cw").mean().alias("bj_cw_mean"),
        pl.col("mf_first_order").mean().alias("p_mf_first_order"),
        ((pl.col("verdict") == "jump") & pl.col("mf_first_order")).mean().alias("p_jump_and_mf")).sort("kind", "bj")
    s4 = pl.read_parquet(SYN / "S4_plm.parquet")
    g4 = s4.group_by("bj").agg(pl.len().alias("reps"), pl.col("d_obs").mean().alias("diag_mean"),
                               (pl.col("z") > 1.96).mean().alias("p_pos"), (pl.col("z") < -1.96).mean().alias("p_neg")).sort("bj")
    return g, g2, g3, g4


def fig_synthetic():
    g, g2, g3, g4 = synthetic_tables()
    fig, ax = plt.subplots(2, 3, figsize=(10, 6.2))
    # recovery (bias) panel: N=13, days=5, p=0.75
    for j, (sh, ls) in enumerate(((0.0, "-"), (1.0, "--"))):
        d = g.filter((pl.col("N") == 13) & (pl.col("days") == 5) & (pl.col("p_obs") == 0.75) & (pl.col("sigma_h") == sh))
        ax[0, 0].errorbar(d["bj"], d["bj_cw_mean"], d["bj_cw_sd"], color=C_FM, ls=ls, marker="o", ms=4, capsize=2,
                          label=f"βJ_CW (period fields), σ_h={sh:g}")
        ax[0, 0].errorbar(np.array(d["bj"]) + 0.12, d["bj_pl_mean"], d["bj_pl_sd"], color=C_AF, ls=ls, marker="s", ms=4, capsize=2,
                          label=f"βJ_PL (agent fields), σ_h={sh:g}")
    ax[0, 0].plot([-4, 4], [-4, 4], color=NULLC, lw=1)
    ax[0, 0].set(xlabel="true βJ", ylabel="estimate (mean ± sd)", title="S1 recovery: N=13, 5 d × 9 win, p_obs=0.75")
    ax[0, 0].legend(fontsize=6)
    # power panels
    for k, (stat, ttl) in enumerate((("pow_cw", "P1 rule: βJ_CW right sign & |t|>t_crit"), ("pow_pl", "P2 rule: βJ_PL right sign & |z_N2|>1.96"))):
        a = ax[0, 1 + k]
        for N, mk in ((7, "o"), (13, "s")):
            for days, ls in ((5, "-"), (10, ":")):
                d = g.filter((pl.col("N") == N) & (pl.col("days") == days) & (pl.col("p_obs") == 0.75) & (pl.col("sigma_h") == 0.0))
                y = np.where(np.array(d["bj"]) == 0, d["sig_cw" if stat == "pow_cw" else "sig_pl"], d[stat])
                a.plot(d["bj"], y, marker=mk, ms=4, ls=ls, color=C_FM if N == 13 else C_AF, label=f"N={N}, {days} d")
        a.axhline(0.05, color=NULLC, lw=1)
        a.set(xlabel="true βJ", ylabel="power (at βJ=0: false-positive rate)", title=ttl, ylim=(0, 1.02))
        a.legend(fontsize=6)
    # S2 confounds
    a = ax[1, 0]
    sp = g2.filter(pl.col("conf") == "specialization")
    a.plot(sp["sigma_h"], sp["bj_cw_mean"], marker="o", color=C_FM, label="βJ_CW, specialization σ_h")
    a.plot(sp["sigma_h"], sp["bj_pl_mean"], marker="s", color=C_AF, label="βJ_PL, specialization σ_h")
    dr = g2.filter(pl.col("conf") == "drift")
    a.plot(dr["drift"], dr["bj_cw_mean"], marker="o", ls="--", color=C_FM, label="βJ_CW, day drift amplitude")
    a.plot(dr["drift"], dr["bj_pl_mean"], marker="s", ls="--", color=C_AF, label="βJ_PL, day drift amplitude")
    a.axhline(0, color=NULLC, lw=1)
    a.set(xlabel="confound strength (true βJ = 0)", ylabel="mean estimate", title="S2 confounds at βJ = 0")
    a.legend(fontsize=6)
    # S3 jumps
    a = ax[1, 1]
    lab = [f"{k}\nβJ={b:g}" for k, b in zip(g3["kind"], g3["bj"])]
    x = np.arange(len(lab))
    a.bar(x - 0.2, g3["p_jump"], 0.38, color=C_FM, label="'jump' verdict")
    a.bar(x + 0.2, g3["p_jump_and_mf"], 0.38, color=C_AF, label="jump + MF first-order region")
    a.set_xticks(x, lab, fontsize=6)
    a.set(ylabel="fraction of runs", title="S3 jump detection (N=10, q=4, 5 d)", ylim=(0, 1.02))
    a.legend(fontsize=6)
    # S4 plm
    a = ax[1, 2]
    a.bar(np.arange(len(g4)) - 0.2, g4["p_pos"], 0.38, color=C_FM, label="z_N1 > 1.96")
    a.bar(np.arange(len(g4)) + 0.2, g4["p_neg"], 0.38, color=C_AF, label="z_N1 < −1.96")
    a.set_xticks(np.arange(len(g4)), [f"βJ={b:g}" for b in g4["bj"]])
    a.set(ylabel="fraction of runs", title="S4 plmDCA diagonal coupling (secondary)", ylim=(0, 1.02))
    a.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(HC.FIG / "synthetic_validation.pdf")
    plt.close(fig)
    return g, g2, g3, g4


# ------------------------------------------------------------------------------------------- real data


def load_round1():
    out = {}
    for f in sorted(HC.OUT.glob("G*/round1.json")):
        R = json.loads(f.read_text())
        out[R["goal"]] = R
    return out


def fig_periods(RR):
    rows = [R for R in RR.values() if R.get("tested")]
    order = sorted(rows, key=lambda R: (0 if R["cls"] == "AF" else 1 if str(R["cls"]).startswith("FM") else 2, R["goal"]))
    fig, ax = plt.subplots(1, 3, figsize=(10, 0.28 * len(order) + 1.4), sharey=True)
    y = np.arange(len(order))[::-1]
    for yi, R in zip(y, order):
        c = cls_color(R["cls"])
        o1 = R["O1"]
        ci = (o1["tcrit"] * o1["se"]) if o1["se"] else np.nan
        lo_, hi_ = o1["bj"] - ci, o1["bj"] + ci
        XL = (-20, 10)
        ax[0].plot([max(lo_, XL[0]), min(hi_, XL[1])], [yi, yi], color=c, lw=1.5)
        if lo_ < XL[0]:
            ax[0].plot(XL[0] + 0.3, yi, marker="<", color=c, ms=4)
        if hi_ > XL[1]:
            ax[0].plot(XL[1] - 0.3, yi, marker=">", color=c, ms=4)
        ax[0].plot(o1["bj"], yi, "o", color=c, ms=5)
        ax[0].plot(o1["N1_mean"], yi, marker="|", color=NULLC, ms=9, mew=2)
        ax[1].plot(R["O2"]["z_N2"], yi, "o", color=c, ms=5)
        ax[1].plot(R["O2"]["z_N1d"], yi, "x", color=c, ms=5)
        ax[2].plot(R["O6"]["bj_cw"], yi, "o", color=c, ms=5)
    for a in ax:
        a.axvline(0, color=NULLC, lw=1)
    ax[1].axvline(1.96, color=GRID, lw=1, ls="--")
    ax[1].axvline(-1.96, color=GRID, lw=1, ls="--")
    ax[0].set_yticks(y, [f"#{R['goal']} {R['cls']}" for R in order])
    ax[0].set(xlabel="βJ_CW (95% jackknife-t CI, clipped ◂ ▸); | = N1 mean", title="O1 primary: project-label βJ_CW", xlim=(-20, 10))
    ax[1].set(xlabel="z of βJ_PL vs N2 (o) and N1d (x)", title="O2 coupling beyond agent fields")
    ax[2].set(xlabel="action-class βJ_CW", title="O6 control: action class")
    from matplotlib.lines import Line2D
    ax[2].legend(handles=[Line2D([], [], marker="o", ls="", color=C_AF, label="AF predicted"),
                          Line2D([], [], marker="o", ls="", color=C_FM, label="FM predicted"),
                          Line2D([], [], marker="o", ls="", color=C_NONE, label="no prediction")], fontsize=6, loc="lower right")
    fig.tight_layout()
    fig.savefig(HC.FIG / "periods_forest.pdf")
    plt.close(fig)


def fig_trajectories(RR):
    gs = [g for g in (19, 26, 31, 40, 41, 13, 18) if g in RR and RR[g].get("tested")]
    n = len(gs) + (1 if 26 in RR and RR[26].get("votes") else 0)
    cols = 4
    rows = int(np.ceil(n / cols))
    fig, ax = plt.subplots(rows, cols, figsize=(10, 2.2 * rows), squeeze=False)
    k = 0

    def panel(a, t, kk, nn, j, title):
        t, kk, nn = map(np.asarray, (t, kk, nn))
        a.scatter(t, kk / np.maximum(nn, 1), s=np.clip(nn * 3, 4, 40), color=INK2, alpha=0.6, lw=0)
        if j and j.get("verdict") not in (None, "n/a"):
            tt = np.linspace(t.min(), t.max(), 300)
            z = 1 / (1 + np.exp(-(tt - j["t0"]) / max(j["tau"], 1e-3)))
            a.plot(tt, j["lo"] + (j["hi"] - j["lo"]) * z, color=C_FM)
            a.set_title(f"{title}\n{j['verdict']}: Δ={j['amp']:.2f}, τ={j['tau']:.1f} win", fontsize=7)
        a.set_ylim(-0.03, 1.03)
        a.set_xlabel("window (30 min, active time)")

    for g in gs:
        a = ax.flat[k]
        s = RR[g]["O45"]["series"]
        panel(a, s["t"], s["k"], s["n"], RR[g]["O45"], f"#{g} dominant-project share")
        k += 1
    if 26 in RR and RR[26].get("votes"):
        v = RR[26]["votes"]
        a = ax.flat[k]
        panel(a, v["series"]["t"], v["series"]["k"], v["series"]["n"], v["jump"], "#26 winner's declared-vote share")
        if v.get("onset_window") is not None:
            a.axvline(v["onset_window"], color=C_AF, lw=1, ls="--")
        k += 1
    for a in ax.flat[k:]:
        a.axis("off")
    ax.flat[0].set_ylabel("share x₁")
    fig.tight_layout()
    fig.savefig(HC.FIG / "dominant_share_trajectories.pdf")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--real", action="store_true")
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()
    if a.synthetic:
        g, g2, g3, g4 = fig_synthetic()
        pl.Config.set_tbl_rows(200)
        pl.Config.set_tbl_cols(30)
        pl.Config.set_tbl_width_chars(250)
        print(g.select("bj", "N", "days", "p_obs", "sigma_h", "bj_cw_mean", "bj_cw_sd", "bj_pl_mean", "bj_pl_sd", "pow_cw", "sig_cw",
                       "wrong_cw", "pow_pl", "sig_pl", "pow_pld", "sig_pld"))
        print(g2)
        print(g3)
        print(g4)
        g.write_parquet(SYN / "S1_summary.parquet")
    if a.real:
        RR = load_round1()
        fig_periods(RR)
        fig_trajectories(RR)
    if a.summary:
        summary_page()



def summary_page():
    """One-page summary PDF: headline, verdict table, key panels."""
    RR = load_round1()
    V = pl.read_parquet(HC.OUT / "verdicts_round1.parquet")
    X = json.loads((HC.OUT / "cross_period_round1.json").read_text())
    g1 = pl.read_parquet(SYN / "S1_summary.parquet")
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.05, 0.968, "H11 · Division of labor vs herding as the sign of a Potts coupling", fontsize=11, weight="bold", color=INK)
    fig.text(0.05, 0.953, "Exploratory round 1 · non-holdout goal periods · 2026-10-03", fontsize=8, color=INK2)
    head = ("Headline: the sign of the uniform-coupling (mean-field) Potts coupling does NOT follow the goal's mode. "
            "Project choice is ferromagnetic (βJ_CW > 0) in 11 of 14 tested weeks — including all five "
            "shared-objective 'divisible' weeks predicted to be antiferromagnetic (βJ_CW +2.0 … +5.0; coupling beyond agent "
            "fields z_N2 +2.1 … +8.7). Spread ('division of labor') appears only as static specialization in the three weeks where the goal "
            f"gave each agent its own artifact (#39 worlds, #42 channels, #40 worlds + hub). Sign test of the mode rule: {X['sign_correct']}/{X['sign_n']} correct "
            f"(p = {X['sign_p']:.2f}); AF<FM contrast p = {X['mw_af_lt_fm_bjcw_p']:.2f}. Consensus: the #26 runoff is an abrupt, persistent "
            "jump in declared votes (Δ = 0.62 within one 30-min window), but its mean-field coupling sits at the first-order threshold "
            "with a wide CI (βJ = 2.8 [0.65, 4.65] vs βJ_s = 2.75); #31 shows herding waves, not one consensus.")
    import textwrap
    fig.text(0.05, 0.938, "\n".join(textwrap.wrap(head, 140)), fontsize=7.2, va="top", color=INK)
    # panel A: forest of βJ_CW (clipped) and z_N2
    t = V.filter(pl.col("tested"))
    order = sorted(t.iter_rows(named=True), key=lambda r: (0 if r["cls"] == "AF" else 1 if r["cls"].startswith("FM") else 2, r["goal"]))
    axA = fig.add_axes([0.17, 0.50, 0.22, 0.30])
    axB = fig.add_axes([0.42, 0.50, 0.21, 0.30], sharey=axA)
    y = np.arange(len(order))[::-1]
    for yi, r in zip(y, order):
        c = cls_color(r["cls"])
        b = max(min(r["bj_cw"], 9.5), -9.5)
        axA.plot(b, yi, "o" if abs(r["bj_cw"]) < 9.5 else ("<" if r["bj_cw"] < 0 else ">"), color=c, ms=5)
        axB.plot(r["z_N2"], yi, "o", color=c, ms=5)
        axB.plot(r["z_loc1"], yi, "x", color=c, ms=5)
    for a in (axA, axB):
        a.axvline(0, color=NULLC, lw=1)
    axB.axvline(1.96, color=GRID, ls="--", lw=1)
    axA.set_yticks(y, [f"#{r['goal']} {r['cls']}" for r in order], fontsize=6.5)
    axA.set_xlim(-10, 10)
    axA.set_title("A  βJ_CW (primary; ◂ = clipped)", fontsize=7.5, loc="left")
    axB.set_title("B  βJ_PL: z vs N2 (o), ±1 win (x)", fontsize=7.5, loc="left")
    plt.setp(axB.get_yticklabels(), visible=False)
    # panel C: synthetic power
    axC = fig.add_axes([0.71, 0.50, 0.26, 0.30])
    for N, mk in ((7, "o"), (13, "s")):
        d = g1.filter((pl.col("N") == N) & (pl.col("days") == 5) & (pl.col("p_obs") == 0.75) & (pl.col("sigma_h") == 0.0))
        yv = np.where(np.array(d["bj"]) == 0, d["sig_cw"], d["pow_cw"])
        axC.plot(d["bj"], yv, marker=mk, ms=4, color=C_FM if N == 13 else C_AF, label=f"P1 rule, N={N}")
        yv2 = np.where(np.array(d["bj"]) == 0, d["sig_pl"], d["pow_pl"])
        axC.plot(d["bj"], yv2, marker=mk, ms=4, ls=":", color=C_FM if N == 13 else C_AF, label=f"P2 rule, N={N}")
    axC.axhline(0.05, color=NULLC, lw=1)
    axC.set(ylim=(0, 1), xlabel="true βJ (5 d × 9 win, p_obs 0.75)")
    axC.set_title("C  synthetic power (βJ=0: FPR)", fontsize=7.5, loc="left")
    axC.legend(fontsize=5.5)
    # panel D-F: trajectories
    def traj(ax, t_, k_, n_, j, title):
        t_, k_, n_ = map(np.asarray, (t_, k_, n_))
        ax.scatter(t_, k_ / np.maximum(n_, 1), s=np.clip(n_ * 2, 3, 30), color=INK2, alpha=0.6, lw=0)
        tt = np.linspace(t_.min(), t_.max(), 300)
        with np.errstate(over="ignore"):
            z = 1 / (1 + np.exp(-(tt - j["t0"]) / max(j["tau"], 1e-3)))
        ax.plot(tt, j["lo"] + (j["hi"] - j["lo"]) * z, color=C_FM)
        ax.set_ylim(-0.03, 1.03)
        ax.set_title(title, fontsize=7.5, loc="left")
        ax.set_xlabel("30-min window (active time)", fontsize=6.5)
    v = RR[26]["votes"]
    traj(fig.add_axes([0.07, 0.28, 0.26, 0.15]), v["series"]["t"], v["series"]["k"], v["series"]["n"], v["jump"],
         f"D  #26 winner's declared votes (Δ={v['jump']['amp']:.2f})")
    s31 = RR[31]["O45"]
    traj(fig.add_axes([0.39, 0.28, 0.26, 0.15]), s31["series"]["t"], s31["series"]["k"], s31["series"]["n"], s31,
         f"E  #31 final-day repo (Δ={s31['amp']:.2f}, relapse {s31['persistence_below_mid']:.2f})")
    s18 = RR[18]["O45"]
    traj(fig.add_axes([0.71, 0.28, 0.26, 0.15]), s18["series"]["t"], s18["series"]["k"], s18["series"]["n"], s18,
         "F  #18 (AF predicted): last day")
    # verdict table
    tbl = [("Prediction", "Outcome"),
           ("P1 sign of βJ_CW by mode (card level)", "MIXED by rule (4 supported, 2 failed, 1 n/a of 7); AF half fails 0/5"),
           ("P2 coupling beyond agent fields by mode", "FM: 5/6 z≥2; AF: 5/5 z≥+2 (opposite) → failed"),
           ("P3 first-order consensus (#19,#26,#31,#40)", "0/4 full passes; #26 votes: jump yes, MF at threshold"),
           ("P4 action class does not follow mode", "supported (contrast p = 1.0; no sig. negatives)"),
           ("P5 held-out gain where |z_N2|≥2", "8/10 periods"),
           ("P6 plmDCA agrees with βJ_PL", "agrees in sign (null absorbs no drift)"),
           ("P7 |βJ| < 2 everywhere (prior)", "failed for βJ_CW (12/14); within-day excess 0.4–3.4"),
           ("HH22 P-G26a / b / c", "uninformative pass / supported / inconclusive")]
    y0 = 0.205
    for i, (a_, b_) in enumerate(tbl):
        w = "bold" if i == 0 else "normal"
        fig.text(0.06, y0 - i * 0.016, a_, fontsize=7, weight=w, color=INK)
        fig.text(0.45, y0 - i * 0.016, b_, fontsize=7, weight=w, color=INK)
    foot = ("Data: strict artifact mentions (H07 tables), 30-min windows, room blocks; 14 non-holdout periods tested, 3 n/a. Estimators: exact finite-N "
            "Curie–Weiss Potts MLE (generating functions), agent-field pseudo-likelihood vs circular-shift null. Caveats: common within-day drive "
            "and coupling are not separable; specialization reads as AF in βJ_CW; per-period power ≈ 0.35 at |βJ| = 2. Holdout untouched; "
            "confirmatory targets #22, #28, #45 (script written, not run). Code: hypotheses/H11-potts-labor-vs-herding/analysis/.")
    fig.text(0.05, 0.045, "\n".join(textwrap.wrap(foot, 165)), fontsize=6.2, color=INK2, va="top")
    fig.savefig(HC.FIG / "H11_round1_summary.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
