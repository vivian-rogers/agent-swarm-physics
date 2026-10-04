# H53 × G51: Each agent: Maximize your assigned goal! ()

**Verdict:** failed — RR 1.05 [0.77, 1.43]; F1 18.00; mean S 0.77; R 2.36
**Role:** replication
**Period:** regime ? · mode ? · ? agents · ? active days · 237 seeds (first chat link per project, non-holdout days). Units (step changes, `period_units`): 51a 2026-07-06→2026-07-08 (goal_start); 51b 2026-07-09→2026-07-09 (ne:NE32; roster_join:GPT-5.6 Luna; roster_join:GPT-5.6 Sol; roster_join:GPT-5.6 Terra); 51c 2026-07-10→2026-07-16 (roster_join:Grok 4.5); 51d 2026-07-17→2026-07-23 (roster_join:Kimi K3); 51e 2026-07-24→2026-07-28 (roster_join:Claude Opus 5); 51f 2026-07-29→2026-08-04 (ne:NE38); 51g 2026-08-05→2026-08-21 (rooms:{#general, #focus}); 51h 2026-08-24→2026-08-27 (rooms:{#general}); 51i 2026-08-28→2026-08-31 (roster_join:GLM-5.3 Flash); 51j 2026-09-01→2026-09-02 (roster_join:Claude Fable 5.1); 51k 2026-09-03→2026-09-03 (ne:NE33; roster_join:Gemini 3.8 Flash; roster_join:Muse Spark 1.3); 51l 2026-09-04→2026-09-04 (ne:NE33; roster_join:GPT-6 Astra). Unit intercepts are not separate fits; the period is the unit (card, exception (d)).

## Why this period
Replication: the common estimator (card O1–O10) on every eligible period.

## Prediction
*Written 2026-10-04, before running on this period.*
*Templated replication prediction (card P1, P1b, P6, P10 applied here), written 2026-10-04 before running on this period.* 236 eligible seeds; median susceptible in-room recipients 24; mean uncommitted U 8.5; mean receptive R 2.4 (structural counts only). R averages ≥ 1 per seed; the timing test has some power if adoption events are not too rare.
- RR_timely (one cycle): 95% CI includes 1, or RR < 1.5 (card call: H53's P1 fails).
- F1 step ratio ≥ 3 would mark read-out-triggered waves; a ratio < 3 marks a pre-ramp (H28). Expected: 1.5–3.
- F4 read-locking ≥ 2 for late readers if adoptions are triggered at read-out. Expected: unclear.
- Decision rule v2 label: not "nucleation".
- Verdict rule (per period): **supported** = v2 label "nucleation" and RR_timely ≥ 1.5 with CI > 1; **failed** = RR_timely CI includes 1 *and* (F1 < 3 or F4 < 2); **mixed** = otherwise; **descriptive** = fewer than 15 adoption events in the agent-level table (underpowered).

## Result
*Run 2026-10-04 (round 1), after the prediction above.* Verdict mapping for replication periods: Amendment 2 in the card (F4 is untestable per period).

| Prediction (templated) | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 RR_timely (one cycle) ≥ 1.5, CI > 1 | 1.05 [0.77, 1.43] (145 adoptions) | 1 (synthetic nulls: CI > 1 in 0–10% of runs) | fail |
| P1b RR_timely (10 min) | 1.19 [0.46, 3.03] | 1 | — |
| F1 step (adoptions 30 min after / before the seed) | 18.00 (pre 6, post 108) | ≈ 1 field, < 1 pre-ramp, > 10 read-out-triggered (synthetic) | step |
| F2 other-room / same-room adoption | 0.41 (87 multi-room seeds) | ≈ 1 field, ≈ 0.3 nucleation | — |
| F3 adopters never exposed to a link before adopting | 0.01 (n = 181) | — | — |
| F4 late-reader read-locking | n = 5, ratio 8.62 | untestable below 10 | — |
| Waves | mean S 0.77, max 7, zero 57%; mean R 2.36; herded 2, never 144 | — | — |

Decision-rule-v2 label (pooled thresholds applied to this period): read-out (no timing).
**Verdict: failed** (RR CI includes 1).

## Scorecard (period-specific axes)
C: RR_timely vs 1 (seed-stratified, day-cluster CI); D: F1/F2/F3 signatures; H: rivals (status, share, size) pooled only. G, E, I: n/a for this period.

## Notes
- Data: `data/processed/H53-announcement-nucleation/` (`seeds.parquet`, `recipients.parquet`, `round1/period_G51.json`).
