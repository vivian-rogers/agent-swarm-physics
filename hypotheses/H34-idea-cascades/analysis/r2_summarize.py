"""H34 round 2: per_period_estimates rows and round-2 lines in the period READMEs.

  uv run python hypotheses/H34-idea-cascades/analysis/r2_summarize.py estimates
  uv run python hypotheses/H34-idea-cascades/analysis/r2_summarize.py periods
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
import h34core as C  # noqa: E402

sys.path.insert(0, str(C.ROOT / "infra/shared"))
R1B, R2 = C.OUT / "r1b", C.OUT / "r2"
GP = HERE.parent / "goalperiod-subhypotheses"
SRC = "data/processed/H34-idea-cascades/r2/"


def days_of(g):
    return json.loads((R1B / f"G{g:02d}" / "meta.json").read_text())["days"]


def fnum(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else float(x)


def estimates():
    from estimates import write_estimates, map_unit
    rows = []
    mx = pl.read_parquet(R2 / "mixture" / "periods_r1b.parquet")
    fc = pl.read_parquet(R2 / "mixture" / "forecast_r1b.parquet").filter(pl.col("win") == "all").group_by("goal").agg(
        (pl.col("ls_gamma") - pl.col("ls_betabin")).sum().alias("d_bb"), pl.col("n_test").sum().alias("n_test"))
    mx = mx.join(fc, on="goal", how="left")
    for r in mx.iter_rows(named=True):
        g = int(r["goal"]); d = days_of(g)
        base = dict(goal_no=g, period_unit=map_unit(g, d[0], d[-1]), first_day=d[0], last_day=d[-1], role="replication",
                    method="H34.r2_gamma_mixture", channel="content", n=float(r["n_trees"]), n_kind="trees",
                    source=SRC + "mixture/periods_r1b.parquet")
        rows.append({**base, "statistic": "gamma_shape_alpha", "estimate": r["alpha"], "ci_lo": r["alpha_lo"], "ci_hi": r["alpha_hi"],
                     "ci_kind": "percentile", "null": "homogeneous FN-GW (alpha -> inf); LR chi-bar2",
                     "notes": f"idea-level R0 ~ Gamma(alpha, mu); mu {r['mu']:.3f}; LR {r['LR']:.1f}; 25 idea-bootstrap refits"})
        rows.append({**base, "statistic": "gamma_mean_R0", "estimate": r["mu"], "ci_lo": r["mu_lo"], "ci_hi": r["mu_hi"],
                     "ci_kind": "percentile", "null": None, "notes": "finite-N GW with depletion, Poisson offspring within idea"})
        rows.append({**base, "statistic": "offspring_ratio_nonroot_root", "estimate": r["ratio_obs"], "ci_lo": r.get("ratio_lo"),
                     "ci_hi": r.get("ratio_hi"), "ci_kind": "parametric", "null": "homogeneous skeleton <= 0.91; node-level NB ~0.8",
                     "notes": "CI = 90% band of the fitted gamma-mixed model (unfitted statistic); observed value is a point"})
        if r.get("d_bb") is not None:
            rows.append({**base, "statistic": "dayahead_logscore_gain_vs_betabinomial", "estimate": r["d_bb"], "ci_lo": None,
                         "ci_hi": None, "ci_kind": "none", "null": "beta-binomial (N1)", "n": float(r["n_test"]), "n_kind": "test trees",
                         "source": SRC + "mixture/forecast_r1b.parquet", "notes": "nats summed over scored days (round-1 P7 design)"})
    for tag, model in (("sem_bge_small", "bge_small"), ("sem_gte_modernbert", "gte_modernbert")):
        pt = pl.read_parquet(R2 / tag / "results" / "period_table.parquet")
        for r in pt.iter_rows(named=True):
            g = int(r["goal"]); d = days_of(g)
            base = dict(goal_no=g, period_unit=map_unit(g, d[0], d[-1]), first_day=d[0], last_day=d[-1], role="replication",
                        method=f"H34.r2_semantic_{model}", channel="content", n=float(r["nodes"]), n_kind="agent first uses",
                        source=SRC + f"{tag}/results/period_table.parquet")
            rows.append({**base, "statistic": "R_hat_semantic", "estimate": r["R"], "ci_lo": r["R_lo"], "ci_hi": r["R_hi"],
                         "ci_kind": "percentile", "null": None, "notes": "leader-clustered paraphrase ideas; idea-cluster bootstrap; ledger"})
            if fnum(r.get("hr10")) is not None:
                rows.append({**base, "statistic": "HR10_semantic", "estimate": r["hr10"], "ci_lo": fnum(r["hr10_lo"]),
                             "ci_hi": fnum(r["hr10_hi"]), "ci_kind": "profile", "null": "no-exposure turns, idea-stratified"})
            if fnum(r.get("hr_seen5")) is not None and fnum(r.get("hr_unread5")) is not None and r["hr_seen5"] > 0:
                rows.append({**base, "statistic": "HR_unread5_over_seen5_semantic", "estimate": r["hr_unread5"] / r["hr_seen5"],
                             "ci_lo": None, "ci_hi": None, "ci_kind": "none", "null": "copying predicts < 1",
                             "notes": f"HR_seen5 {r['hr_seen5']:.2f}, HR_unread5 {r['hr_unread5']:.2f}"})
    g = pl.read_parquet(R2 / "ne" / "groups.parquet").filter(pl.col("used"))
    summ = json.loads((R2 / "ne" / "summary.json").read_text())
    for r in g.iter_rows(named=True):
        g1 = int(r["g1"]); d0, d1 = days_of(int(r["g0"])), days_of(g1)
        rows.append(dict(goal_no=g1, period_unit=map_unit(g1, d1[0], d1[-1]), first_day=d1[0], last_day=d1[-1], role="native",
                         method="H34.r2_room_change", channel="content", statistic=f"dlnRsrc_{r['boundary']}_room{r['room_before']}to{r['room_after']}",
                         estimate=r["d_obs"], ci_lo=r["d_lo"], ci_hi=r["d_hi"], ci_kind="percentile", n=float(r["fu_after"]),
                         n_kind="group first uses (after side)", null=f"predicted {r['d_pred']:+.3f} from N {r['N_before']}->{r['N_after']}",
                         source=SRC + "ne/groups.parquet", notes=f"source-based R {r['R_before']:.3f} -> {r['R_after']:.3f}; {r['n_members']} agents"))
    d36, d42 = days_of(36), days_of(42)
    rows.append(dict(goal_no=None, holdout=False, period_unit="local:G36-G42", first_day=d36[0], last_day=d42[-1], role="native",
                     method="H34.r2_room_change", channel="content", statistic="dilution_slope_beta", estimate=summ["beta"],
                     ci_lo=summ["beta_ci"][0], ci_hi=summ["beta_ci"][1], ci_kind="percentile", n=float(summ["n_groups"]), n_kind="groups",
                     null="beta = 1 law; skeleton constant-per-read 1.4-2.5; field 2.5", source=SRC + "ne/summary.json",
                     notes="boundary fixed effects; CI = wider of idea bootstrap and residual t (6 boundaries)"))
    ne = summ["NE42"]; d40, d41 = days_of(40), days_of(41)
    rows.append(dict(goal_no=40, period_unit=map_unit(40, d40[0], d40[-1]), first_day=d40[0], last_day=d40[-1], role="native",
                     method="H34.r2_room_change", channel="content", statistic="NE42_ABA_contrast_D", estimate=ne["D"],
                     ci_lo=ne["D_ci"][0], ci_hi=ne["D_ci"][1], ci_kind="percentile", n=4.0, n_kind="groups",
                     null=f"predicted {ne['D_pred']:.2f}; skeleton 1.2-2.6", source=SRC + "ne/summary.json"))
    rh = summ["rho40"]
    rows.append(dict(goal_no=40, period_unit=map_unit(40, d40[0], d40[-1]), first_day=d40[0], last_day=d40[-1], role="native",
                     method="H34.r2_room_change", channel="content", statistic="merged_week_rho_cross_over_same", estimate=rh["rho"],
                     ci_lo=rh["rho_ci"][0], ci_hi=rh["rho_ci"][1], ci_kind="percentile", n=float(rh["trans_same"] + rh["trans_cross"]),
                     n_kind="transmissions", null="rho = 1 (rooms only route reading)", source=SRC + "ne/summary.json"))
    fo = summ["focus51"]; d51 = days_of(51)
    rows.append(dict(goal_no=51, period_unit="local:G51-focus-0805-0824", first_day="2026-08-05", last_day="2026-08-24", role="native",
                     method="H34.r2_room_change", channel="content", statistic="focus_vs_general_rpair_ratio", estimate=fo["ratio"],
                     ci_lo=fo["ratio_ci"][0], ci_hi=fo["ratio_ci"][1], ci_kind="percentile", n=float(fo["fu_focus"] + fo["fu_general"]),
                     n_kind="first uses", null=f"law {fo['pred_ratio']:.2f}; constant R {(fo['N_general'] - 1) / (fo['N_focus'] - 1):.2f}",
                     source=SRC + "ne/summary.json", status="descriptive"))
    write_estimates(rows, "H34")
    print(len(rows), "rows")


def fmt(x, d=2):
    return "n/a" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:.{d}f}"


def periods():
    mx = {int(r["goal"]): r for r in pl.read_parquet(R2 / "mixture" / "periods_r1b.parquet").iter_rows(named=True)}
    fc = pl.read_parquet(R2 / "mixture" / "forecast_r1b.parquet").filter(pl.col("win") == "all").group_by("goal").agg(
        (pl.col("ls_gamma") - pl.col("ls_betabin")).sum().alias("d"))
    fcd = {int(r["goal"]): r["d"] for r in fc.iter_rows(named=True)}
    sb = {int(r["goal"]): r for r in pl.read_parquet(R2 / "sem_bge_small" / "results" / "period_table.parquet").iter_rows(named=True)}
    sg = {int(r["goal"]): r for r in pl.read_parquet(R2 / "sem_gte_modernbert" / "results" / "period_table.parquet").iter_rows(named=True)}
    ne = pl.read_parquet(R2 / "ne" / "groups.parquet").filter(pl.col("used"))
    names = {2: "#best", 3: "#rest", 4: "#universe"}
    for g, m in mx.items():
        p = GP / f"G{g:02d}" / "README.md"
        s = p.read_text()
        b, t = sb[g], sg[g]
        ratio_u = lambda r: (r["hr_unread5"] / r["hr_seen5"]) if r.get("hr_seen5") and r["hr_seen5"] > 0 and r.get("hr_unread5") is not None else float("nan")
        line = (f"**Round 2 (2026-10-05):** replication only; the 1b verdict stands. Gamma-mixed branching α̂ {fmt(m['alpha'])} "
                f"[{fmt(m['alpha_lo'])}, {fmt(m['alpha_hi'])}], tail {'covered' if m['cover_both'] else 'not covered'}; "
                f"semantic R̂ {fmt(b['R'])} (bge) / {fmt(t['R'])} (gte).")
        sec = ["", "## Round 2 (2026-10-05)", "*Replication rows for the card's R1 and R4 (predictions in the main card, written 03:50 UTC). Role: replication; no verdict change.*", "",
               "| Quantity | Value | Reference |", "| --- | --- | --- |",
               f"| R1 gamma-mixed FN-GW: α̂ (CV² = 1/α), μ̂ | {fmt(m['alpha'])} [{fmt(m['alpha_lo'])}, {fmt(m['alpha_hi'])}], μ̂ {fmt(m['mu'], 3)} | LR vs one R: {fmt(m['LR'], 1)} (5% point 2.71) |",
               f"| R1 tail: P(s ≥ 3), P(s ≥ 5) | {fmt(m['obs_p3'], 3)}, {fmt(m['obs_p5'], 4)} | Γ-FN 90% band [{fmt(m['lo_p3'], 3)}, {fmt(m['hi_p3'], 3)}], [{fmt(m['lo_p5'], 4)}, {fmt(m['hi_p5'], 4)}]: {'covered' if m['cover_both'] else 'not covered'} |",
               f"| R1 non-root / root offspring (unfitted) | {fmt(m.get('ratio_obs'))} | Γ-FN band [{fmt(m.get('ratio_lo'))}, {fmt(m.get('ratio_hi'))}]; one R {fmt(m.get('ratio_h0'))}; homogeneous skeleton ≤ 0.91 |",
               f"| R1 day-ahead log score, Γ-FN minus beta-binomial | {fmt(fcd.get(g), 1)} nats | > 0 favours Γ-FN |",
               f"| R4 semantic R̂, bge (θ 0.90) | {fmt(b['R'])} [{fmt(b['R_lo'])}, {fmt(b['R_hi'])}], {b['nodes']} first uses | marker R̂ (1b) in the 1b line above |",
               f"| R4 semantic R̂, gte (θ 0.877) | {fmt(t['R'])} [{fmt(t['R_lo'])}, {fmt(t['R_hi'])}], {t['nodes']} first uses | |",
               f"| R4 HR₁₀ (bge / gte) | {fmt(b.get('hr10'), 1)} / {fmt(t.get('hr10'), 1)} | field null 1 |",
               f"| R4 HR_unread5 / HR_seen5 (bge / gte) | {fmt(ratio_u(b))} / {fmt(ratio_u(t))} | copying < 1; marker median 0.56 |"]
        sub = ne.filter(pl.col("g1") == g)
        if sub.height:
            ne_txt = "; ".join(f"{names.get(r['room_before'], r['room_before'])}→{names.get(r['room_after'], r['room_after'])} "
                               f"(N {r['N_before']}→{r['N_after']}): Δ ln R_src {r['d_obs']:+.2f} [{r['d_lo']:+.2f}, {r['d_hi']:+.2f}] vs predicted {r['d_pred']:+.2f}"
                               for r in sub.iter_rows(named=True))
            line += f" **NE (round 2), boundary #{g - 1}→#{g}:** {ne_txt}."
            sec += ["", f"**R2 native, boundary #{g - 1}→#{g}** (role native; dilution rule R̂ ∝ (N − 1)^0.451 written before looking): {ne_txt}. "
                    "The boundary is also a goal change, so only the difference between groups is read (card, R2)."]
        lines = s.split("\n")
        lines = [l for l in lines if not l.startswith("**Round 2 (2026-10-05):**")]
        if "## Round 2 (2026-10-05)" in s:
            i = lines.index("## Round 2 (2026-10-05)")
            lines = lines[:i - 1] if lines[i - 1] == "" else lines[:i]
        k = next(i for i, l in enumerate(lines) if l.startswith("**Role:**"))
        lines.insert(k, line)
        p.write_text("\n".join(lines).rstrip("\n") + "\n" + "\n".join(sec) + "\n")
    print("updated", len(mx), "period READMEs")


if __name__ == "__main__":
    {"estimates": estimates, "periods": periods}[sys.argv[1]]()
