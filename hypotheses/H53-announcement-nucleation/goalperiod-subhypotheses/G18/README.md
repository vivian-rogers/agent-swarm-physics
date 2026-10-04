# H53 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-11-03)

**Verdict:** mixed — RR 1.38 [1.03, 1.83]; F1 101.00; mean S 2.21; R 1.44
**Role:** replication
**Period:** regime I · mode C · 7 agents · 10 active days · 52 seeds (first chat link per project, non-holdout days). Units (step changes, `period_units`): 18a 2025-10-20→2025-10-21 (goal_start); 18b 2025-10-22→2025-10-28 (roster_join:Claude Haiku 4.5); 18c 2025-10-29→2025-10-31 (roster_leave:Grok 4). Unit intercepts are not separate fits; the period is the unit (card, exception (d)).

## Why this period
Replication: the common estimator (card O1–O10) on every eligible period.

## Prediction
*Written 2026-10-04, before running on this period.*
*Templated replication prediction (card P1, P1b, P6, P10 applied here), written 2026-10-04 before running on this period.* 52 eligible seeds; median susceptible in-room recipients 7; mean uncommitted U 2.7; mean receptive R 1.4 (structural counts only). R averages ≥ 1 per seed; the timing test has some power if adoption events are not too rare.
- RR_timely (one cycle): 95% CI includes 1, or RR < 1.5 (card call: H53's P1 fails).
- F1 step ratio ≥ 3 would mark read-out-triggered waves; a ratio < 3 marks a pre-ramp (H28). Expected: 1.5–3.
- F4 read-locking ≥ 2 for late readers if adoptions are triggered at read-out. Expected: unclear.
- Decision rule v2 label: not "nucleation".
- Verdict rule (per period): **supported** = v2 label "nucleation" and RR_timely ≥ 1.5 with CI > 1; **failed** = RR_timely CI includes 1 *and* (F1 < 3 or F4 < 2); **mixed** = otherwise; **descriptive** = fewer than 15 adoption events in the agent-level table (underpowered).

## Result
*Run 2026-10-04 (round 1), after the prediction above.* Verdict mapping for replication periods: Amendment 2 in the card (F4 is untestable per period).

| Prediction (templated) | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 RR_timely (one cycle) ≥ 1.5, CI > 1 | 1.38 [1.03, 1.83] (109 adoptions) | 1 (synthetic nulls: CI > 1 in 0–10% of runs) | fail |
| P1b RR_timely (10 min) | 2.09 [0.21, 21.17] | 1 | — |
| F1 step (adoptions 30 min after / before the seed) | 101.00 (pre 1, post 101) | ≈ 1 field, < 1 pre-ramp, > 10 read-out-triggered (synthetic) | step |
| F2 other-room / same-room adoption | n/a (0 multi-room seeds) | ≈ 1 field, ≈ 0.3 nucleation | — |
| F3 adopters never exposed to a link before adopting | 0.03 (n = 115) | — | — |
| F4 late-reader read-locking | n = 1, ratio 0.00 | untestable below 10 | — |
| Waves | mean S 2.21, max 7, zero 33%; mean R 1.44; herded 16, never 31 | — | — |

Decision-rule-v2 label (pooled thresholds applied to this period): seed-locked field (F4 untestable here, so a "seed-locked field" label only means read-out locking could not be shown).
**Verdict: mixed** (CI > 1 but RR < 1.5).

## Scorecard (period-specific axes)
C: RR_timely vs 1 (seed-stratified, day-cluster CI); D: F1/F2/F3 signatures; H: rivals (status, share, size) pooled only. G, E, I: n/a for this period.

## Notes
- Data: `data/processed/H53-announcement-nucleation/` (`seeds.parquet`, `recipients.parquet`, `round1/period_G18.json`).
