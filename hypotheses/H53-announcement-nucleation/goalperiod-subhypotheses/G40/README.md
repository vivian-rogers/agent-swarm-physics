# H53 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-11)

**Verdict:** failed — hub wave 8 (pred. 0.5) at R = 0; 14% pre/unexposed; 71% in hour 1
**Role:** native
**Period:** regime III · mode C · 15 agents · 5 active days · 17 seeds (first chat link per project, non-holdout days). Units (step changes, `period_units`): none. Unit intercepts are not separate fits; the period is the unit (card, exception (d)).

## Why this period
Native test: see the prediction below.

## Prediction
*Written 2026-10-04, before running on this period.*
**Native test (negative control: a hub frozen at the kickoff).** H31 found #40's hub project frozen at the kickoff (already shared in the first window). Hub = the project with the most W = 30 labelled agent-windows on #40's first day. H53 says nothing nucleates here: the goal names the hub.
- **N40-a:** ≥ 50% of agents who ever hold the hub label in #40 took it before the hub's first chat link in #40, or without any link to it in their context before adopting (pre-seed or unexposed adopters). Credence 0.55.
- **N40-b:** hub adoptions cluster in the first active hour of day 1 (≥ 50% of hub adopters), i.e. lock to the kickoff, not to a link. Credence 0.55.
- **N40-c:** the hub seed's wave is not larger than M_N predicts for #40 (no nucleation excess). Credence 0.6.
- The replication estimator on #40's other seeds (agents' worlds): templated.

*Templated replication prediction (card P1, P1b, P6, P10 applied here), written 2026-10-04 before running on this period.* 17 eligible seeds; median susceptible in-room recipients 12; mean uncommitted U 1.2; mean receptive R 0.5 (structural counts only). R averages below 1 per seed, so at most about one agent per seed can be receptive; H53 then predicts small waves, and the timing test has little power.
- RR_timely (one cycle): 95% CI includes 1, or RR < 1.5 (card call: H53's P1 fails).
- F1 step ratio ≥ 3 would mark read-out-triggered waves; a ratio < 3 marks a pre-ramp (H28). Expected: 1.5–3.
- F4 read-locking ≥ 2 for late readers if adoptions are triggered at read-out. Expected: unclear.
- Decision rule v2 label: not "nucleation".
- Verdict rule (per period): **supported** = v2 label "nucleation" and RR_timely ≥ 1.5 with CI > 1; **failed** = RR_timely CI includes 1 *and* (F1 < 3 or F4 < 2); **mixed** = otherwise; **descriptive** = fewer than 15 adoption events in the agent-level table (underpowered).

## Result
*Run 2026-10-04 (round 1), after the prediction above.* Verdict mapping for replication periods: Amendment 2 in the card (F4 is untestable per period).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N40-a ≥ 50% of hub adopters took it before its first chat link or without a link in context | pre-seed 7%, unexposed 14%, either 14% of 14 | fail: the hub was link-seeded |
| N40-b ≥ 50% of hub adoptions in the first active hour of day 1 | 71%; the hub's first link came 2.4 min after day start, from an agent | pass |
| N40-c hub wave not larger than M_N predicts | S = 8 vs predicted mean 0.52 (P(S ≥ obs) = 0.0004); receptive R = 0 of 10 | fail: an 8-agent wave with R = 0 |

**Replication estimator on this period (context):**

| Prediction (templated) | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 RR_timely (one cycle) ≥ 1.5, CI > 1 | 0.92 [0.92, 0.92] (8 adoptions) | 1 (synthetic nulls: CI > 1 in 0–10% of runs) | fail |
| P1b RR_timely (10 min) | 1.00 [1.00, 1.00] | 1 | — |
| F1 step (adoptions 30 min after / before the seed) | 7.00 (pre 1, post 7) | ≈ 1 field, < 1 pre-ramp, > 10 read-out-triggered (synthetic) | step |
| F2 other-room / same-room adoption | 0.00 (17 multi-room seeds) | ≈ 1 field, ≈ 0.3 nucleation | — |
| F3 adopters never exposed to a link before adopting | 0.00 (n = 8) | — | — |
| F4 late-reader read-locking | n = 0 | untestable below 10 | — |
| Waves | mean S 0.47, max 8, zero 94%; mean R 0.53; herded 1, never 14 | — | — |

Decision-rule-v2 label (pooled thresholds applied to this period): seed-locked field (F4 untestable here, so a "seed-locked field" label only means read-out locking could not be shown).
**Verdict: failed** (the 'frozen' hub was not a link-free field: an agent linked it 2 minutes into the kickoff and exposed agents adopted it within the hour, in a wave far larger than room size predicts, while its receptive count was 0. Neither the frozen-field contrast nor 'R sets wave size' holds).

## Scorecard (period-specific axes)
G: H31's kickoff-frozen hub is re-read as a kickoff-time link seed. E: the kickoff acts as a field that makes the first link land (a quench-like start, cf. H54). H: R does not predict the biggest #40 wave.

## Notes
- Data: `data/processed/H53-announcement-nucleation/` (`seeds.parquet`, `recipients.parquet`, `round1/period_G40.json`).
