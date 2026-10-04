"""Write per-period README skeletons with dated predictions (step 'predict', run BEFORE the real-data run), and later
fill the Result / Verdict sections from round-1 outputs (step 'fill'). Native periods' predictions are hand-written in
NATIVE_PRED below (also written before their run). Replication predictions are templated and labelled as such.

Usage: uv run python analysis/period_folders.py predict | fill
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import polars as pl

from h53core import OUT, load, prep

HYP = Path(__file__).resolve().parents[1]
GP = HYP.parents[0] / "hypohypotheses" / "goal-periods.md"
REPL = [4, 8, 12, 13, 17, 18, 19, 20, 21, 24, 25, 26, 30, 31, 36, 37, 38, 39, 40, 41, 42, 44, 51]
DESC = [5, 6, 16, 23, 27, 33, 35]
NATIVE = [26, 30, 31, 40]
DATE = "2026-10-04"


def period_meta():
    txt = GP.read_text()
    meta = {}
    for m in re.finditer(r"^\| (\d+) \| (\S+ → \S+) \| ([^|]+) \| ([^|]+) \| [^|]+ \| (I+) \| (\w) \| (\w) \|", txt, re.M):
        g = int(m.group(1))
        meta[g] = dict(dates=m.group(2), d=m.group(3).strip(), N=m.group(4).strip(), reg=m.group(5), by=m.group(6), mode=m.group(7))
    for m in re.finditer(r"^### (\d+) · (.+)$", txt, re.M):
        meta.setdefault(int(m.group(1)), {})["title"] = m.group(2).strip()
    return meta


NATIVE_PRED = {
    26: """**Native test (election rounds; DQ6 ground truth).** Seeds are the three round-opening announcements in `ground_truth_labels` (`phase` rows, preferred): the 01-05 approval vote, the 01-05 runoff (opened 19:32:19 UTC, closed 19:34:00, 7–1–0) and the 01-09 confirmatory vote (scheduled window 18:45–19:00). The wave is the ballots (`ballot` rows; voter = `agent_a`; each voter's first ballot per round). Read-out = the voter's ledger receiving call of the announcement.
- **N26-a (read-out gating):** ≥ 90% of ballots are cast at or after the voter's read-out call of the round's announcement. Against: ≥ 2 ballots in a round before the voter's read-out (anticipation). Credence 0.8.
- **N26-b (latency):** in each round the median number of the voter's calls from read-out to ballot is ≤ 2. Credence 0.6.
- **N26-c (order):** Spearman ρ(read-out time, ballot time) ≥ 0.6 in the runoff and in the confirmatory round. Credence 0.6.
- **N26-d (wave = receptive count):** in the runoff, ballots cast within the 100-s window = voters whose read-out fell inside the window, ±1; non-voters read late or not at all. Credence 0.6.
- **N26-e (scheduled-field rival):** the 01-09 round was scheduled in advance. A clock-driven field predicts ballots at 18:45 regardless of read-out; H53 predicts ballots follow the opening message's read-out (N26-a holds in round 2). Credence 0.7.
- The replication estimator also runs on #26's link seeds (templated prediction as for replication periods: RR_timely CI includes 1).""",
    30: """**Native test (re-announcements of one shared repo).** #30 has one shared park repo linked ~160 times by 11 agents (and a second repo ~95 times). Every chat link to one of these two projects after ≥ 60 active min without a link to it is a **re-seed**. Project attractiveness is then held fixed. Outcome per re-seed: *returners*, in-room agents without the project as their W = 15 label in the previous 60 active min who take it within 60 active min after their own read-out; wave = returners within 2 h.
- **N30-a:** return-wave size rises with R (NB slope on log(1+R) with log(1+N) control > 0, 95% CI > 0). Credence 0.2.
- **N30-b:** agent-level RR_timely for returning ≥ 1.5 with CI > 1. Credence 0.2.
- **N30-c (pre-trend):** returns in the 30 active min after re-seeds / before ≥ 2. Credence 0.35 (H28: links ride ongoing bursts).
- **N30-d (descriptive):** each of H27's four #30 onsets lies within 60 min after a re-seed.
- The replication estimator on #30's 11 first-link seeds: templated, underpowered (R mean ≈ 0.6).""",
    31: """**Native test (free week: H11's waves vs H06's private projects).** #31 is the clearest herding week (H11; the time-capsule repo reached 11 agents; H27: 4 onsets) and also a week of mostly private projects (H06: singletons 0.79–0.91). Structural note: only ~15% of recipients are uncommitted here, so R averages ≈ 0.5 per seed.
- **N31-a:** ≥ 70% of #31's eligible seeds never herd (max k ≤ 1). Credence 0.7.
- **N31-b:** AUC of R for herded vs never-herded seeds ≥ 0.65. Credence 0.25.
- **N31-c:** the largest 2-h wave in #31 comes from a seed with R ≥ 2. Against: the largest wave at R ≤ 1 (big waves without a receptive crowd). Credence 0.3.
- **N31-d:** herded seeds show a step (F1 ≥ 3); against: a pre-ramp (H28). Credence 0.35.
- **N31-e:** RR_timely within #31: CI includes 1 (33 seeds, low R). Credence it is > 1 with CI: 0.15.""",
    40: """**Native test (negative control: a hub frozen at the kickoff).** H31 found #40's hub project frozen at the kickoff (already shared in the first window). Hub = the project with the most W = 30 labelled agent-windows on #40's first day. H53 says nothing nucleates here: the goal names the hub.
- **N40-a:** ≥ 50% of agents who ever hold the hub label in #40 took it before the hub's first chat link in #40, or without any link to it in their context before adopting (pre-seed or unexposed adopters). Credence 0.55.
- **N40-b:** hub adoptions cluster in the first active hour of day 1 (≥ 50% of hub adopters), i.e. lock to the kickoff, not to a link. Credence 0.55.
- **N40-c:** the hub seed's wave is not larger than M_N predicts for #40 (no nucleation excess). Credence 0.6.
- The replication estimator on #40's other seeds (agents' worlds): templated.""",
}


def templated(g, s):
    d = s.filter((pl.col("goal_no") == g) & pl.col("eligible"))
    n = d.height
    rm = d["R"].mean() if n else 0
    um = d["U"].mean() if n else 0
    nm = d["N_sus"].median() if n else 0
    power = ("R averages below 1 per seed, so at most about one agent per seed can be receptive; H53 then predicts small waves, and the timing test has little power."
             if rm < 1 else "R averages ≥ 1 per seed; the timing test has some power if adoption events are not too rare.")
    return f"""*Templated replication prediction (card P1, P1b, P6, P10 applied here), written {DATE} before running on this period.* {n} eligible seeds; median susceptible in-room recipients {nm:.0f}; mean uncommitted U {um:.1f}; mean receptive R {rm:.1f} (structural counts only). {power}
- RR_timely (one cycle): 95% CI includes 1, or RR < 1.5 (card call: H53's P1 fails).
- F1 step ratio ≥ 3 would mark read-out-triggered waves; a ratio < 3 marks a pre-ramp (H28). Expected: 1.5–3.
- F4 read-locking ≥ 2 for late readers if adoptions are triggered at read-out. Expected: unclear.
- Decision rule v2 label: not "nucleation".
- Verdict rule (per period): **supported** = v2 label "nucleation" and RR_timely ≥ 1.5 with CI > 1; **failed** = RR_timely CI includes 1 *and* (F1 < 3 or F4 < 2); **mixed** = otherwise; **descriptive** = fewer than 15 adoption events in the agent-level table (underpowered)."""


def predict():
    meta = period_meta()
    seeds, rec = load()
    s, r = prep(seeds, rec)
    pu = pl.read_parquet(OUT.parents[0] / "shared" / "period_units.parquet")
    for g in REPL + DESC:
        m = meta.get(g, {})
        units = pu.filter((pl.col("goal_no") == g) & ~pl.col("holdout")).sort("seq")
        split = "; ".join(f"{u['unit_id']} {u['first_day']}→{u['last_day']} ({u['reason']})" for u in units.iter_rows(named=True)) if units.height > 1 else "none"
        role = "native" if g in NATIVE else ("replication" if g in REPL else "replication")
        folder = HYP / "goalperiod-subhypotheses" / f"G{g:02d}"
        (folder / "figures").mkdir(parents=True, exist_ok=True)
        pred = NATIVE_PRED[g] + "\n\n" + templated(g, s) if g in NATIVE else templated(g, s)
        if g in DESC:
            pred = pred.replace("*Templated replication prediction", "*Descriptive period (3–9 eligible seeds): templated prediction") + "\n- Verdict: descriptive whatever the outcome (too few seeds)."
        nseeds = s.filter(pl.col("goal_no") == g).height
        txt = f"""# H53 × G{g:02d}: {m.get('title', '')} ({m.get('dates', '')})

**Verdict:** pending
**Role:** {role}
**Period:** regime {m.get('reg', '?')} · mode {m.get('mode', '?')} · {m.get('N', '?')} agents · {m.get('d', '?')} active days · {nseeds} seeds (first chat link per project, non-holdout days). Units (step changes, `period_units`): {split}. Unit intercepts are not separate fits; the period is the unit (card, exception (d)).

## Why this period
{"Native test: see the prediction below." if g in NATIVE else ("Replication: the common estimator (card O1–O10) on every eligible period." if g in REPL else "Descriptive: 3–9 eligible seeds.")}

## Prediction
*Written {DATE}, before running on this period.*
{pred}

## Result
(pending)

## Scorecard (period-specific axes)
(pending)

## Notes
- Data: `data/processed/H53-announcement-nucleation/` (`seeds.parquet`, `recipients.parquet`, `round1/period_G{g:02d}.json`).
"""
        p = folder / "README.md"
        if p.exists() and "**Verdict:** pending" not in p.read_text():
            print("skip (already filled)", p)
            continue
        p.write_text(txt)
    print("written", len(REPL + DESC))




def fmt_rr(v):
    if not v:
        return "n/a"
    return f"{v['rr']:.2f} [{v['lo']:.2f}, {v['hi']:.2f}]"


def repl_verdict(pk):
    """Amendment 2 mapping (F4 untestable per period): supported = RR >= 1.5, CI > 1, F1 >= 3; failed = CI includes 1 or
    RR < 1; mixed = CI > 1 but RR < 1.5 (or CI < 1: noted); descriptive = < 15 adoptions or non-estimable SE."""
    a = (pk.get("agent") or {}).get("x_timely")
    if pk["agent_n_adopt"] < 15 or not a or a["se"] < 0.01:
        return "descriptive", "underpowered (< 15 adoptions or SE not estimable)"
    f1 = pk["field"]["F1"]["ratio"]
    if a["rr"] >= 1.5 and a["lo"] > 1 and (f1 is None or f1 >= 3):
        return "supported", "RR ≥ 1.5 with CI > 1 and a step at the seed"
    if a["lo"] > 1:
        return "mixed", "CI > 1 but RR < 1.5"
    if a["hi"] < 1:
        return "failed", "RR < 1 with CI < 1 (late readers adopt more)"
    return "failed", "RR CI includes 1"


def fill(native_text: dict | None = None):
    R1 = OUT / "round1"
    d = json.loads((R1 / "round1.json").read_text())
    seeds, rec = load()
    s, r = prep(seeds, rec)
    rows = []
    for g in REPL + DESC:
        p = HYP / "goalperiod-subhypotheses" / f"G{g:02d}" / "README.md"
        txt = p.read_text()
        f = R1 / f"period_G{g:02d}.json"
        if f.exists():
            pk = json.loads(f.read_text())
            a = (pk.get("agent") or {}).get("x_timely")
            fd = pk["field"]
            f1 = fd["F1"]["ratio"]; f2 = fd["F2"]["ratio"]; f4 = fd["F4"]
            ftxt = lambda x: "n/a" if x is None else ("∞ (no pre-seed adoption)" if x == float("inf") else f"{x:.2f}")
            table = f"""| Prediction (templated) | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 RR_timely (one cycle) ≥ 1.5, CI > 1 | {fmt_rr(a)} ({pk['agent_n_adopt']} adoptions) | 1 (synthetic nulls: CI > 1 in 0–10% of runs) | {'pass' if a and a['rr'] >= 1.5 and a['lo'] > 1 else 'fail'} |
| P1b RR_timely (10 min) | {fmt_rr(pk.get('agent_f600'))} | 1 | — |
| F1 step (adoptions 30 min after / before the seed) | {ftxt(f1)} (pre {fd['F1']['pre']}, post {fd['F1']['post']}) | ≈ 1 field, < 1 pre-ramp, > 10 read-out-triggered (synthetic) | {'step' if f1 is not None and f1 >= 3 else 'no step'} |
| F2 other-room / same-room adoption | {ftxt(f2)} ({fd['F2']['n_seeds']} multi-room seeds) | ≈ 1 field, ≈ 0.3 nucleation | — |
| F3 adopters never exposed to a link before adopting | {ftxt(fd['F3']['unexposed'])} (n = {fd['F3']['n']}) | — | — |
| F4 late-reader read-locking | {('n = ' + str(f4.get('n', 0)) + (', ratio ' + ftxt(f4.get('ratio')) if f4.get('n') else '')) } | untestable below 10 | — |
| Waves | mean S {pk['mean_S']:.2f}, max {pk['max_S']}, zero {pk['frac_zero']:.0%}; mean R {pk['mean_R']:.2f}; herded {pk['herded']}, never {pk['never']} | — | — |"""
            verdict, why = repl_verdict(pk)
            label = pk.get("label_v2")
            key = f"RR {fmt_rr(a)}; F1 {ftxt(f1)}; mean S {pk['mean_S']:.2f}; R {pk['mean_R']:.2f}"
        else:
            el = s.filter((pl.col("goal_no") == g) & pl.col("eligible"))
            table = f"Descriptive: {el.height} eligible seeds; mean wave S {el['S'].mean() if el.height else float('nan'):.2f}, max {el['S'].max() if el.height else 0}; mean R {el['R'].mean() if el.height else float('nan'):.2f}; mean N_sus {el['N_sus'].mean() if el.height else float('nan'):.1f}. Pooled into nothing (period below the 10-seed rule)."
            verdict, why, label = "descriptive", "3–9 eligible seeds", "n/a"
            key = f"{el.height} seeds; mean S {el['S'].mean() if el.height else float('nan'):.2f}"
        nat = (native_text or {}).get(g)
        if nat:
            verdict, why = nat["verdict"], nat["why"]
            key = nat["key"]
            table = nat["table"] + "\n\n**Replication estimator on this period (context):**\n\n" + table
        res = f"""*Run 2026-10-04 (round 1), after the prediction above.* Verdict mapping for replication periods: Amendment 2 in the card (F4 is untestable per period).

{table}

Decision-rule-v2 label (pooled thresholds applied to this period): {label}{' (F4 untestable here, so a "seed-locked field" label only means read-out locking could not be shown)' if label == 'seed-locked field' else ''}.
**Verdict: {verdict}** ({why})."""
        txt = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {verdict} — {key}", txt, count=1)
        txt = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + res.replace("\\", "\\\\") + "\n\n## Scorecard", txt, count=1, flags=re.S)
        sc = nat["scorecard"] if nat else "C: RR_timely vs 1 (seed-stratified, day-cluster CI); D: F1/F2/F3 signatures; H: rivals (status, share, size) pooled only. G, E, I: n/a for this period."
        txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes", "## Scorecard (period-specific axes)\n" + sc + "\n\n## Notes", txt, count=1, flags=re.S)
        p.write_text(txt)
        rows.append((g, verdict, key))
    (OUT / "round1" / "period_verdicts.json").write_text(json.dumps(rows, indent=1))
    return rows


if __name__ == "__main__":
    if sys.argv[1] == "predict":
        predict()
    else:
        from natives_text import NATIVE_RESULTS
        for row in fill(NATIVE_RESULTS):
            print(row)
