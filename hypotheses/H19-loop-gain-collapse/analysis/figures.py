"""H19 figures: collapse plot, control-parameter scan, concordance, synthetic validation, mapping and dilution,
per-period residual panels, and the one-page summary PDF.

Usage: uv run python hypotheses/H19-loop-gain-collapse/analysis/figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h19common as C  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

FIG = C.HYP / "figures"
XP = "x_att_village"
# reference palette (dataviz skill): first three categorical slots validate all-pairs; regime by marker shape, not color
FAM = {"E": "#2a78d6", "T": "#eb6834"}
AQUA = "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
MARK = {"I": "o", "II": "s", "III": "^"}
ORDER = ["H19.geq_active", "H19.geq_talk", "H04.K_week", "H05.g2b_talk", "H05.g2b_active",
         "H03.n_talk", "H03.n_all", "H03.nx_fast", "H04.n_week"]
SHORT = {"H19.geq_active": "E1 g_eq active (H19)", "H19.geq_talk": "E2 g_eq talk (H19)", "H04.K_week": "E3 K weekly (H04)",
         "H05.g2b_talk": "E4 2-block g talk (H05)", "H05.g2b_active": "E5 2-block g active (H05)",
         "H03.n_talk": "T1 n̂ TALK (H03)", "H03.n_all": "T2 n̂ ALL (H03)", "H03.nx_fast": "T3 fast n_x (H03)",
         "H04.n_week": "T4 n weekly (H04)"}
DIV = LinearSegmentedColormap.from_list("div", ["#eb6834", "#f3f2ee", "#2a78d6"])

plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False, "lines.linewidth": 2})


def load():
    R = json.loads((C.OUT / "results/explore.json").read_text())
    est = pl.read_parquet(C.OUT / "estimates.parquet").filter(~pl.col("validation_only"))
    ctr = pl.read_parquet(C.OUT / "controls.parquet")
    d = est.join(ctr.select("goal_no", XP, "regime", "k_village", "N_roster"), on="goal_no")
    return R, d, ctr


def slope(R, m, model="x"):
    c = R["fits"][m][model]["coefs"]
    return c[0]["b"], c[1]["b"] if len(c) > 1 else 0.0


def collapse_overlay(ax, R, d, legend=True):
    """All methods z-scored (per-method mean and SD across periods) vs x_att, with each method's meta-regression line."""
    xs = np.linspace(d[XP].min(), d[XP].max(), 50)
    for m in ORDER:
        dm = d.filter(pl.col("method") == m)
        if dm.height == 0:
            continue
        y, s = dm["value"].to_numpy(), dm["se"].to_numpy()
        mu, sd = y.mean(), y.std()
        fam = dm["family"][0]
        for reg in ("I", "II", "III"):
            k = dm["regime"].to_numpy() == reg
            ax.errorbar(dm[XP].to_numpy()[k], (y[k] - mu) / sd, yerr=s[k] / sd, fmt=MARK[reg], ms=3.2, color=FAM[fam], alpha=0.45,
                        elinewidth=0.5, capsize=0, mec="white", mew=0.3)
        a, b = slope(R, m)
        ax.plot(xs, (a + b * xs - mu) / sd, color=FAM[fam], lw=1.2 if m not in R["P1"]["slopes"] or m not in ("H03.n_talk", "H19.geq_active") else 2.2,
                alpha=0.9)
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_xlabel("x_att = (N_room − 1) / (1 + k̄)   [attended partners per unit attention]")
    ax.set_ylabel("loop gain, z-scored within method")
    if legend:
        h = [Line2D([], [], color=FAM["E"], lw=2, label="equal-time gains (E1–E5)"),
             Line2D([], [], color=FAM["T"], lw=2, label="Hawkes triggering gains (T1–T4)")]
        h += [Line2D([], [], ls="", marker=MARK[r], color=INK2, ms=4, label=f"regime {r}") for r in ("I", "II", "III")]
        ax.legend(handles=h, loc="upper left", fontsize=6.5, ncol=1)


def fig_collapse(R, d):
    fig = plt.figure(figsize=(11, 7.2))
    gs = fig.add_gridspec(3, 5, wspace=0.6, hspace=0.6)
    ax0 = fig.add_subplot(gs[:, :2])
    collapse_overlay(ax0, R, d)
    ax0.set_title("Collapse test: per-method lines should share one sign", loc="left", fontsize=9, color=INK)
    for i, m in enumerate(ORDER):
        ax = fig.add_subplot(gs[i // 3, 2 + i % 3])
        dm = d.filter(pl.col("method") == m)
        fam = dm["family"][0]
        for reg in ("I", "II", "III"):
            k = dm["regime"].to_numpy() == reg
            ax.errorbar(dm[XP].to_numpy()[k], dm["value"].to_numpy()[k], yerr=dm["se"].to_numpy()[k], fmt=MARK[reg], ms=3.5,
                        color=FAM[fam], elinewidth=0.6, capsize=0, mec="white", mew=0.3)
        xs = np.linspace(dm[XP].min(), dm[XP].max(), 20)
        a, b = slope(R, m)
        ax.plot(xs, a + b * xs, color=INK, lw=1.4)
        c = R["P1"]["slopes"][m]
        ax.set_title(f"{SHORT[m]}\nslope {c['b']:+.2f} [{c['lo']:+.2f}, {c['hi']:+.2f}], R²het {R['P1']['r2_het'][m] or 0:.2f}",
                     fontsize=5.8, loc="left", color=INK)
        ax.tick_params(labelsize=6)
    fig.savefig(FIG / "fig1_collapse.pdf", bbox_inches="tight"); fig.savefig(FIG / "fig1_collapse.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_scan(R):
    sc = pl.read_parquet(C.OUT / "results/scan.parquet")
    joint = pl.DataFrame(R["scan_joint"])
    ctrls = joint["control"].to_list()
    M = np.full((len(ORDER), len(ctrls)), np.nan)
    for i, m in enumerate(ORDER):
        for j, x in enumerate(ctrls):
            r = sc.filter((pl.col("method") == m) & (pl.col("control") == x))
            if r.height:
                M[i, j] = r["delta_elpd_vs_const"][0] * np.sign(r["slope"][0])
    fig, ax = plt.subplots(figsize=(10, 4))
    lim = np.nanmax(np.abs(M))
    im = ax.imshow(M, cmap=DIV, vmin=-lim, vmax=lim, aspect="auto")
    ax.set_xticks(range(len(ctrls))); ax.set_xticklabels(ctrls, rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(ORDER))); ax.set_yticklabels([SHORT[m] for m in ORDER], fontsize=7)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if np.isfinite(M[i, j]):
                ax.text(j, i, f"{M[i, j]:+.1f}", ha="center", va="center", fontsize=5.5, color=INK)
    ax.grid(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.025)
    cb.set_label("ΔELPD (LOPO, vs constant) × sign(slope)", fontsize=7)
    ax.set_title("Control-parameter scan (exploratory). Blue: helps and positive slope; orange: helps with negative slope. "
                 "Columns ordered by joint ΔELPD.", loc="left", fontsize=8)
    fig.savefig(FIG / "fig2_scan.pdf", bbox_inches="tight"); fig.savefig(FIG / "fig2_scan.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_concordance(R):
    n = len(ORDER)
    M = np.full((n, n), np.nan); Nn = np.zeros((n, n), int)
    for k, v in {**R["P2"]["E"]["pairs"], **R["P2"]["T"]["pairs"], **R["cross_family_concordance"]}.items():
        a, b = k.split("|")
        if a in ORDER and b in ORDER:
            i, j = ORDER.index(a), ORDER.index(b)
            M[i, j] = M[j, i] = v["rho"]; Nn[i, j] = Nn[j, i] = v["n"]
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    im = ax.imshow(M, cmap=DIV, vmin=-1, vmax=1)
    for i in range(n):
        for j in range(n):
            if np.isfinite(M[i, j]):
                ax.text(j, i, f"{M[i, j]:+.2f}\n(n={Nn[i, j]})", ha="center", va="center", fontsize=5, color=INK)
    ax.set_xticks(range(n)); ax.set_xticklabels([SHORT[m].split(" ")[0] for m in ORDER], fontsize=7)
    ax.set_yticks(range(n)); ax.set_yticklabels([SHORT[m] for m in ORDER], fontsize=6.5)
    ax.axhline(4.5, color=INK, lw=1); ax.axvline(4.5, color=INK, lw=1); ax.grid(False)
    fig.colorbar(im, ax=ax, fraction=0.04).set_label("Spearman ρ across shared periods", fontsize=7)
    ax.set_title("Do methods agree on which periods have high loop gain? (pairs with ≥ 8 shared periods)", loc="left", fontsize=7.5)
    fig.savefig(FIG / "fig3_concordance.pdf", bbox_inches="tight"); fig.savefig(FIG / "fig3_concordance.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def synthetic_bars(ax):
    S = json.loads((C.OUT / "synthetic/summary.json").read_text())
    order = ["null", "collapse_R25", "collapse_R50", "collapse_R75", "scatter_sign", "scatter_control", "regime", "era", "logN"]
    lab = ["null", "collapse\nR²=.25", "collapse\nR²=.5", "collapse\nR²=.75", "opposite\nsigns", "different\ncontrols",
           "regime\nstep", "era\ntrend", "log N"]
    sup = np.array([S[t]["P_supported"] for t in order]); mix = np.array([S[t]["P_mixed"] for t in order])
    x = np.arange(len(order))
    ax.bar(x, sup, color=FAM["E"], width=0.7, label="supported", edgecolor="white", linewidth=1)
    ax.bar(x, mix, bottom=sup, color=AQUA, width=0.7, label="mixed", edgecolor="white", linewidth=1)
    for i in range(len(order)):
        ax.text(i, sup[i] + mix[i] + 0.02, f"{sup[i]:.2f}", ha="center", fontsize=6, color=INK)
    ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=6)
    ax.set_ylim(0, 1.1); ax.set_ylabel("share of synthetic data sets")
    ax.legend(fontsize=6.5, loc="upper right")
    return S


def fig_synthetic():
    fig, ax = plt.subplots(figsize=(7, 3))
    synthetic_bars(ax)
    ax.set_title("Synthetic validation (axis F): P1 verdicts on data simulated with the real design (periods, SEs, controls)",
                 loc="left", fontsize=8)
    fig.savefig(FIG / "fig4_synthetic.pdf", bbox_inches="tight"); fig.savefig(FIG / "fig4_synthetic.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_mapping(R):
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.4))
    p3 = R["P3"]["_points"]
    ax = axs[0]
    ax.scatter(p3["gmap075"], p3["geq_talk"], s=18, color=FAM["E"], edgecolor="white", linewidth=0.5)
    lim = max(max(p3["gmap075"]), max(p3["geq_talk"])) * 1.05
    ax.plot([0, lim], [0, lim], color=INK2, lw=1, ls="--")
    ax.set_xlabel("Hawkes-mapped equal-time gain ĝ_map (w = 0.75, H03 fast n_x, n_s)")
    ax.set_ylabel("measured g_eq, talk spins (H19)")
    ax.set_title(f"P3 mapping: ρ = {R['P3']['rho_geq_talk_vs_map']:+.2f}; g_eq ≥ ĝ_map(0.6) in {R['P3']['w0.6']['frac_geq_ge_map']:.0%}",
                 loc="left", fontsize=7.5)
    p4 = R["P4"]["_points"]
    for ax, key, f, lab in ((axs[1], "one_plus_k", R["P4"]["fit_k"], "1 + k̄ (agent messages waiting per turn)"),
                            (axs[2], "N_minus_1", R["P4"]["fit_N"], "N_active − 1")):
        x = np.array(p4[key]); y = np.array(p4["n_pair"]); s = np.array(p4["se"])
        ax.errorbar(x, y, yerr=s, fmt="o", ms=3.5, color=FAM["T"], elinewidth=0.5, mec="white", mew=0.3)
        xs = np.linspace(x.min(), x.max(), 50)
        ax.plot(xs, f["A"] * xs ** (-f["alpha"]), color=INK, lw=1.4)
        ax.set_xscale("log"); ax.set_yscale("symlog", linthresh=1e-3)
        ax.set_xlabel(lab); ax.set_ylabel("per-pair fast n_x (H03)")
        ax.set_title(f"P4: exponent {f['alpha']:.2f} [{f['lo']:.2f}, {f['hi']:.2f}]", loc="left", fontsize=7.5)
    axs[1].text(0.02, 0.04, f"ΔELPD(k̄ − N) = {R['P4']['elpd_k_minus_N']['delta']:+.1f} ± {R['P4']['elpd_k_minus_N']['se']:.1f}",
                transform=axs[1].transAxes, fontsize=6.5, color=INK2)
    fig.tight_layout()
    fig.savefig(FIG / "fig5_mapping_dilution.pdf", bbox_inches="tight"); fig.savefig(FIG / "fig5_mapping_dilution.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_periods(R):
    pq = pl.read_parquet(C.OUT / "results/per_period.parquet")
    for (P,), d in pq.group_by(["period"]):
        d = d.with_columns(pl.col("method").replace_strict({m: i for i, m in enumerate(ORDER)}, default=99).alias("o")).sort("o")
        fig, ax = plt.subplots(figsize=(5.2, 0.32 * d.height + 0.9))
        for i, r in enumerate(d.iter_rows(named=True)):
            fam = "E" if r["method"] in ORDER[:5] else "T"
            if r["mu"] is not None:
                ax.plot([r["lo90"], r["hi90"]], [i, i], color=GRID, lw=6, solid_capstyle="round")
                ax.plot([r["mu"]], [i], "|", color=INK2, ms=10, mew=1.5)
            if r["mu_regime"] is not None:
                ax.plot([r["mu_regime"]], [i], "x", color=INK2, ms=5, mew=1)
            ax.errorbar([r["y"]], [i], xerr=[r["s"]], fmt="o", ms=4.5, color=FAM[fam], elinewidth=1, mec="white", mew=0.4)
        ax.set_yticks(range(d.height)); ax.set_yticklabels([SHORT.get(m, m) for m in d["method"]], fontsize=6.5)
        ax.invert_yaxis(); ax.set_xlabel("loop gain")
        ax.set_title(f"H19 × {P}: own estimate ± SE (dot) vs LOPO collapse prediction | with 90% PI (bar); × regime-only rival",
                     loc="left", fontsize=6.5)
        out = C.HYP / P / "figures"
        out.mkdir(parents=True, exist_ok=True)
        fig.savefig(out / f"{P}_residuals.png", dpi=130, bbox_inches="tight")
        plt.close(fig)


def fig_posthoc(R, d):
    """POST HOC: channel split. Talk-channel gains vs k_llm; activity-channel gains vs x_att (z-scored within method)."""
    ctr = pl.read_parquet(C.OUT / "controls.parquet").select("goal_no", "k_llm")
    d = d.join(ctr, on="goal_no")
    H = json.loads((C.OUT / "results/posthoc_channels.json").read_text())
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
    for ax, ch, ms, x, col in ((axs[0], "talk", ["H03.n_talk", "H03.n_all", "H03.nx_fast", "H04.n_week", "H19.geq_talk"], "k_llm", FAM["T"]),
                               (axs[1], "activity", ["H19.geq_active", "H04.K_week", "H05.g2b_active"], XP, FAM["E"])):
        for m in ms:
            dm = d.filter(pl.col("method") == m)
            y, s = dm["value"].to_numpy(), dm["se"].to_numpy(); mu, sd = y.mean(), y.std()
            for reg in ("I", "II", "III"):
                k = dm["regime"].to_numpy() == reg
                ax.errorbar(dm[x].to_numpy()[k], (y[k] - mu) / sd, yerr=s[k] / sd, fmt=MARK[reg], ms=3.2, color=col, alpha=0.45,
                            elinewidth=0.5, mec="white", mew=0.3)
            sl = H[ch][x]["slopes"][m]["b"]
            xs = np.linspace(dm[x].min(), dm[x].max(), 20)
            ax.plot(xs, sl * (xs - dm[x].to_numpy().mean()) / sd, color=col, lw=1.2)
        r = H[ch][x]
        ax.set_title(f"{ch} channel vs {x}: {r['n_sig_same_sign']}/{len(ms)} same-sign significant; "
                     f"ΔELPD vs regime-only {r['x_minus_regime']:+.1f}", loc="left", fontsize=7.5)
        ax.set_xlabel({"k_llm": "k_llm = agent messages delivered per LLM step (attention load per model call)", XP: "x_att (village turns)"}[x])
        ax.set_ylabel("loop gain, z-scored within method"); ax.axhline(0, color=INK2, lw=0.6)
    fig.suptitle("POST HOC (not pre-registered): methods split by spin channel, not by the card's E/T families", x=0.01, ha="left", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(FIG / "fig6_posthoc_channels.pdf", bbox_inches="tight"); fig.savefig(FIG / "fig6_posthoc_channels.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def summary_pdf(R, d):
    fig = plt.figure(figsize=(8.5, 11))
    gs = fig.add_gridspec(4, 2, height_ratios=[0.55, 2.1, 1.25, 1.35], hspace=0.55, wspace=0.3)
    ax = fig.add_subplot(gs[0, :]); ax.axis("off")
    P1 = R["P1"]
    ax.text(0, 0.95, "H19 · One curve for all periods? Loop-gain data collapse across 35 goal periods (exploratory round 1)",
            fontsize=10.5, weight="bold", color=INK, va="top")
    ax.text(0, 0.55, R.get("_headline", ""), fontsize=8, color=INK, va="top", wrap=True)
    ax1 = fig.add_subplot(gs[1, :])
    collapse_overlay(ax1, R, d)
    ax1.set_title("Collapse plot: every method z-scored, with its own meta-regression line on x_att (bold = primaries T1, E1)",
                  loc="left", fontsize=8.5)
    ax2 = fig.add_subplot(gs[2, 0]); ax2.axis("off")
    rows = [["Prediction", "Outcome"]]
    for k, lab in (("P1", "P1 collapse on x_att"), ("P2E", "P2 concordance, equal-time"), ("P2T", "P2 concordance, Hawkes"),
                   ("P3", "P3 cross-family mapping"), ("P4", "P4 dilution exponent"), ("P5", "P5 no mode effect")):
        v = {"P1": P1["verdict"], "P2E": R["P2"]["E"]["verdict"], "P2T": R["P2"]["T"]["verdict"], "P3": R["P3"]["verdict"],
             "P4": R["P4"]["verdict"], "P5": R["P5"]["verdict"]}[k]
        rows.append([lab, v])
    t = ax2.table(cellText=rows, loc="upper left", cellLoc="left", colWidths=[0.7, 0.3])
    t.auto_set_font_size(False); t.set_fontsize(7.5); t.scale(1, 1.35)
    for (i, j), c in t.get_celld().items():
        c.set_edgecolor(GRID)
        if i == 0:
            c.set_text_props(weight="bold")
    ax2.set_title("Outcome vs. prediction", loc="left", fontsize=8.5)
    ax3 = fig.add_subplot(gs[2, 1])
    el = P1["elpd_x_minus_rival"]
    names = ["const", "regime", "era", "logN"]
    vals = [el[k] for k in names]
    ax3.barh(range(4), vals, color=[FAM["E"] if v > 0 else FAM["T"] for v in vals], height=0.6)
    ax3.axvline(0, color=INK2, lw=0.8); ax3.axvline(2, color=INK2, lw=0.6, ls=":")
    ax3.set_yticks(range(4)); ax3.set_yticklabels(["N0 constant", "N1 regime step", "N2 era trend", "N3 log N"], fontsize=7)
    for i, v in enumerate(vals):
        ax3.text(v, i, f" {v:+.1f}", va="center", fontsize=7, color=INK)
    ax3.set_xlabel("ΔELPD, collapse − rival (nats, LOPO, summed over methods)")
    ax3.set_title("Collapse model vs. rivals (> 2 needed)", loc="left", fontsize=8.5)
    ax4 = fig.add_subplot(gs[3, :])
    synthetic_bars(ax4)
    ax4.set_title("Synthetic validation: share of data sets the P1 rule calls supported / mixed, by true generating model",
                  loc="left", fontsize=8.5)
    fig.savefig(FIG / "summary.pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    R, d, ctr = load()
    fig_collapse(R, d); fig_scan(R); fig_concordance(R); fig_synthetic(); fig_mapping(R); fig_periods(R); fig_posthoc(R, d)
    hl = Path(C.OUT / "results/headline.txt")
    R["_headline"] = hl.read_text() if hl.exists() else ""
    summary_pdf(R, d)
    print("figures written to", FIG)


if __name__ == "__main__":
    main()
