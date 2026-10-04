"""H96 period folders. --init writes each folder's header and dated prediction before the real run;
--fill adds the result from data/processed/H96-goal-switch-hysteresis/results and natives.

Usage: uv run python hypotheses/H96-goal-switch-hysteresis/analysis/period_folders.py --init | --fill
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h96lib as L  # noqa: E402

GP = L.ROOT / "hypotheses/H96-goal-switch-hysteresis/goalperiod-subhypotheses"
RES = L.DATA / "results"
PRED_TIME = "2026-10-04 21:40 UTC"
NATIVE = {"G39", "NE38"}


def f(x, d=2):
    return "–" if (x is None or (isinstance(x, float) and not np.isfinite(x))) else f"{x:+.{d}f}" if d < 0 else f"{x:.{d}f}"


def ci(d, k=2):
    return f"{f(d['est'], k)} [{f(d['lo'], k)}, {f(d['hi'], k)}]"


def header(name, title, verdict, role, period_line):
    return f"# H96 × {name}: {title}\n\n**Verdict:** {verdict}\n**Role:** {role}\n**Period:** {period_line}\n"


REPL_PRED = """## Why this period
The common estimator (card O1–O3, O5) at the transition #{pm1} → #{p}: both periods non-holdout and in regime {reg}. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written {t}, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime {reg}; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.
"""


def init():
    tr = L.transition_records()
    cal = pl.read_parquet(L.OUT / "calendar.parquet")
    for r in tr:
        name = f"G{r['P']:02d}"
        d = GP / name; (d / "figures").mkdir(parents=True, exist_ok=True)
        days = cal.filter(pl.col("goal_no") == r["P"])["pt_date"]
        role = "native" if name in NATIVE else "replication"
        txt = header(name, f"old-state remanence after the #{r['Pm1']} → #{r['P']} switch ({days.min()} → {days.max()})",
                     "pending", role, f"regime {r['regime']} · transition #{r['Pm1']} → #{r['P']} · pre day {r['pre_day']} · "
                     f"old-state days {', '.join(r['old_days'])} · post days {', '.join(r['post_days'])} · "
                     f"{r['n_placebos']} placebo old states.")
        txt += "\n" + REPL_PRED.format(pm1=r["Pm1"], p=r["P"], reg=r["regime"], t=PRED_TIME)
        if name == "G39":
            txt += f"""
### Native N1 (two old rooms, one new field)
*Written {PRED_TIME}, before running.* #38 had two rooms with different kickoffs (#best: agents 20–23; #rest: 6, 10, 12–14, 16–18; DQ6). #39 applies one new field to both. Domain memory Δ = ⟨s·ê_own⊥ − s·ê_other⊥⟩ over veterans.
- Δ_pre > 0 with the CI excluding 0 [0.85]; Δ_1 > 0 with the CI excluding 0 [0.5]; Δ_1/Δ_pre < 0.5 [0.6].
- HH123: the room with the higher order q_room keeps the larger fraction Δ_1/Δ_pre [0.5].
- *Supported* if Δ_1 > 0 and the more ordered room keeps more; *failed* if Δ_pre > 0 and Δ_1's CI includes 0; *mixed* otherwise. Movers (20, 21, 23 go from #best to #rest) are reported separately because their new room-mates carry the other room's old state (contemporaneous convergence).
"""
        (d / "README.md").write_text(txt)
    # NE38 native
    d = GP / "NE38"; (d / "figures").mkdir(parents=True, exist_ok=True)
    txt = header("NE38", "one agent's role is reassigned (2026-07-29, inside #51)", "pending", "native",
                 "regime III · #51 · agent 40 (Claude Opus 5) reassigned by an operator message at 16:50 UTC on 07-29 "
                 "(DQ6) · old-state days 07-27, 07-28 · post days 07-29 (after the switch), 07-30, 07-31 · placebo: the "
                 "other #51 agents with statements in the same windows.")
    txt += f"""
## Why this period
A single-spin field step: one agent's own goal changes while every other agent keeps its goal. The other agents' own-state persistence across the same hours is a same-day placebo that the swarm-wide transitions do not have.

## Prediction
*Written {PRED_TIME}, before running (card N2).*
- Agent 40's old role state is identified (M_pre > 0).
- Its persistence ratio R₁ lies below the 10th percentile of the placebo agents' R₁ (its old state is erased faster than other agents' states drift) [0.7]; τ_old < 8 active h [0.6].
- HH123's lag reading: R₁ inside the placebo 10–90% band [0.3].
- *Supported (lag)* if R₁ is inside the band; *failed (quench)* if R₁ is below the 10th percentile; *descriptive* if M_pre ≤ 0; *mixed* otherwise.
"""
    (d / "README.md").write_text(txt)
    print("init", len(tr) + 1, "folders")


def fill(model="bge_small", variant="style_resid32"):
    tr = {o["P"]: o for o in json.loads((RES / f"transitions_{model}_{variant}.json").read_text())}
    tr_g = {o["P"]: o for o in json.loads((RES / f"transitions_gte_modernbert_{variant}.json").read_text())}
    nat = json.loads((L.DATA / "natives" / f"natives_{model}.json").read_text())
    nat_g = json.loads((L.DATA / "natives" / "natives_gte_modernbert.json").read_text())
    rows = []
    for P, o in tr.items():
        name = f"G{P:02d}"
        p = GP / name / "README.md"
        txt = p.read_text().split("\n## Result")[0]
        s, k, g = o["state"], o["kickoff"], tr_g[P]["state"]
        verdict = o["verdict"]
        vg = tr_g[P]["verdict"]
        res = f"""
## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* {s['n_agents']} agents, {s['n_placebos']} placebo old states, old-state order q = {f(s['q'], 3)}.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | {ci(s['M_pre'], 3)} | {ci(g['M_pre'], 3)} | 0 |
| M_1 (day 1 after the switch) | {ci(s['M_1'], 3)} | {ci(g['M_1'], 3)} | 0 |
| R₁ = M_1 / M_pre | {ci(s['R1'])} | {ci(g['R1'])} | pseudo-switch median {f(o['R1_pseudo_median'])} |
| τ_old (active h) | {ci(s['tau'], 2)} | {ci(g['tau'], 2)} | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | {ci(s['tau_sw'], 1)} | {ci(g['tau_sw'], 1)} | – |
| old kickoff R₁ (O6) | {ci(k['R1'])} | – | |
| new-kickoff depth A_K, day 1 | {ci(s['A_K1'], 3)} | {ci(g['A_K1'], 3)} | 0 |

**Verdict (card rule):** bge {verdict}; gte {vg}. M_exc by bin (active h {', '.join(f(x, 1) for x in s['H_centres'][2:] if x is not None)}): {', '.join(f(x, 3) for x in s['M_series'][2:] if x is not None)}.
"""
        if name == "G39":
            gn = nat["G39"]; gg = nat_g["G39"]
            def grp(G, key):
                d = G["groups"].get(key)
                return "–" if d is None else (f"Δ_pre {f(d['Delta_pre'], 3)} [{f(d['lo'][0], 3)}, {f(d['hi'][0], 3)}], "
                                              f"Δ_1 {f(d['Delta_1'], 3)} [{f(d['lo'][1], 3)}, {f(d['hi'][1], 3)}], "
                                              f"ratio {f(d['ratio'])} (n {d['n']})")
            res += f"""
### Native N1 result
| Group | bge | gte |
| --- | --- | --- |
| all veterans | {grp(gn, 'all')} | {grp(gg, 'all')} |
| from #best | {grp(gn, 'from_best')} | {grp(gg, 'from_best')} |
| from #rest | {grp(gn, 'from_rest')} | {grp(gg, 'from_rest')} |
| movers (20, 21, 23) | {grp(gn, 'movers')} | {grp(gg, 'movers')} |
| stayers | {grp(gn, 'stayers')} | {grp(gg, 'stayers')} |

Room order q_room (bge): #best {f(gn['q_room']['best'], 3)}, #rest {f(gn['q_room']['rest'], 3)}; higher-q room keeps more: {gn.get('higher_q_room_keeps_more')}. **Native verdict:** bge {gn['verdict']}, gte {gg['verdict']}. The folder verdict is the native verdict; the replication verdict for this transition is {verdict} (bge).
"""
            verdict = gn["verdict"]
        res += """
## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = %d).
""" % P
        txt = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {verdict}", txt, count=1)
        p.write_text(txt + res)
        rows.append((name, verdict))
    # NE38
    p = GP / "NE38" / "README.md"
    txt = p.read_text().split("\n## Result")[0]
    n, ng = nat["NE38"], nat_g["NE38"]
    a, ag = n["agent40"], ng["agent40"]
    res = f"""
## Result
*Run 2026-10-04 (`analysis/natives.py`; non-holdout).* {n['n_placebo_agents']} placebo agents.

| Quantity | bge | gte |
| --- | --- | --- |
| agent 40 M_pre | {f(a['M_pre'], 3)} | {f(ag['M_pre'], 3)} |
| agent 40 M_1 | {f(a['M_1'], 3)} | {f(ag['M_1'], 3)} |
| agent 40 R₁ [statement bootstrap] | {f(a['R1'])} [{f(a['R1_ci'][0])}, {f(a['R1_ci'][1])}] | {f(ag['R1'])} [{f(ag['R1_ci'][0])}, {f(ag['R1_ci'][1])}] |
| agent 40 τ_old (active h) | {f(a['tau'])} | {f(ag['tau'])} |
| placebo R₁ median [p10, p90] | {f((n['placebo_R1'] or {}).get('median'))} [{f((n['placebo_R1'] or {}).get('p10'))}, {f((n['placebo_R1'] or {}).get('p90'))}] | {f((ng['placebo_R1'] or {}).get('median'))} [{f((ng['placebo_R1'] or {}).get('p10'))}, {f((ng['placebo_R1'] or {}).get('p90'))}] |
| agent 40 percentile among placebos | {f(n['agent40_percentile'])} | {f(ng['agent40_percentile'])} |

**Verdict (card N2 rule):** bge {n['verdict']}; gte {ng['verdict']}.

## Scorecard (period-specific axes)
- **E:** a single-agent field step with a same-day placebo; **G:** the switch time comes from DQ6 (operator message).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/natives/natives_{{bge_small,gte_modernbert}}.json` (key NE38).
"""
    txt = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {n['verdict']}", txt, count=1)
    p.write_text(txt + res)
    rows.append(("NE38", n["verdict"]))
    print(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--fill", action="store_true")
    a = ap.parse_args()
    if a.init:
        init()
    if a.fill:
        fill()
