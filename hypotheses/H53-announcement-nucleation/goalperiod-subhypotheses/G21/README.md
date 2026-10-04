# H53 × G21: Forecast the abilities and effects of AI (2025-12-01 → 2025-12-08)

**Verdict:** failed — RR 0.76 [0.42, 1.36]; F1 ∞ (no pre-seed adoption); mean S 0.70; R 2.32
**Role:** replication
**Period:** regime I · mode I · 8 agents · 5 active days · 38 seeds (first chat link per project, non-holdout days). Units (step changes, `period_units`): 21a 2025-12-01→2025-12-03 (goal_start); 21b 2025-12-04→2025-12-05 (ne:NE07; roster_join:DeepSeek-V3.2). Unit intercepts are not separate fits; the period is the unit (card, exception (d)).

## Why this period
Replication: the common estimator (card O1–O10) on every eligible period.

## Prediction
*Written 2026-10-04, before running on this period.*
*Templated replication prediction (card P1, P1b, P6, P10 applied here), written 2026-10-04 before running on this period.* 37 eligible seeds; median susceptible in-room recipients 7; mean uncommitted U 4.4; mean receptive R 2.3 (structural counts only). R averages ≥ 1 per seed; the timing test has some power if adoption events are not too rare.
- RR_timely (one cycle): 95% CI includes 1, or RR < 1.5 (card call: H53's P1 fails).
- F1 step ratio ≥ 3 would mark read-out-triggered waves; a ratio < 3 marks a pre-ramp (H28). Expected: 1.5–3.
- F4 read-locking ≥ 2 for late readers if adoptions are triggered at read-out. Expected: unclear.
- Decision rule v2 label: not "nucleation".
- Verdict rule (per period): **supported** = v2 label "nucleation" and RR_timely ≥ 1.5 with CI > 1; **failed** = RR_timely CI includes 1 *and* (F1 < 3 or F4 < 2); **mixed** = otherwise; **descriptive** = fewer than 15 adoption events in the agent-level table (underpowered).

## Result
*Run 2026-10-04 (round 1), after the prediction above.* Verdict mapping for replication periods: Amendment 2 in the card (F4 is untestable per period).

| Prediction (templated) | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 RR_timely (one cycle) ≥ 1.5, CI > 1 | 0.76 [0.42, 1.36] (24 adoptions) | 1 (synthetic nulls: CI > 1 in 0–10% of runs) | fail |
| P1b RR_timely (10 min) | 130845384624.66 [12275824416.71, 1394652945203.70] | 1 | — |
| F1 step (adoptions 30 min after / before the seed) | ∞ (no pre-seed adoption) (pre 0, post 23) | ≈ 1 field, < 1 pre-ramp, > 10 read-out-triggered (synthetic) | step |
| F2 other-room / same-room adoption | n/a (0 multi-room seeds) | ≈ 1 field, ≈ 0.3 nucleation | — |
| F3 adopters never exposed to a link before adopting | 0.00 (n = 26) | — | — |
| F4 late-reader read-locking | n = 0 | untestable below 10 | — |
| Waves | mean S 0.70, max 4, zero 57%; mean R 2.32; herded 2, never 30 | — | — |

Decision-rule-v2 label (pooled thresholds applied to this period): seed-locked field (F4 untestable here, so a "seed-locked field" label only means read-out locking could not be shown).
**Verdict: failed** (RR CI includes 1).

## Scorecard (period-specific axes)
C: RR_timely vs 1 (seed-stratified, day-cluster CI); D: F1/F2/F3 signatures; H: rivals (status, share, size) pooled only. G, E, I: n/a for this period.

## Notes
- Data: `data/processed/H53-announcement-nucleation/` (`seeds.parquet`, `recipients.parquet`, `round1/period_G21.json`).
