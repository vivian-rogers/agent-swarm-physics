"""Write the H26 goal-period folders.

  --predict   writes goalperiod-subhypotheses/G<NN>/README.md with the dated prediction and a pending result
              (run 2026-10-04 ~02:05 UTC, before explore.py touched any real unit)
  --results   fills the Result / Verdict / Scorecard sections from data/processed/H26-content-near-critical/G<NN>/*.json
              (the Prediction section is never rewritten)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
D = ROOT / "data/processed/H26-content-near-critical"
PRED_DATE = "2026-10-04 ~02:05 UTC"

PERIODS = {
    35: dict(title="RPG forks (#best / #rest)", dates="2026-03-16 → 2026-03-23", regime="II", mode="C", N=13,
             rooms="two rooms (#best, #rest) working on separate forks of one game", days=5, units=["35"],
             why="Descriptive extra (regime II). Highest within-room content co-fluctuation in H01 (ρ_within 0.66 vs ρ_cross 0.09); rooms work on different forks, so a room-specific task field competes with coupling.",
             pred="Content L3 (day) g_ex,c ≥ 0.5 [0.65]: the room excess in H01 is very large. Activity L3 (day) is unpowered (IQR ≈ 0.9 in the synthetic), so Δg_ca will not exclude 0 → verdict **mixed** [0.6]. At w30, content > activity by > 0.15 [0.5]. The fork split is a room field the static projection cannot remove (it is not in the kickoff text), so even a high g_ex here is weak evidence for coupling."),
    36: dict(title="Regime-III start (#36b)", dates="2026-03-24 → 2026-03-30 (non-holdout unit #36b)", regime="III", mode="C", N=13,
             rooms="two rooms", days=4, units=["36b"],
             why="First regime-III days after the switch to continuous computer use; H01: ρ_within 0.31 vs ρ_cross 0.15 (sizeable global component).",
             pred="Borderline: g_ex,c (day) 0.3–0.6 [0.6]; the global component is large, so L3 removes more here than elsewhere. Verdict **mixed** or **failed** [0.75 combined]; Δg_ca unpowered at 4 days."),
    37: dict(title="Free week", dates="2026-03-30 → 2026-04-02", regime="III", mode="F", N=13, rooms="two rooms", days=3,
             units=["37"],
             why="Free week; H01 found no room excess (ρ_within 0.30 ≈ ρ_cross 0.26): co-fluctuation is global. A clean test that L3 deflates a drive-dominated week.",
             pred="g_ex,c (day) < 0.5 [0.75], near 0 [0.5]: the co-fluctuation is cross-room, i.e. global drive. Verdict **failed** [0.7]. Only 3 days: CIs very wide."),
    38: dict(title="Rooms with different instructions (#38a–c)", dates="2026-04-02 → 2026-04-27 (units 38a, 38b, 38c split at NE17 04-14 and NE18 04-20)",
             regime="III", mode="C", N=12, rooms="two rooms given different instructions", days=17, units=["38a", "38b", "38c"],
             why="Rooms received different goals (a room field). Also the period with most self-repetition loops (H12; 11–23% of chat removed by the dedupe). H20's kickoff relaxation lasts ~4 days here.",
             pred="38a (8 days): g_ex,c (day) ≥ 0.5 [0.55]. 38b and 38c: g_ex,c < 0.5 [0.65 each]. Dedupe lowers raw content gains in 38a/38b by ≥ 0.05 [0.5]. Because room-specific instructions are a room field, a high 38a value is not evidence for coupling. Verdicts: 38a mixed, 38b/38c failed."),
    39: dict(title="Individual tasks, pre-merge", dates="2026-04-27 → 2026-05-04", regime="III", mode="I", N=15,
             rooms="two rooms", days=5, units=["39"],
             why="Individual-task week (mode I); H01: weak room excess (0.17 vs 0.08), strong lab order.",
             pred="g_ex,c (day) < 0.5 [0.7]; verdict **failed** [0.65]. Content and activity gains both small; Δg_ca ≈ 0 ± noise."),
    40: dict(title="Room merge week", dates="2026-05-04 → 2026-05-11", regime="III", mode="C", N=15,
             rooms="two rooms, merged mid-week (universe-coordination room)", days=5, units=["40"],
             why="Rooms merged during the week (H01 P7: residual alignment of new pairs rose). Pair type is set per pair-window, so the merge enters L3 correctly. H12: self-repetition loops.",
             pred="g_ex,c (day) 0.3–0.6 [0.6]; verdict **mixed** [0.5]. The merge shrinks the number of cross-room pair-days, so ρ_cross is noisy."),
    41: dict(title="Same task in both rooms", dates="2026-05-11 → 2026-05-18", regime="III", mode="I", N=15,
             rooms="two rooms, identical task", days=5, units=["41"],
             why="The most coupling-like week in H01 (ρ_within 0.47 vs ρ_cross 0.04) with the *same* instructions in both rooms, so room-specific fields are least plausible. The best period for H26.",
             pred="g_ex,c (day) ≥ 0.5 [0.7]; content exceeds activity at w30 by > 0.15 [0.55]. Verdict **mixed** [0.55] (Δg_ca CI at day level likely includes 0) or **supported** [0.25]."),
    42: dict(title="Individual tasks (contagion candidate)", dates="2026-05-18 → 2026-05-25", regime="III", mode="I", N=15,
             rooms="two rooms", days=5, units=["42"],
             why="Field-dominated week in H01 (goal-only R² 0.54) with little room excess (0.19 vs 0.14).",
             pred="g_ex,c (day) < 0.5 [0.75], probably < 0.3 [0.6]; verdict **failed** [0.7]."),
    44: dict(title="Per-room goal override, leader week", dates="2026-05-26 → 2026-06-01", regime="III", mode="C", N=16,
             rooms="two rooms, one with an overridden goal", days=4, units=["44"],
             why="Large room excess in H01 (0.34 vs −0.01) but with a per-room goal override (room field); 59 human messages (the most of any regime-III period), so the measured exogenous drive is largest here.",
             pred="g_ex,c (day) ≥ 0.5 [0.6]; the exogenous projection (L2) lowers the room gain by more here than in any other period [0.5]. Verdict **mixed** [0.6]: the room field (goal override) is not removed by projection of one kickoff direction."),
    51: dict(title="Private roles, one big room (#51a–e)", dates="2026-07-06 → 2026-09-07 (non-holdout; tail held out)", regime="III", mode="P (I/K)", N=21,
             rooms="one room (#general), plus the #focus room in 51c", days=45, units=["51a", "51b", "51c", "51d", "51e"],
             why="Large single room (N 21–32) with private role goals; long sub-units (51b: 19 days, 51c: 14) give the best-powered activity estimates. Single room → no cross-room baseline except in 51c (#focus).",
             pred="51c (#focus, two rooms): g_ex,c (day) < 0.5 [0.6] (H01: 0.06 vs 0.01). Single-room units (51a, b, d, e): L2 content gains are upper bounds; the synthetic shows a global drive alone gives g ≈ 0.75 at N = 24, T = 15, so a high value means nothing. P6: g_c ≥ g_a at day level in most sub-units [0.55]. Verdict **descriptive** for single-room units, **failed** for 51c [0.55]."),
}


def predict():
    for g, p in PERIODS.items():
        d = HYP / "goalperiod-subhypotheses" / f"G{g:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        f = d / "README.md"
        if f.exists() and "## Prediction" in f.read_text():
            print(f"G{g:02d}: prediction already written; not overwriting"); continue
        txt = f"""# H26 × G{g:02d}: {p['title']} ({p['dates']})

**Verdict:** pending
**Role:** exploratory
**Period:** regime {p['regime']} · mode {p['mode']} · {p['N']} agents · {p['rooms']} · {p['days']} days. H01 units used: {', '.join(p['units'])}.

## Why this period
{p['why']}

## Prediction
*Written {PRED_DATE}, before running on this period.* The card's rules apply (day level, L3 on two-room units): **supported** = g_ex,c ≥ 0.5, Δg_ca > 0.15 with 95% CI excluding 0, and N2 p < 0.05; **failed** = g_ex,c < 0.5 and Δg_ca ≤ 0.15; else **mixed**. Single-room units are descriptive. Bracketed numbers are my probabilities. Seen beforehand: H01's per-unit ρ_within / ρ_cross and βJ₀/n, H19's per-period activity and talk gains, the synthetic validation, scheme counts.

{p['pred']}

## Result
(pending)

## Scorecard (period-specific axes)
(pending)

## Notes
- {PRED_DATE[:10]}: prediction written before the H26 estimators touched this period.
"""
        f.write_text(txt)
        print(f"G{g:02d}: written")


if __name__ == "__main__":
    if "--predict" in sys.argv:
        predict()
    elif "--results" in sys.argv:
        from write_period_results import results  # noqa: E402
        results(PERIODS)
