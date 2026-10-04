"""Write H70 period and native folders: --predict (before outcomes) or --results (after run.py)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
H = HERE.parent
ROOT = H.parents[1]
DATA = ROOT / "data/processed/H70-artifact-store-semantic-info"
GP = H / "goalperiod-subhypotheses"
STAMP = "2026-10-04 20:05 UTC"

NATIVES = {
    "NE41": ("forced context erasures at the 41-call cap: the call-scale κ table (regime III, 2026-03-24 →)",
             "The scaffold erases the context window when a segment reaches 41 calls, at a time the agent did not "
             "choose; memory note, artifact and room stay. 21,165 non-holdout forced erasures and 21,806 "
             "pseudo-erasures at position 21 of no-reset runs give the HH307 rows with the same agents, days and "
             "estimator. Pooled over regime-III periods with agent-period strata (exception (c): each erasure is a "
             "transition object).",
             "- **N1a (artifact row):** I_A ≥ 0.3 bits (shuffle-corrected, CI > 0); ΔV_A > 0 with the CI excluding "
             "0; κ_A finite and positive.\n- **N1b (memory-note row):** I_M < I_A with non-overlapping CIs and "
             "ΔV_M's CI includes 0 (κ_M ≈ 0; H15).\n- **N1c (room row):** I_R < I_A / 3; ΔV_R < ΔV_A.\n"
             "- **N1d (context row):** ΔV_C = V(P) − V(F) > 0 (H15/H44: about −30 to −40% of commits); "
             "I_C < 0.3 × I_A.\n- **Order:** κ_A > κ_R > κ_M (HH307's order restricted to the rows H70 estimates).\n"
             "- **Counts against:** ΔV_A ≤ 0 with the CI excluding 0 (R2: reading precedes writing at least as "
             "much without an erasure), or I_M ≥ I_A (R1)."),
    "NE34": ("goal changes as relevance scrambles of the artifact store (nights across goal boundaries)",
             "At a new goal the agent's last repo usually stops being relevant: the store survives, its information "
             "about the next allocation should not. The #39 → #40 boundary is a continuation (#40 connects the "
             "worlds built in #39), so the store should stay informative there. Boundaries with both sides "
             "non-holdout and ≤ 7 days apart: #30→#31, #35→#36, #36→#37, #37→#38, #38→#39, #39→#40, #40→#41, "
             "#41→#42. Exception (c): the boundary is the object.",
             "- **N2a:** P(return to A⁻ | a commit) on the first day of a new goal ≤ 0.2, against ≥ 0.6 on "
             "within-period nights.\n- **N2b:** I_A across new-goal nights ≤ 0.3 × I_A within periods.\n"
             "- **N2c (continuation):** at #39 → #40, P(return) ≥ 0.4 (artifacts stay relevant).\n"
             "- **Counts against:** P(return) at new goals ≥ 0.5 (the artifact store, not the goal, sets "
             "allocation; R4 fails in the other direction), or #39 → #40 indistinguishable from new goals "
             "(the goal field alone sets allocation)."),
}


def counts() -> pl.DataFrame:
    e = pl.read_parquet(DATA / "events.parquet").filter((pl.col("n_win") >= 10) & (pl.col("A_prev") >= 0))
    return (e.group_by("period").agg(*[(pl.col("etype") == t).sum().alias(t) for t in ("F", "P", "N", "PN")],
                                     pl.col("agent").n_unique().alias("agents"), pl.col("regime").mode().first(),
                                     pl.col("pt_date").min().alias("first"), pl.col("pt_date").max().alias("last"))
            .sort("period"))


def predict():
    for r in counts().to_dicts():
        per = r["period"]
        d = GP / per
        (d / "figures").mkdir(parents=True, exist_ok=True)
        call = r["F"] >= 30 and r["P"] >= 30
        prim = "call scale (forced erasure vs pseudo-erasure)" if call else "day scale (night vs mid-day placebo)"
        small = (r["N"] < 30 or r["PN"] < 30) and not call
        txt = f"""# H70 × {per}: the artifact row of the κ table ({r['first']} → {r['last']})

**Verdict:** pending
**Role:** replication
**Period:** regime {r['regime']} · {r['agents']} agents with an own artifact · events with A⁻ known and ≥ 10 window calls: F {r['F']}, P {r['P']}, N {r['N']}, PN {r['PN']} (non-holdout). Primary scale: {prim}.

## Why this period
The common estimator on every non-holdout period with dense git (DQ4 from #30): the artifact channel's information about the next allocation (bits) and its value (commits per 20 calls) at the context erasures this period has. Each period is one point for the κ row of HH307.

## Prediction
*Written {STAMP}, before running on this period (card P1, P2, P7 applied).*
- I_A > 0 (within-agent permutation p < 0.05) at the primary scale; I_A ≥ 0.3 bits expected where agents hold more than one repo in the period.
- ΔV_A (open × scramble DiD, agent-period fixed effects, V_pre covariate) > 0 with the cluster-bootstrap CI excluding 0 at the primary scale.
- P(X⁺ = A⁻ | a commit) ≥ 0.8 after the scramble, within 0.1 of the placebo.
- Counts against: I_A not significant, or ΔV_A's CI excludes 0 below zero.{chr(10) + '- Fewer than 30 events per arm at day scale: the verdict is descriptive by the card rule.' if small else ''}

## Result
*(Filled by `analysis/period_folders.py --results`.)*

## Scorecard (period-specific axes)
*(Filled with the result.)*

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/periods.json` (key `{per}`).
"""
        (d / "README.md").write_text(txt)
    for ne, (title, why, pred) in NATIVES.items():
        d = GP / ne
        (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(f"""# H70 × {ne}: {title}

**Verdict:** pending
**Role:** native
**Period:** see "Why this period".

## Why this period
{why}

## Prediction
*Written {STAMP}, before running this native test.*
{pred}

## Result
*(Filled by `analysis/period_folders.py --results`.)*

## Scorecard (period-specific axes)
*(Filled with the result.)*

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/natives.json` (key `{ne}`).
""")
    print(counts())


def fill(path: Path, verdict: str, result_md: str, score_md: str):
    s = path.read_text()
    s = s.replace("**Verdict:** pending", f"**Verdict:** {verdict}", 1)
    s = s.replace("*(Filled by `analysis/period_folders.py --results`.)*", result_md, 1)
    s = s.replace("*(Filled with the result.)*", score_md, 1)
    path.write_text(s)


if __name__ == "__main__":
    if "--predict" in sys.argv:
        predict()


def _ci(r, k):
    c = r.get(k + "_ci") or [None, None]
    if c[0] is None:
        return "–"
    return f"[{c[0]:+.2f}, {c[1]:+.2f}]"


def results():
    per = json.loads((DATA / "results/periods.json").read_text())
    for p, r in per.items():
        path = GP / p / "README.md"
        if not path.exists():
            continue
        rows = []
        for scale in ("call", "day"):
            a = r.get(scale, {}).get("A")
            c = r.get(scale, {}).get("C")
            if a:
                rows.append(f"| {scale}: I_A (bits) | {a['I']:+.3f} {_ci(a, 'I')}; raw {a['I_raw']:.3f}, floor {a['I_floor']:.3f}; p {a['p_perm']:.3f} | within-agent permutation | {'met' if a['p_perm'] < 0.05 and a['I'] > 0 else 'not met'} |")
                rows.append(f"| {scale}: ΔV_A (open × scramble, Poisson) | rel {a['dV_rel']:+.2f} {_ci(a, 'dV_rel')}; {a['dV']:+.2f} commits / 20 calls {_ci(a, 'dV')} (open share F/N {a['open_share_scramble']:.2f}, placebo {a['open_share_placebo']:.2f}) | 0 (reading precedes writing) | {'met' if (a['dV_rel_ci'][0] or -1) > 0 else ('opposite' if (a['dV_rel_ci'][1] or 1) < 0 else 'not met')} |")
                k = a.get("kappa")
                rows.append(f"| {scale}: κ_A | {('%+.2f' % k) if k == k else 'undefined (I_A ≤ 0.02)'} {_ci(a, 'kappa')} commits / 20 calls / bit | – | – |")
            if c:
                rows.append(f"| {scale}: context row (cost of the erasure) | cost rel {c['dV_rel']:+.2f} {_ci(c, 'dV_rel')}; I_C {c['I']:+.3f} {_ci(c, 'I')} | 0 | – |")
        ret = r.get("return", {})
        rows.append("| P(X⁺ = A⁻ \\| commit) | " + ", ".join(f"{t} {v['p_return']:.2f} (n {v['n']})" for t, v in ret.items())
                    + " | – | " + ("met" if ret.get("F", ret.get("N", {"p_return": 0}))["p_return"] >= 0.8 else "not met") + " |")
        tab = "| Statistic | Observed | Null | Verdict |\n| --- | --- | --- | --- |\n" + "\n".join(rows)
        res = (f"*Run 2026-10-04 (`analysis/run.py`; non-holdout; agent-day cluster bootstrap, B = 300).* Primary scale: "
               f"{r['primary_scale']}.\n\n{tab}\n")
        score = ("- **C:** I_A against the within-agent permutation floor; ΔV_A against the placebo arm (Poisson DiD). "
                 "**E:** forced erasures (exogenous timing) and nights as context scrambles. **F:** synthetic recovery at "
                 "these counts (`synthetic/synthetic.json`).")
        fill(path, r["verdict"], res, score)


if __name__ == "__main__" and "--results" in sys.argv:
    results()
