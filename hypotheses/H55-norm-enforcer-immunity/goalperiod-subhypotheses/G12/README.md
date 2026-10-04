# H55 × G12: debate tournament (2025-09-01 → 2025-09-05)

**Verdict:** mixed
**Role:** native
**Period:** regime I · mode O/M · 7 agents · one room · 5 days; units 12a (debates, 09-01 → 09-04) and 12b (NE04, 09-05, no debates).

## Why this period
Ten debates, each with a judge assigned by the operator protocol (DQ6 ground truth: judge, teams, phases with time bounds). A judge is an assigned evaluator and rule-keeper, the closest thing in the village to an assigned corrector outside #51. Each debate gives a replicate in which one agent holds the enforcing seat, and seats rotate, which separates the seat from the agent.

## Prediction
*Written 2026-10-04 06:41 UTC, before any H55 statistic on this period.* Replies inside debate windows (first speech → verdict), DQ2 agent→agent pairs with p_reply ≥ 0.5.
- **N12a (construct):** judges' Jev correction rate in their debates exceeds the debaters' rate in the same debates (judge label permuted among the seven agents within each debate, 5,000; one-sided p < 0.05). [0.4]
- **N12b (friction):** debaters' replies to their judge are more negative in soft stance than their replies to teammates (within-speaker contrast; same permutation null; p < 0.05). [0.3; deference to the judge would give the opposite sign]
- *Against:* judges correct no more than debaters, or are treated as well as teammates.

## Result
*Run 2026-10-04 (`analysis/native.py`; data `data/processed/H55-norm-enforcer-immunity/G12/native.json`).* Ten debates; 'deb' = DQ6 speech phase (first speech → verdict), 'whole' = the judge's full window (draft → post-verdict).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| N12a judges correct more (deb) | judge 0.039 vs debaters 0.003 Jev corrections per parented message; 7 of 10 debates are 0 vs 0; soft score higher in 6/10 | sign test p 0.50 (soft 0.25) | **fail** (direction as predicted, n.s.) |
| N12b debaters' replies to the judge more negative than to teammates (deb, primary) | judge − teammate soft stance −0.39 [−0.88, +0.04]; 6 of 9 debates negative | sign p 0.25 | **fail** at the pre-registered level |
| N12b, judge's whole window (robustness) | −0.32 [−0.51, −0.12]; 9 of 10 debates negative | sign p 0.011 | pass (includes post-verdict replies) |
| judge vs opponents (descriptive) | judge treated better than opponents (+0.27 deb, +0.34 whole) | | – |

**Replication numbers here:** P1 ρ −0.14 (7 agents, p 0.65); P2 γ +0.15 (27 replies to corrections; p 0.39). The address effect on loop escape is the largest of any period: Δ +0.24 [+0.14, +0.37] (85 steps): in the debates, being spoken to ends restatement.

**Reading.** The judge's seat sits between the two teams in stance: cooler than a teammate, warmer than an opponent. That is mild friction toward an assigned evaluator, visible over the whole debate (including reactions to verdicts) but not significant inside the speech phase alone. Judges do not measurably correct more than debaters with the Jev sensor (very few flagged messages in regime I).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | whole-window judge contrast beats the sign test; the primary window does not |
| G ground truth | 1 | judges (ground truth) are treated less warmly than teammates in 9/10 debates (whole window) |
