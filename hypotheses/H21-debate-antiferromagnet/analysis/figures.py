"""H21 figures from saved results (no recomputation).

Writes
  goalperiod-subhypotheses/G12/figures/g12_partitions.pdf   per-debate Delta for every partition, the true split highlighted
  goalperiod-subhypotheses/G12/figures/g12_robustness.pdf   pooled Delta under every variant / confound check, with null 95% bands
  goalperiod-subhypotheses/G12/figures/g12_verdict.pdf      sigma(tau) around the verdict, winners vs losers; judge check
  goalperiod-subhypotheses/G12/figures/g12_fluct.pdf        sublattice fluctuations dm_A vs dm_B (staggered susceptibility)
  figures/summary_obs.pdf          4.3 x 2.6 in, for the one-page hypothesis summary
  figures/summary.pdf              one-page results summary (all panels)
Usage: uv run python hypotheses/H21-debate-antiferromagnet/analysis/figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H21-debate-antiferromagnet"
GF = HERE.parent / "goalperiod-subhypotheses/G12/figures"
FF = HERE.parent / "figures"
BLUE, ORANGE, AQUA, INK, INK2, GRID, NULL = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e4e3df", "#b9b8b2"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 8.5, "axes.titleweight": "bold", "legend.frameon": False, "pdf.fonttype": 42})


def load_posthoc():
    f = DATA / "G12/results_posthoc.json"
    return json.loads(f.read_text()) if f.exists() else None


def panel_text_phase(ax, P, R=None):
    """Gov-minus-Opp projection on the a-priori motion stance axis (support minus oppose templates), by phase."""
    if not P:
        return
    ph = {"pre": P["Q6_text_axis_by_phase"]["pre"], "deb": P["Q5_text_axis_statement_level"], "post": P["Q6_text_axis_by_phase"]["post"]}
    debs = sorted({int(d) for v in ph.values() for d in v["per_debate"]})
    xs = {"pre": 0, "deb": 1, "post": 2}
    for d in debs:
        pts = [(xs[k], v["per_debate"].get(str(d), v["per_debate"].get(d))) for k, v in ph.items()]
        pts = [(x, y) for x, y in pts if y is not None]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=GRID, lw=0.8, zorder=1)
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=9, color=NULL, zorder=2, lw=0)
    means = [ph[k]["gov_minus_opp_projection"] for k in ("pre", "deb", "post")]
    cols = [INK2, BLUE, ORANGE]
    for k, (x, m) in enumerate(zip(range(3), means)):
        ax.scatter([x], [m], s=46, color=cols[k], zorder=3, edgecolor="white", lw=0.8)
    ax.plot(range(3), means, color=INK2, lw=1.2, zorder=2)
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_xticks(range(3), ["pre\n(sides known)", "debate", "post-verdict\n(≤10 min)"])
    ax.set_ylabel("Gov − Opp projection on\nmotion stance axis (whitened)")
    d5, p6 = P["Q5_text_axis_statement_level"], P["Q6_text_axis_by_phase"]["post"]
    ax.set_title(f"Along the motion's a-priori stance axis: debate +{d5['gov_minus_opp_projection']:.2f} "
                 f"(p={d5['p']:.1g}, {d5['positive_debates']}/{d5['n_debates']}); post {p6['gov_minus_opp_projection']:+.2f}", loc="left")


def panel_topic(ax, P):
    if not P:
        return
    q = P["Q4_topic_field"]["Mu_topic_mean"]
    ax.bar(range(3), [q["pre"], q["deb"], q["post"]], color=[NULL, AQUA, NULL], width=0.6)
    ax.set_xticks(range(3), ["pre", "debate", "post"])
    ax.set_ylabel("uniform M_u · ĝ (topic)")
    ax.set_title("Uniform order along the motion topic", loc="left")


def load():
    R = json.loads((DATA / "G12/results.json").read_text())
    tc = pl.read_csv(DATA / "G12/time_course.csv") if (DATA / "G12/time_course.csv").exists() else None
    syn = json.loads((DATA / "synthetic/synthetic.json").read_text()) if (DATA / "synthetic/synthetic.json").exists() else None
    return R, tc, syn


def panel_partitions(ax, R):
    per = R["static"]["per_debate"]
    rng = np.random.default_rng(0)
    for k, p in enumerate(per):
        allv = np.array(p["delta_all"])
        others = np.delete(allv, p["true_idx"])
        ax.scatter(np.full(len(others), k) + rng.uniform(-0.15, 0.15, len(others)), others, s=9, color=NULL, zorder=2, lw=0)
        ax.scatter([k], [p["delta"]], s=34, color=BLUE if p["recovered"] else ORANGE, zorder=3, edgecolor="white", lw=0.8)
    ax.axhline(0, color=GRID, lw=0.8, zorder=1)
    ax.set_xticks(range(len(per)), [str(p["debate"]) for p in per])
    ax.set_xlabel("debate")
    ax.set_ylabel("Δ = cos(within) − cos(cross)")
    s = R["static"]
    ax.set_title(f"True split vs all other splits: recovered {s['recovered']}/{s['n_debates']} "
                 f"(chance {s['recovered_expected_null']:.1f}), p = {s['p_recovered']:.1g}", loc="left")
    ax.scatter([], [], s=34, color=BLUE, label="true split, ranked 1st")
    ax.scatter([], [], s=34, color=ORANGE, label="true split, not 1st")
    ax.scatter([], [], s=9, color=NULL, label="other splits (null)")
    ax.legend(loc="upper right", fontsize=6.5)


def robustness_rows(R):
    rows = [("main (masked, D=32)", R["static"])]
    rb = R.get("robustness", {})
    for k, lab in (("unmasked", "unmasked"), ("dim16", "D = 16"), ("dim64", "D = 64"),
                   ("length_weighted", "length-weighted means"), ("min_n1", "min 1 statement"), ("min_n3", "min 3 statements"),
                   ("drop_debate7", "drop #7 (= #6 teams)")):
        if k in rb:
            rows.append((lab, rb[k]["static"]))
    g = R.get("generic", {}).get("specific")
    if g:
        rows.append(("generic axis projected out", g))
    f = R.get("family", {})
    if "no_agent_centre" in f:
        rows.append(("no agent-centring", f["no_agent_centre"]))
    if "lab_partition_placebo_centred" in f:
        rows.append(("PLACEBO: labs (centred)", f["lab_partition_placebo_centred"]))
    if "lab_partition_placebo_uncentred" in f:
        rows.append(("PLACEBO: labs (uncentred)", f["lab_partition_placebo_uncentred"]))
    for ph in ("pre", "post"):
        if ph in R.get("phases", {}) and R["phases"][ph].get("n_debates"):
            rows.append((f"{ph} phase", R["phases"][ph]))
    return rows


def panel_robustness(ax, R):
    rows = robustness_rows(R)
    y = np.arange(len(rows))[::-1]
    for yy, (lab, s) in zip(y, rows):
        q95 = s.get("delta_null_q95", np.nan)
        ax.plot([s.get("delta_null_mean", 0), q95], [yy, yy], color=NULL, lw=5, solid_capstyle="round", zorder=1)
        col = ORANGE if lab.startswith("PLACEBO") else BLUE
        ax.scatter([s["delta"]], [yy], color=col, s=22, zorder=3, edgecolor="white", lw=0.6)
        ax.text(s["delta"] + 0.01, yy, f"p={s['p_delta']:.1g}", va="center", fontsize=6, color=INK2)
    ax.set_yticks(y, [r[0] for r in rows], fontsize=6.5)
    ax.axvline(0, color=GRID, lw=0.8)
    ax.set_xlabel("pooled Δ̄ (gray: null mean → 95th pct)")
    ax.set_title("Robustness and confound checks", loc="left")


def panel_verdict(ax, tc, R):
    if tc is None or tc.height == 0:
        return
    d = tc.with_columns((pl.col("bin") / 60).alias("tau_min"))
    for side, col, lab in ((1, BLUE, "winners"), (-1, ORANGE, "losers")):
        g = d.filter(pl.col("winner_side") == side).group_by("tau_min").agg(
            pl.col("sigma").mean().alias("m"), (pl.col("sigma").std() / pl.len().sqrt()).alias("se"), pl.len().alias("n")).sort("tau_min")
        g = g.filter(pl.col("n") >= 3)
        x, m, se = g["tau_min"].to_numpy(), g["m"].to_numpy(), g["se"].fill_null(0).to_numpy()
        ax.fill_between(x, m - se, m + se, color=col, alpha=0.15, lw=0)
        ax.plot(x, m, color=col, lw=2, marker="o", ms=3, label=lab)
    ax.axvline(0, color=INK2, lw=0.8, ls="--")
    ax.axhline(0, color=GRID, lw=0.8)
    ax.text(0.2, ax.get_ylim()[1] * 0.92 if ax.get_ylim()[1] > 0 else 0.1, "verdict", fontsize=6.5, color=INK2)
    v = R.get("verdict", {})
    ax.set_title(f"Staggered order around the verdict: remanence R = {v.get('remanence', np.nan):.2f}", loc="left")
    ax.set_xlabel("minutes from verdict (5-min bins)")
    ax.set_ylabel("σ = ε_i s_i·â_{−i}  (LOAO)")
    ax.legend(fontsize=6.5, loc="upper right")


def panel_fluct(ax, R):
    f = R.get("fluct", {})
    ser = f.get("series", [])
    if not ser:
        return
    for a, b in ser:
        a, b = np.array(a), np.array(b)
        ax.scatter(a - a.mean(), b - b.mean(), s=10, color=AQUA, alpha=0.8, lw=0)
    ax.axhline(0, color=GRID, lw=0.8); ax.axvline(0, color=GRID, lw=0.8)
    ax.set_xlabel("δm_Gov (3-min bin, along debate axis)")
    ax.set_ylabel("δm_Opp")
    ax.set_title(f"Sublattice fluctuations: ρ = {f.get('rho', np.nan):.2f} (p_neg = {f.get('p_rho_neg', np.nan):.2f}), "
                 f"χ_s/χ_u = {f.get('chi_ratio', np.nan):.2f}", loc="left")


def panel_synth(ax, syn):
    if not syn:
        return
    E1 = syn["E1_power"]; E6 = syn.get("E6_semisynthetic", [])
    ax.plot([e["mu"] for e in E1], [e["power_delta"] for e in E1], "o-", color=BLUE, lw=2, ms=4, label="Δ̄, Gaussian noise")
    ax.plot([e["mu"] for e in E1], [e["power_recovery"] for e in E1], "o--", color=BLUE, lw=1.2, ms=3, label="recovery, Gaussian")
    if E6:
        ax.plot([e["mu"] for e in E6], [e["power_delta"] for e in E6], "s-", color=AQUA, lw=2, ms=4, label="Δ̄, real #12 noise")
        ax.plot([e["mu"] for e in E6], [e["power_recovery"] for e in E6], "s--", color=AQUA, lw=1.2, ms=3, label="recovery, real noise")
    ax.axhline(0.05, color=GRID, lw=0.8)
    ax.set_xlabel("injected staggered field μ (whitened units)")
    ax.set_ylabel("power (α = 0.05)")
    ax.set_title("Synthetic validation at G12's design", loc="left")
    ax.legend(fontsize=6, loc="lower right")


def main():
    GF.mkdir(parents=True, exist_ok=True); FF.mkdir(parents=True, exist_ok=True)
    R, tc, syn = load()
    P = load_posthoc()
    for name, fn, size in (("g12_partitions", lambda ax: panel_partitions(ax, R), (6, 3)),
                           ("g12_robustness", lambda ax: panel_robustness(ax, R), (5.5, 4.2)),
                           ("g12_verdict", lambda ax: panel_verdict(ax, tc, R), (5, 3)),
                           ("g12_fluct", lambda ax: panel_fluct(ax, R), (4.5, 3.2))):
        fig, ax = plt.subplots(figsize=size)
        fn(ax)
        fig.tight_layout(); fig.savefig(GF / f"{name}.pdf"); plt.close(fig)
    fig, ax = plt.subplots(figsize=(5, 3.2)); panel_text_phase(ax, P); fig.tight_layout(); fig.savefig(GF / "g12_text_axis_phases.pdf"); plt.close(fig)
    # summary_obs: (a) full-vector test (null), (b) stance axis by phase
    fig, ax = plt.subplots(1, 2, figsize=(4.3 * 1.75, 2.6 * 1.75), gridspec_kw={"width_ratios": [1.3, 1]})
    panel_partitions(ax[0], R); panel_text_phase(ax[1], P)
    s_ = R["static"]
    ax[0].set_title(f"(a) Full-vector two-sublattice test: true split ranked 1st in {s_['recovered']}/10\n"
                    f"debates (chance {s_['recovered_expected_null']:.1f}); pooled Δ̄ = {s_['delta']:.3f}, p = {s_['p_delta']:.2f}", loc="left", fontsize=7.5)
    if P:
        d5, p6 = P["Q5_text_axis_statement_level"], P["Q6_text_axis_by_phase"]["post"]
        ax[1].set_title("(b) Motion's a-priori stance axis: weak order\nin debate (9/10), flips after verdict (7/9)", loc="left", fontsize=7.5)
    ax[0].legend(fontsize=6, loc="lower left")
    fig.tight_layout(); fig.savefig(FF / "summary_obs.pdf"); plt.close(fig)
    # one-page results summary
    fig = plt.figure(figsize=(8.5, 11))
    gs = fig.add_gridspec(4, 2, height_ratios=[0.55, 1, 1, 1], hspace=0.62, wspace=0.42, left=0.2, right=0.96, top=0.97, bottom=0.05)
    axt = fig.add_subplot(gs[0, :]); axt.axis("off")
    s = R["static"]; gsp = R.get("generic", {}); fam = R.get("family", {}); f = R.get("fluct", {})
    pfe = fam.get("pair_fixed_effects", {})
    q = P or {}
    q5 = q.get("Q5_text_axis_statement_level", {}); q6 = q.get("Q6_text_axis_by_phase", {}); q7 = q.get("Q7_post_verdict_decomposition", {})
    q3 = q.get("Q3_same_lab_pairs", {}); q4 = q.get("Q4_topic_field", {}).get("Mu_topic_mean", {})
    lines = [
        "H21 × G12: the debate week as a two-sublattice magnet (exploratory; regime I; 10 debates; 7 agents)",
        "",
        f"PRE-REGISTERED, FAILED. Full-vector staggered order: Δ̄ = {s['delta']:.3f} [{s['delta_ci'][0]:.2f}, {s['delta_ci'][1]:.2f}], p = {s['p_delta']:.2f};",
        f"   LOAO m_s = {s['ms']:.3f} (p = {s['p_ms']:.2f}); teams recovered {s['recovered']}/{s['n_debates']} (chance {s['recovered_expected_null']:.1f}). Pair-FE b_team = {pfe.get('b_team_pairFE', np.nan):.3f} (p = {pfe.get('p_team_pairFE', np.nan):.2f}).",
        f"   Generic Gov−Opp transfer σ = {gsp.get('ms_generic', np.nan):.3f} (flip p = {gsp.get('p_generic_flip', np.nan):.2f}). Sublattice fluctuations ρ = {f.get('rho', np.nan):+.2f} (3-min; common drive, not AF).",
        f"PRE-REGISTERED, PASSED (not predicted significant). A-priori motion stance axis: σ_text = {R['text_axis']['raw']['ms_text']:.3f} (p = {R['text_axis']['raw']['p_text']:.3f}).",
        f"POST-HOC. Statement-level Gov−Opp on that axis: +{q5.get('gov_minus_opp_projection', np.nan):.2f} in debate (p = {q5.get('p', np.nan):.3f}, {q5.get('positive_debates', 0)}/{q5.get('n_debates', 0)}), "
        f"{q6.get('post', {}).get('gov_minus_opp_projection', np.nan):+.2f} after the verdict (flip, 7/9).",
        f"   Crossing field κ = {q7.get('kappa_crossing', np.nan):.2f} (8/10 debates); winner field w = {q7.get('w_winner_field', np.nan):+.2f} (none). Same-lab pairs +{q3.get('same_minus_diff_cos', np.nan):.2f} cos (p = {q3.get('p_exact', np.nan):.2f}).",
        f"   Uniform topic order M_u·ĝ: pre {q4.get('pre', np.nan):.2f}, debate {q4.get('deb', np.nan):.2f}, post {q4.get('post', np.nan):.2f} (the motion is a uniform field, on during debates).",
    ]
    axt.text(-0.22, 1, "\n".join(lines), va="top", ha="left", fontsize=7.2, color=INK, transform=axt.transAxes)
    a1 = fig.add_subplot(gs[1, :]); panel_partitions(a1, R)
    a2 = fig.add_subplot(gs[2, 0]); panel_robustness(a2, R); a2.set_title("Robustness / confounds (Δ̄)", loc="left")
    a3 = fig.add_subplot(gs[2, 1]); panel_fluct(a3, R); a3.set_title(f"Sublattice fluctuations, ρ = {f.get('rho', np.nan):+.2f}", loc="left")
    a4 = fig.add_subplot(gs[3, 0]); panel_text_phase(a4, P); a4.set_title("Motion stance axis by phase", loc="left")
    a5 = fig.add_subplot(gs[3, 1]); panel_synth(a5, syn)
    fig.savefig(FF / "summary.pdf"); plt.close(fig)
    print("figures written")


if __name__ == "__main__":
    main()
