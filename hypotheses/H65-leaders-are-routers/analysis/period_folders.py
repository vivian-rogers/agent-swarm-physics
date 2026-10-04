"""Write H65 goal-period folders: `predict` (dated predictions, before the real-data run) and `results` (same
predictions plus verdicts and numbers, after the run).

    uv run python hypotheses/H65-leaders-are-routers/analysis/period_folders.py predict|results
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
CARD = HERE.parent
ROOT = CARD.parents[1]
DATA = ROOT / "data/processed/H65-leaders-are-routers"
PRED_TIME = "2026-10-04 20:15 UTC"
sys.path.insert(0, str(HERE))
from run import eligible_units  # noqa: E402

REPL = ("**Replication layer (templated).** Per agent: content inflow χ̂ and outflow κ̂ (read-gated linear response, "
        "bge-small primary), reply-out share RO, breadth BO and reply-in rate RI. Predictions for this period: "
        "R1 ρ(RO, χ̂) > 0 (answering is absorbing) [0.6]; **R2 D_p = ρ(RI, χ̂ | n) − ρ(RI, κ̂ | n) > 0** (the agents others "
        "reply to are content sinks, not sources) [0.35]; R3 ρ(χ̂, κ̂) < 0.5 [0.7]. Counts against H65's generalization: "
        "D_p < 0 with a bootstrap CI below 0.")

NATIVE = {
    "G26": """**Native (H65-N1, elected leader).** Agent 17 (DeepSeek-V3.2) over term 1 (2026-01-05 19:35:22 → 01-09 19:00:43 UTC), ranked among the period's agents with ≥ 30 statements: pct χ̂ ≥ 0.6 [0.45]; pct κ̂ ≤ 0.5 [0.6]; pct BO ≥ 0.5 [0.55]; **router call** (pct χ̂ ≥ 0.6 and pct κ̂ ≤ 0.5) [0.3]. H29 saw this leader's broadcast pull rise most (R-agenda would put pct κ̂ high).""",
    "G35": """**Native (H65-N2, daily lead designers, within agent).** Six DQ6 leader room-days. Agent × room-day estimates (≥ 10 statements); leader-day minus the same agent's other room-days, net of room-day effects; null = leader label permuted among each room-day's agents (5,000): Δχ > 0 [0.5]; Δκ ≤ 0 [0.6]; ΔBO > 0 [0.5]; ΔRI > 0 [0.7, H29]. **Router call** = Δχ > 0 with permutation p < 0.10 and Δκ ≤ 0 [0.25].""",
    "G44": """**Native (H65-N3, installed fine-tuned leader).** Agent 28 in #best from 2026-05-26 19:15:47 UTC (27 statements; thresholds 15 statements / 15 exposed targets for this native, fixed before the run): pct κ̂ ≤ 0.5 [0.8]; pct χ̂ ≥ 0.6 [0.5] (H23: its plans track the room); router call [0.4]. Expected low reliability.""",
    "G12": """**Native (H65-N4, rotating judges, within agent).** Each agent's statements as the judge of a debate vs as a debater in other debates (debate windows from DQ6; ≥ 5 statements per agent-debate); net of debate effects; null = judge label permuted among each debate's participants (5,000): Δκ > 0 (judges set the motion: R-agenda) [0.45]; Δχ > 0 [0.5]; router call [0.3].""",
}


def meta():
    pa = pl.read_parquet(ROOT / "data/processed/shared/period_affordances.parquet").filter(~pl.col("holdout"))
    m = pa.group_by("goal_no").agg(pl.col("goal_slug").first(), pl.col("mode").first(), pl.col("regime").first(),
                                   pl.col("N").max(), pl.col("n_days").sum(), pl.col("first_day").min(),
                                   pl.col("last_day").max(), pl.col("n_rooms").max(), pl.col("unit_id"))
    return {r["goal_no"]: r for r in m.to_dicts()}


def f(x, k=2):
    return "—" if x is None or not np.isfinite(x) else f"{x:+.{k}f}"


def write(predict_only: bool):
    M = meta()
    units = eligible_units()
    goals = sorted({g for g, _ in units})
    rep = {}
    if not predict_only:
        for r in json.loads((DATA / "replication/bge_small/periods.json").read_text()):
            rep.setdefault(r["goal"], []).append(r)
    for g in goals:
        name = f"G{g:02d}"
        m = M[g]
        native = name in NATIVE
        d = CARD / "goalperiod-subhypotheses" / name
        (d / "figures").mkdir(parents=True, exist_ok=True)
        if not (d / "figures/.gitkeep").exists():
            (d / "figures/.gitkeep").write_text("")
        verdict, result = "pending", "*Pending (run after this prediction).*"
        if not predict_only:
            verdict, result = results(name, g, rep.get(g, []))
        us = [u for gg, u in units if gg == g]
        units_txt = ", ".join(us) if us[0] else "one unit"
        txt = f"""# H65 × {name}: {m['goal_slug']} ({m['first_day']} → {m['last_day']})

**Verdict:** {verdict}
**Role:** {'native' if native else 'replication'}
**Period:** regime {m['regime']} · mode {m['mode']} · {m['N']} agents · {m['n_rooms']} room(s) · {m['n_days']} days. Units analysed: {units_txt}.

## Why this period
{why(name)}

## Prediction
*Written {PRED_TIME}, before running on this period.*

{REPL}
{chr(10) + NATIVE[name] if native else ''}

## Result
{result}

## Scorecard (period-specific axes)
{'*Pending.*' if verdict == 'pending' else scorecard(name)}

## Notes
- Data: `data/processed/H65-leaders-are-routers/G{g:02d}/` (targets, reads), `replication/<model>/` (periods.json, agents.parquet){', `natives/<model>/' + name + '.json`' if native else ''}. Holdout masked.
"""
        (d / "README.md").write_text(txt)
    print(f"wrote {len(goals)} folders ({'predict' if predict_only else 'results'})")


def why(name):
    return {
        "G26": "Native test: an elected leader with a DQ6 start instant (term 1 from 01-05 19:35 UTC).",
        "G35": "Native test: daily-rotating designated lead designers per room (DQ6), so the same agent is observed with and without the role.",
        "G44": "Native test: an installed fine-tuned leader in #best with DQ6 checkpoints.",
        "G12": "Native test: rotating debate judges (DQ6), so the same agent is observed as judge and as debater.",
    }.get(name, "A replication point: the router alignment D_p computed with the common estimator.")


def scorecard(name):
    if name in NATIVE:
        return "- **G (ground truth):** DQ6 leader or judge labels.\n- **F:** synthetic recovery at this skeleton (card).\n- **H:** R-source and R-agenda read off pct κ̂ / Δκ."
    return "- **C/D:** D_p with block-bootstrap CI; R1 mechanics."


def results(name, g, reps):
    lines = ["| Unit | agents | ρ(RO, χ̂) | D_p [95% CI] | ρ(χ̂, κ̂) | median λ̂/χ̂ | ρ(κ̂, H32 Out) |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in reps:
        ci = r.get("D_ci", [None, None])
        cis = f"[{f(ci[0])}, {f(ci[1])}]" if ci[0] is not None else ""
        lines.append(f"| {r['unit']} | {r['n_agents']} | {f(r['rho_RO_chi'])} | {f(r['D'])} {cis} | {f(r['rho_chi_kappa'])} | "
                     f"{f(r['lam_over_chi_median'])} | {f(r.get('rho_kappa_H32out', np.nan))} |")
    Ds = [r["D"] for r in reps if np.isfinite(r["D"])]
    v = "descriptive"
    if Ds:
        lo = [r["D_ci"][0] for r in reps if r.get("D_ci", [None])[0] is not None]
        hi = [r["D_ci"][1] for r in reps if r.get("D_ci", [None, None])[1] is not None]
        md = float(np.median(Ds))
        if lo and min(lo) > 0:
            v = "supported"
        elif hi and max(hi) < 0:
            v = "failed"
        else:
            v = "descriptive"
    lines.append(f"\nReplication verdict rule: supported if D_p > 0 with CI above 0; failed if D_p < 0 (attention goes to sources); "
                 "descriptive (no decision) if the CI includes 0 (as pre-registered, a D_p < 0 counts against only with its CI below 0).")
    nat = DATA / f"natives/bge_small/{name}.json"
    if name in NATIVE and nat.exists():
        r = json.loads(nat.read_text())
        lines.append("\n**Native layer** (bge-small primary; gte and style variants in `natives/<model>/`).\n")
        if name in ("G26", "G44"):
            lines.append(f"- leader percentiles among {r['n_agents']} agents: χ̂ {r['pct_chi']:.2f} (CI {r['pct_chi_ci']}), κ̂ {r['pct_kappa']:.2f} (CI {r['pct_kappa_ci']}), "
                         f"BO {r['pct_BO']:.2f}, RI {r['pct_RI']:.2f}, RO {r['pct_RO']:.2f}; router index {r['router_index']:+.2f}; router call **{r['router_call']}** "
                         f"(bootstrap share {r['router_call_boot_share']:.2f}); leader statements {r['leader_n']:.0f}.")
            for mdl in ("gte_modernbert", "style"):
                p = DATA / f"natives/{mdl}/{name}.json"
                if p.exists():
                    q = json.loads(p.read_text())
                    lines.append(f"- {mdl}: pct χ̂ {q['pct_chi']:.2f}, pct κ̂ {q['pct_kappa']:.2f}, router call {q['router_call']}.")
            nv = "supported" if r["router_call"] else ("failed" if r["pct_kappa"] > r["pct_chi"] else "mixed")
            if name == "G44":
                nv = "descriptive"   # Amendment A1: no router call is possible at this skeleton (null 90th pct = 1.0)
        else:
            lines.append("| Metric | β (role) | p (greater) | p (less) | rows |")
            lines.append("| --- | --- | --- | --- | --- |")
            for mt in ("chi", "kappa", "RO", "BO", "RI"):
                x = r[mt]
                lines.append(f"| {mt} | {f(x['beta'], 3)} | {x['p_greater']:.3f} | {x['p_less']:.3f} | {x['n']} |")
            lines.append(f"\nRouter call **{r['router_call']}**.")
            for mdl in ("gte_modernbert", "style"):
                p = DATA / f"natives/{mdl}/{name}.json"
                if p.exists():
                    q = json.loads(p.read_text())
                    lines.append(f"- {mdl}: Δχ {f(q['chi']['beta'], 3)} (p {q['chi']['p_greater']:.3f}), Δκ {f(q['kappa']['beta'], 3)} (p> {q['kappa']['p_greater']:.3f}), router call {q['router_call']}.")
            bc, bk = r["chi"]["beta"], r["kappa"]["beta"]
            nv = "supported" if r["router_call"] else ("failed" if (np.isfinite(bk) and np.isfinite(bc) and bk > bc and r["kappa"]["p_greater"] < 0.10) else "mixed")
        v = nv
    return v, "\n".join(lines)


if __name__ == "__main__":
    write(predict_only=(sys.argv[1] == "predict"))
