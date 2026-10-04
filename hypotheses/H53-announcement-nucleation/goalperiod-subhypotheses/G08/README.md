# H53 × G08: Design the AI Village benchmark for open-ended goal pursuit – and test yourselves on it! (2025-07-18 → 2025-08-13)

**Verdict:** descriptive — RR 0.32 [0.03, 2.88]; F1 ∞ (no pre-seed adoption); mean S 0.13; R 1.52
**Role:** replication
**Period:** regime I · mode C · 4 agents · 18 active days · 61 seeds (first chat link per project, non-holdout days). Units (step changes, `period_units`): none. Unit intercepts are not separate fits; the period is the unit (card, exception (d)).

## Why this period
Replication: the common estimator (card O1–O10) on every eligible period.

## Prediction
*Written 2026-10-04, before running on this period.*
*Templated replication prediction (card P1, P1b, P6, P10 applied here), written 2026-10-04 before running on this period.* 60 eligible seeds; median susceptible in-room recipients 3; mean uncommitted U 2.5; mean receptive R 1.5 (structural counts only). R averages ≥ 1 per seed; the timing test has some power if adoption events are not too rare.
- RR_timely (one cycle): 95% CI includes 1, or RR < 1.5 (card call: H53's P1 fails).
- F1 step ratio ≥ 3 would mark read-out-triggered waves; a ratio < 3 marks a pre-ramp (H28). Expected: 1.5–3.
- F4 read-locking ≥ 2 for late readers if adoptions are triggered at read-out. Expected: unclear.
- Decision rule v2 label: not "nucleation".
- Verdict rule (per period): **supported** = v2 label "nucleation" and RR_timely ≥ 1.5 with CI > 1; **failed** = RR_timely CI includes 1 *and* (F1 < 3 or F4 < 2); **mixed** = otherwise; **descriptive** = fewer than 15 adoption events in the agent-level table (underpowered).

## Result
*Run 2026-10-04 (round 1), after the prediction above.* Verdict mapping for replication periods: Amendment 2 in the card (F4 is untestable per period).

| Prediction (templated) | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 RR_timely (one cycle) ≥ 1.5, CI > 1 | 0.32 [0.03, 2.88] (7 adoptions) | 1 (synthetic nulls: CI > 1 in 0–10% of runs) | fail |
| P1b RR_timely (10 min) | 1.00 [1.00, 1.00] | 1 | — |
| F1 step (adoptions 30 min after / before the seed) | ∞ (no pre-seed adoption) (pre 0, post 6) | ≈ 1 field, < 1 pre-ramp, > 10 read-out-triggered (synthetic) | step |
| F2 other-room / same-room adoption | n/a (0 multi-room seeds) | ≈ 1 field, ≈ 0.3 nucleation | — |
| F3 adopters never exposed to a link before adopting | 0.00 (n = 8) | — | — |
| F4 late-reader read-locking | n = 0 | untestable below 10 | — |
| Waves | mean S 0.13, max 2, zero 88%; mean R 1.52; herded 1, never 54 | — | — |

Decision-rule-v2 label (pooled thresholds applied to this period): seed-locked field (F4 untestable here, so a "seed-locked field" label only means read-out locking could not be shown).
**Verdict: descriptive** (underpowered (< 15 adoptions or SE not estimable)).

## Scorecard (period-specific axes)
C: RR_timely vs 1 (seed-stratified, day-cluster CI); D: F1/F2/F3 signatures; H: rivals (status, share, size) pooled only. G, E, I: n/a for this period.

## Notes
- Data: `data/processed/H53-announcement-nucleation/` (`seeds.parquet`, `recipients.parquet`, `round1/period_G08.json`).
