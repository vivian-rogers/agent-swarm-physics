"""H103 period folders. --init writes headers and dated predictions before the real run; --fill adds results.

Usage: uv run python hypotheses/H103-nights-demagnetize/analysis/period_folders.py --init | --fill
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
import h103lib as L  # noqa: E402

GP = L.ROOT / "hypotheses/H103-nights-demagnetize/goalperiod-subhypotheses"
RES = L.DATA / "results"
PRED_TIME = "2026-10-04 21:45 UTC"


def f(x, d=3):
    return "–" if (x is None or (isinstance(x, float) and not np.isfinite(x))) else f"{x:.{d}f}"


def header(name, title, verdict, role, line):
    return f"# H103 × {name}: {title}\n\n**Verdict:** {verdict}\n**Role:** {role}\n**Period:** {line}\n"


O1_PRED = """## Why this period
The common clock comparison (card O1) on the kickoff remanence of #{g}, and the two-time night step (O3) on its period units. Regime {reg}: {mech}.

## Prediction
*Written {t}, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.
"""
MECH = {"I": "nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h",
        "II": "nights rarely start a new context (10% of first-of-day calls); days are about 4 active h",
        "III": "the context carries over the night in most cases, and resets happen every ~41 calls inside the day (NE41); days are 4–8 active h"}


def init():
    S_per = pl.read_parquet(L.DATA / "periods.parquet")
    days = pl.read_parquet(L.DATA / "days.parquet")
    for rec in S_per.to_dicts():
        g = rec["goal_no"]; name = f"G{g:02d}"
        d = GP / name; (d / "figures").mkdir(parents=True, exist_ok=True)
        dd = days.filter(pl.col("goal_no") == g)
        role = "native" if name == "G06" else "replication"
        txt = header(name, f"which clock the kickoff remanence decays on ({dd['pt_date'].min()} → {dd['pt_date'].max()})",
                     "pending", role, f"regime {rec['regime']} · {len(rec['incumbents'])} incumbents · fit days "
                     f"{', '.join(rec['fit_days'])} · {rec['n_days']} non-holdout active days.")
        txt += "\n" + O1_PRED.format(g=g, reg=rec["regime"], mech=MECH[rec["regime"]], t=PRED_TIME)
        if name == "G06":
            txt += f"""
### Native N3 (village-off midday breaks)
*Written {PRED_TIME}, before running (card N3).* Two village-wide midday breaks of near-night length exist in the non-holdout record, both in regime I: 2025-06-18 (#4, 300 min) and 2025-06-29 (#6, 774 min). For the same agents on that day and the adjacent active days: self-overlap of window pairs across the break vs same-side pairs and cross-night pairs at matched active lag (break time excluded).
- Prediction: across-break overlap is within the range of same-side pairs, not at the cross-night level [0.6]. Descriptive (4 agents, 2 events). Both events are reported here.
"""
        (d / "README.md").write_text(txt)
    for name, title, line, body in (
        ("NE43", "the operator's daily bookends stop (2026-08-05, inside #51)",
         "regime III · #51 non-holdout days 07-06 → 08-04 (before) vs 08-05 → 09-04 (after) · the 08-05 room split "
         "(#general / #focus) lands on the same day.",
         f"""## Why this period
The operator's pause/resume messages framed every night until 2026-08-04; after that the runner still stops and starts the agents, but nobody announces it. If the night step needs the announcement, it changes here.

## Prediction
*Written {PRED_TIME}, before running (card N1).*
- Δβ_N = β_N(after) − β_N(before) has a CI that includes 0 [0.6]: the night step, whatever its size, does not depend on the bookends.
- *Against:* the CI excludes 0. Verdict: *supported* if the CI includes 0, *failed* otherwise. Confounded with the room split.
"""),
        ("NE41", "context resets inside the day as demagnetizing steps (regime III)",
         "regime III · every eligible regime-III period unit · forced consolidations at the 41-call cap plus voluntary "
         "consolidations and session starts (`context_ledger_turns`).",
         f"""## Why this period
In regime III the context is erased every ~41 calls inside the day, while it mostly carries over the night (H69). If HH331's mechanism (consolidation and erasure) demagnetizes content, each reset should lower an agent's self-overlap at fixed active lag.

## Prediction
*Written {PRED_TIME}, before running (card N2).*
- The within-day reset term β_R (per own reset between two windows, at fixed active-lag bins) has an RE mean with a CI that includes 0 and |β_R| < 0.005 [0.55] (H46: content does not move at erasures).
- *Against:* β_R < 0 with the CI excluding 0. Verdict: *supported* (no reset effect) if the CI includes 0 and |β_R| < 0.005; *failed* if the CI is below 0; *mixed* otherwise.
""")):
        d = GP / name; (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(header(name, title, "pending", "native", line) + "\n" + body)
    print("init done")


def fill(tag="bge_small_style_resid"):
    tag_g = tag.replace("bge_small", "gte_modernbert")
    o1 = json.loads((RES / f"o1_{tag}.json").read_text()); o1g = json.loads((RES / f"o1_{tag_g}.json").read_text())
    o3 = json.loads((RES / f"o3_{tag}.json").read_text()); o3g = json.loads((RES / f"o3_{tag_g}.json").read_text())
    o2 = json.loads((RES / f"o2_{tag}.json").read_text())
    nat = json.loads((RES / f"natives_{tag}.json").read_text())
    natg = json.loads((RES / f"natives_{tag_g}.json").read_text())
    out = []
    for name, r in o1.items():
        p = GP / name / "README.md"
        txt = p.read_text().split("\n## Result")[0]
        g = o1g.get(name, {})
        units = [u for u, x in o3.items() if x["goal_no"] == r["goal_no"]]
        def row(r):
            return (f"winner {r['winner']}; SSE N/H/W/R/0 = " + "/".join(f(r['sse'][c] * 1e3, 2) for c in ['N', 'H', 'W', 'R', '0'])
                    + f" (×10⁻³); λ {f(r['nested']['lam'], 2)} [{f(r['lam_ci'][0], 2)}, {f(r['lam_ci'][1], 2)}]; "
                    f"Δm(best) [{f(r['dA_best_ci'][0])}, {f(r['dA_best_ci'][1])}]; P(N beats H) {f(r['p_N_beats_H'], 2)}")
        res = f"""
## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* {r['n_windows']} windows, {r['n_agents']} incumbents, {r['n_days']} fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | {row(r)} | {row(g) if g else '–'} |
| day-1 kickoff excess | {f(r['level_day1'])} [{f(r['level_day1_ci'][0])}, {f(r['level_day1_ci'][1])}] | {f(g.get('level_day1'))} |
| night step S_N / day drift D / midday step S_mid | {f(r['steps']['S_N'])} / {f(r['steps']['D'])} / {f(r['steps']['S_mid'])} | {f(g['steps']['S_N'])} / {f(g['steps']['D'])} / {f(g['steps']['S_mid'])} |
| O1 verdict | {r['verdict']} | {g.get('verdict', '–')} |
"""
        for u in units:
            x, y = o3[u], o3g.get(u, {})
            def b(z, k):
                return "–" if not z or not np.isfinite(z[k]["est"]) else f"{z[k]['est']:+.4f} [{z[k]['lo']:+.4f}, {z[k]['hi']:+.4f}]"
            res += f"| O3 unit {u}: β_N / β_G / β_gap | {b(x, 'beta_N')} / {b(x, 'beta_G')} / {b(x, 'beta_gap')} | {b(y, 'beta_N')} |\n"
        if name in o2:
            z = o2[name]
            res += f"| O2 previous-centroid day-1 level | {f(z['level_day1'])} [{f(z['level_day1_ci'][0])}, {f(z['level_day1_ci'][1])}]; verdict {z['verdict']} | – |\n"
        verdict = r["verdict"]
        if name == "G06":
            md = nat["midday"]
            res += "\n### Native N3 result (village-off midday breaks)\n| Day | break (min) | across-break C | same-side C (matched lag) | cross-night C (matched lag) |\n| --- | --- | --- | --- | --- |\n"
            for d, v in md.items():
                m = v["matched"] or {}
                res += (f"| {d} (#{v['goal_no']}) | {v['dur_min']} | {f(m.get('across_break'))} (n {m.get('n_across')}) | "
                        f"{f(m.get('same_side_matched'))} (n {m.get('n_same')}) | {f(m.get('cross_night_matched'))} (n {m.get('n_cross')}) |\n")
            verdict = "descriptive"
            res += "\nThe folder verdict is the native's (descriptive); the O1 replication verdict for #6 is " + r["verdict"] + ".\n"
        res += f"""
## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key {name}), `o3_*.json`.
"""
        txt = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {verdict}", txt, count=1)
        p.write_text(txt + res)
        out.append((name, verdict))
    # natives
    n1, n1g = nat["NE43"], natg["NE43"]
    p = GP / "NE43" / "README.md"; txt = p.read_text().split("\n## Result")[0]
    def bb(z):
        return f"{z['est']:+.4f} [{z['lo']:+.4f}, {z['hi']:+.4f}]"
    res = f"""
## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).*

| Statistic | bge | gte |
| --- | --- | --- |
| β_N before (07-06 → 08-04) | {bb(n1['before']['beta_N'])} | {bb(n1g['before']['beta_N'])} |
| β_N after (08-05 → 09-04) | {bb(n1['after']['beta_N'])} | {bb(n1g['after']['beta_N'])} |
| Δβ_N | {bb(n1['delta_beta_N'])} | {bb(n1g['delta_beta_N'])} |
| β_G before / after | {bb(n1['before']['beta_G']) if np.isfinite(n1['before']['beta_G']['est']) else '–'} / {bb(n1['after']['beta_G']) if np.isfinite(n1['after']['beta_G']['est']) else '–'} | |
| pairs before / after | {n1['before']['n_pairs']} / {n1['after']['n_pairs']} | |

**Verdict (card N1 rule):** bge {n1['verdict']}; gte {n1g['verdict']}.
"""
    p.write_text(re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {n1['verdict']}", txt, count=1) + res)
    n2, n2g = nat["NE41"], natg["NE41"]
    p = GP / "NE41" / "README.md"; txt = p.read_text().split("\n## Result")[0]
    res = f"""
## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* {n2['beta_R_RE']['k']} regime-III units.

| Statistic | bge | gte |
| --- | --- | --- |
| β_R RE mean (per own reset, same-day pairs) | {bb(n2['beta_R_RE'])} | {bb(n2g['beta_R_RE'])} |

Per unit (bge): """ + "; ".join(f"{u} {x['beta_R']['est']:+.4f} [{x['beta_R']['lo']:+.4f}, {x['beta_R']['hi']:+.4f}]"
                                   for u, x in n2["units"].items() if "beta_R" in x) + f"""

**Verdict (card N2 rule):** bge {n2['verdict']}; gte {n2g['verdict']}.
"""
    p.write_text(re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {n2['verdict']}", txt, count=1) + res)
    out += [("NE43", n1["verdict"]), ("NE41", n2["verdict"])]
    print(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--fill", action="store_true")
    a = ap.parse_args()
    if a.init:
        init()
    if a.fill:
        fill()
