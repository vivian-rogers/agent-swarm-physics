# H53 × G44: Finetune your leader! (2026-05-26 → 2026-06-01)

**Verdict:** failed — RR 1.18 [0.86, 1.60]; F1 13.67; mean S 1.20; R 1.24
**Role:** replication
**Period:** regime III · mode C · 16 agents · 4 active days · 46 seeds (first chat link per project, non-holdout days). Units (step changes, `period_units`): 44a 2026-05-26→2026-05-27 (goal_start); 44b 2026-05-28→2026-05-29 (roster_join:Claude Opus 4.8; roster_join:[Temporary] Fine-tuned Leader). Unit intercepts are not separate fits; the period is the unit (card, exception (d)).

## Why this period
Replication: the common estimator (card O1–O10) on every eligible period.

## Prediction
*Written 2026-10-04, before running on this period.*
*Templated replication prediction (card P1, P1b, P6, P10 applied here), written 2026-10-04 before running on this period.* 45 eligible seeds; median susceptible in-room recipients 11; mean uncommitted U 2.8; mean receptive R 1.2 (structural counts only). R averages ≥ 1 per seed; the timing test has some power if adoption events are not too rare.
- RR_timely (one cycle): 95% CI includes 1, or RR < 1.5 (card call: H53's P1 fails).
- F1 step ratio ≥ 3 would mark read-out-triggered waves; a ratio < 3 marks a pre-ramp (H28). Expected: 1.5–3.
- F4 read-locking ≥ 2 for late readers if adoptions are triggered at read-out. Expected: unclear.
- Decision rule v2 label: not "nucleation".
- Verdict rule (per period): **supported** = v2 label "nucleation" and RR_timely ≥ 1.5 with CI > 1; **failed** = RR_timely CI includes 1 *and* (F1 < 3 or F4 < 2); **mixed** = otherwise; **descriptive** = fewer than 15 adoption events in the agent-level table (underpowered).

## Result
*Run 2026-10-04 (round 1), after the prediction above.* Verdict mapping for replication periods: Amendment 2 in the card (F4 is untestable per period).

| Prediction (templated) | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 RR_timely (one cycle) ≥ 1.5, CI > 1 | 1.18 [0.86, 1.60] (49 adoptions) | 1 (synthetic nulls: CI > 1 in 0–10% of runs) | fail |
| P1b RR_timely (10 min) | 1.49 [0.22, 9.94] | 1 | — |
| F1 step (adoptions 30 min after / before the seed) | 13.67 (pre 3, post 41) | ≈ 1 field, < 1 pre-ramp, > 10 read-out-triggered (synthetic) | step |
| F2 other-room / same-room adoption | 0.04 (45 multi-room seeds) | ≈ 1 field, ≈ 0.3 nucleation | — |
| F3 adopters never exposed to a link before adopting | 0.04 (n = 54) | — | — |
| F4 late-reader read-locking | n = 2, ratio 4.24 | untestable below 10 | — |
| Waves | mean S 1.20, max 6, zero 40%; mean R 1.24; herded 5, never 28 | — | — |

Decision-rule-v2 label (pooled thresholds applied to this period): read-out (no timing).
**Verdict: failed** (RR CI includes 1).

## Scorecard (period-specific axes)
C: RR_timely vs 1 (seed-stratified, day-cluster CI); D: F1/F2/F3 signatures; H: rivals (status, share, size) pooled only. G, E, I: n/a for this period.

## Notes
- Data: `data/processed/H53-announcement-nucleation/` (`seeds.parquet`, `recipients.parquet`, `round1/period_G44.json`).
