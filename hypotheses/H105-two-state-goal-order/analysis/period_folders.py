"""Write H105 replication period READMEs (goalperiod-subhypotheses/G<NN>/). G12 (native + pair) is edited by hand."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h105lib as L  # noqa: E402

GP = Path(__file__).resolve().parents[1] / "goalperiod-subhypotheses"
PAIRS = {"P16_17": 17, "P37_38": 38, "P03_04": 4, "P05_06": 6, "P11_12": 12}


def f(x, d=3):
    return "–" if x is None or x != x else f"{x:.{d}f}"


def main():
    pa = pl.read_parquet(L.ROOT / "data/processed/shared/period_affordances.parquet").unique("goal_no")
    meta = {r["goal_no"]: r for r in pa.iter_rows(named=True)}
    des = {r["design"]: r for r in pl.read_parquet(L.DATA / "designs.parquet").iter_rows(named=True)}
    pairs = pl.read_parquet(L.DATA / "NE34/pairs_all_configs.parquet")
    kick = pl.read_parquet(L.DATA / "NE34/kickoffs.parquet")
    rep = json.loads((L.DATA / "replication.json").read_text())
    items = [(d, g, True) for d, g in PAIRS.items()] + [(d, int(d[1:]), False) for d in kick["design"].to_list()
                                                         if d not in ("K04", "K06", "K12", "K17", "K38")]
    for d, g, is_pair in items:
        if g == 12:
            continue
        m = meta[g]; ds = des[d]
        if is_pair:
            r = pairs.filter((pl.col("design") == d) & (pl.col("cfg") == "primary")).row(0, named=True)
            rg = pairs.filter((pl.col("design") == d) & (pl.col("cfg") == "gte")).row(0, named=True)
        else:
            r = kick.filter(pl.col("design") == d).row(0, named=True); rg = None
        if not r.get("testable"):
            continue
        cal = rep["calibrated"].get(d)
        lines = [f"# H105 × G{g:02d}: {m['goal_slug']}", "", "**Verdict:** descriptive", "**Role:** replication",
                 f"**Period:** regime {ds['regime']} · mode {m['mode']} · {r['n_agents']} agents with ≥ 6 eligible windows in F and A · "
                 f"F = #{ds['F_goal']} ({ds['F_days'].split(',')[0]} … {ds['F_days'].split(',')[-1]}), A = unit {ds['A_unit']} days 2+ "
                 f"({ds['A_days'].split(',')[0]} … {ds['A_days'].split(',')[-1]}).", "",
                 "## Why this period",
                 ("A free → assigned pair named in HH130 (primary)." if d in ("P11_12", "P16_17", "P37_38") else
                  "A secondary free → assigned pair (N = 4)." if is_pair else
                  "One eligible kickoff transition (P6); F is the previous goal's tail."), "",
                 "## Prediction",
                 "*Templated from the card (written 2026-10-04 ~20:27 UTC), labelled as such.* P1: the tilt-predicted variance matches "
                 "the observed (90% block-bootstrap CI of ρ_V contains 0 and |ρ_V| < ln 1.5). P2 (pairs): logit-shift slope s ≈ 1. "
                 "**Amendment 1 (~20:51 UTC, before real data):** P1 and P3 are not identifiable at village sampling, so this folder is "
                 "descriptive; the rule's outcome is reported.", "",
                 "## Result", "| Statistic | bge-small | gte-modernbert |", "| --- | --- | --- |"]
        def row(name, k, d_=3):
            lines.append(f"| {name} | {f(r.get(k), d_)} | {f(rg.get(k), d_) if rg else '–'} |")
        row("occupancy p_F (free / previous)", "pF"); row("occupancy p_A (assigned)", "pA")
        row("loop gain g₂ in F", "gF", 2); row("loop gain g₂ in A", "gA", 2)
        row("observed growth ln(V_A/V_F)", "growth_obs", 2); row("tilt-predicted growth", "growth_pred", 2)
        row("ρ_V = ln(V_A obs / pred)", "rho", 2)
        lines.append(f"| ρ_V 90% CI | [{f(r.get('rho_lo'), 2)}, {f(r.get('rho_hi'), 2)}] | "
                     f"{'[' + f(rg.get('rho_lo'), 2) + ', ' + f(rg.get('rho_hi'), 2) + ']' if rg else '–'} |")
        lines.append(f"| P1 rule outcome | {r.get('p1')} | {rg.get('p1') if rg else '–'} |")
        if is_pair:
            row("logit slope s (P2)", "s", 2)
            lines.append(f"| s 90% CI | [{f(r['s_lo'], 2)}, {f(r['s_hi'], 2)}] | [{f(rg['s_lo'], 2)}, {f(rg['s_hi'], 2)}] |")
        lines.append("")
        if cal:
            lines.append(f"Calibrated (matched parametric bootstrap, 200 runs each): real ρ_V at the {cal['rho_pct_H']:.2f} quantile of the tilt (H) "
                         f"and {cal['rho_pct_R5']:.2f} of R5; slope s at {cal['s_pct_H']:.2f} of H and {cal['s_pct_R2']:.2f} of R2 → "
                         f"calibrated P2: **{cal['p2_calibrated']}**. Matched latent parameters: {cal['par']}.")
            lines.append("")
        if is_pair and "trajectory" in json.loads((L.DATA / f"G{g:02d}/results.json").read_text()):
            tr = json.loads((L.DATA / f"G{g:02d}/results.json").read_text())["trajectory"]
            lines.append("Day trajectory in A (p_d, V_d obs / tilt-pred): " + "; ".join(
                f"{t['day'][5:]} {t['p']:.2f}, {t['V']:.3f}/{f(t['V_pred'])}" for t in tr) + ".")
            res = json.loads((L.DATA / f"G{g:02d}/results.json").read_text())
            lines.append(f"Transverse control (50 directions ⊥ ĝ): median p⊥ {f(res.get('perp_pF'))} (F) → {f(res.get('perp_pA'))} (A); "
                         f"median ρ_V⊥ {f(res.get('perp_rho'), 2)}.")
            lines.append("")
        lines += [f"Data: `data/processed/H105-two-state-goal-order/NE34/{'pairs_all_configs' if is_pair else 'kickoffs'}.parquet`"
                  + (f", `G{g:02d}/results.json`" if is_pair else "") + ".", "",
                  "## Scorecard (period-specific axes)", "- D: the variance prediction is unfitted but not identifiable here (Amendment 1).",
                  "", "## Notes", "- Holdout masked; #23 excluded."]
        out = GP / f"G{g:02d}"; out.mkdir(parents=True, exist_ok=True)
        (out / "README.md").write_text("\n".join(lines) + "\n")
        print(g, d)


if __name__ == "__main__":
    main()
