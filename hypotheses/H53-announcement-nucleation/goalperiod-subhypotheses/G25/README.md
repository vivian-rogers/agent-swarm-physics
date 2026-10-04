# H53 × G25: Create a digital museum of 2025 (2025-12-29 → 2026-01-05)

**Verdict:** failed — RR 0.88 [0.45, 1.72]; F1 ∞ (no pre-seed adoption); mean S 1.71; R 2.38
**Role:** replication
**Period:** regime I · mode C · 10 agents · 5 active days · 22 seeds (first chat link per project, non-holdout days). Units (step changes, `period_units`): none. Unit intercepts are not separate fits; the period is the unit (card, exception (d)).

## Why this period
Replication: the common estimator (card O1–O10) on every eligible period.

## Prediction
*Written 2026-10-04, before running on this period.*
*Templated replication prediction (card P1, P1b, P6, P10 applied here), written 2026-10-04 before running on this period.* 21 eligible seeds; median susceptible in-room recipients 9; mean uncommitted U 4.9; mean receptive R 2.4 (structural counts only). R averages ≥ 1 per seed; the timing test has some power if adoption events are not too rare.
- RR_timely (one cycle): 95% CI includes 1, or RR < 1.5 (card call: H53's P1 fails).
- F1 step ratio ≥ 3 would mark read-out-triggered waves; a ratio < 3 marks a pre-ramp (H28). Expected: 1.5–3.
- F4 read-locking ≥ 2 for late readers if adoptions are triggered at read-out. Expected: unclear.
- Decision rule v2 label: not "nucleation".
- Verdict rule (per period): **supported** = v2 label "nucleation" and RR_timely ≥ 1.5 with CI > 1; **failed** = RR_timely CI includes 1 *and* (F1 < 3 or F4 < 2); **mixed** = otherwise; **descriptive** = fewer than 15 adoption events in the agent-level table (underpowered).

## Result
*Run 2026-10-04 (round 1), after the prediction above.* Verdict mapping for replication periods: Amendment 2 in the card (F4 is untestable per period).

| Prediction (templated) | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 RR_timely (one cycle) ≥ 1.5, CI > 1 | 0.88 [0.45, 1.72] (28 adoptions) | 1 (synthetic nulls: CI > 1 in 0–10% of runs) | fail |
| P1b RR_timely (10 min) | 0.01 [0.00, 5.83] | 1 | — |
| F1 step (adoptions 30 min after / before the seed) | ∞ (no pre-seed adoption) (pre 0, post 25) | ≈ 1 field, < 1 pre-ramp, > 10 read-out-triggered (synthetic) | step |
| F2 other-room / same-room adoption | n/a (0 multi-room seeds) | ≈ 1 field, ≈ 0.3 nucleation | — |
| F3 adopters never exposed to a link before adopting | 0.00 (n = 36) | — | — |
| F4 late-reader read-locking | n = 0 | untestable below 10 | — |
| Waves | mean S 1.71, max 8, zero 33%; mean R 2.38; herded 3, never 15 | — | — |

Decision-rule-v2 label (pooled thresholds applied to this period): seed-locked field (F4 untestable here, so a "seed-locked field" label only means read-out locking could not be shown).
**Verdict: failed** (RR CI includes 1).

## Scorecard (period-specific axes)
C: RR_timely vs 1 (seed-stratified, day-cluster CI); D: F1/F2/F3 signatures; H: rivals (status, share, size) pooled only. G, E, I: n/a for this period.

## Notes
- Data: `data/processed/H53-announcement-nucleation/` (`seeds.parquet`, `recipients.parquet`, `round1/period_G25.json`).
