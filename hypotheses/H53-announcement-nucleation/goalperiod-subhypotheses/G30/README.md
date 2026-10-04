# H53 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-16)

**Verdict:** failed — RR 0.80 [0.53, 1.18]; re-link step 1.29; 8 re-seeds
**Role:** native
**Period:** regime I · mode C · 12 agents · 5 active days · 11 seeds (first chat link per project, non-holdout days). Units (step changes, `period_units`): 30a 2026-02-09→2026-02-09 (goal_start); 30b 2026-02-10→2026-02-13 (ne:NE10). Unit intercepts are not separate fits; the period is the unit (card, exception (d)).

## Why this period
Native test: see the prediction below.

## Prediction
*Written 2026-10-04, before running on this period.*
**Native test (re-announcements of one shared repo).** #30 has one shared park repo linked ~160 times by 11 agents (and a second repo ~95 times). Every chat link to one of these two projects after ≥ 60 active min without a link to it is a **re-seed**. Project attractiveness is then held fixed. Outcome per re-seed: *returners*, in-room agents without the project as their W = 15 label in the previous 60 active min who take it within 60 active min after their own read-out; wave = returners within 2 h.
- **N30-a:** return-wave size rises with R (NB slope on log(1+R) with log(1+N) control > 0, 95% CI > 0). Credence 0.2.
- **N30-b:** agent-level RR_timely for returning ≥ 1.5 with CI > 1. Credence 0.2.
- **N30-c (pre-trend):** returns in the 30 active min after re-seeds / before ≥ 2. Credence 0.35 (H28: links ride ongoing bursts).
- **N30-d (descriptive):** each of H27's four #30 onsets lies within 60 min after a re-seed.
- The replication estimator on #30's 11 first-link seeds: templated, underpowered (R mean ≈ 0.6).

*Templated replication prediction (card P1, P1b, P6, P10 applied here), written 2026-10-04 before running on this period.* 11 eligible seeds; median susceptible in-room recipients 10; mean uncommitted U 0.9; mean receptive R 0.6 (structural counts only). R averages below 1 per seed, so at most about one agent per seed can be receptive; H53 then predicts small waves, and the timing test has little power.
- RR_timely (one cycle): 95% CI includes 1, or RR < 1.5 (card call: H53's P1 fails).
- F1 step ratio ≥ 3 would mark read-out-triggered waves; a ratio < 3 marks a pre-ramp (H28). Expected: 1.5–3.
- F4 read-locking ≥ 2 for late readers if adoptions are triggered at read-out. Expected: unclear.
- Decision rule v2 label: not "nucleation".
- Verdict rule (per period): **supported** = v2 label "nucleation" and RR_timely ≥ 1.5 with CI > 1; **failed** = RR_timely CI includes 1 *and* (F1 < 3 or F4 < 2); **mixed** = otherwise; **descriptive** = fewer than 15 adoption events in the agent-level table (underpowered).

## Result
*Run 2026-10-04 (round 1), after the prediction above.* Verdict mapping for replication periods: Amendment 2 in the card (F4 is untestable per period).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N30-a return-wave size rises with R (slope CI > 0) | 8 re-seeds after ≥ 60-min lulls (2 projects); 6 with ≥ 3 susceptibles; slope -0.13 [-3.01, 2.76]; mean wave 4.7, mean R 0.5 | fail (untestable at n = 6) |
| N30-b RR_timely for returning ≥ 1.5, CI > 1 | 0.80 [0.53, 1.18] (30 returns of 48 at-risk readers) | fail |
| N30-c returns 30 min after / before re-seeds ≥ 2 | 22 / 17 = 1.29 | fail (as I predicted: re-links ride ongoing bursts, H28) |
| N30-d H27's four #30 onsets follow a re-seed within 60 min | minutes since the last re-seed: [16.8, -9.8, 49.4, 33.4]; 3/4 within 0–60 min | descriptive |

**Replication estimator on this period (context):**

| Prediction (templated) | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 RR_timely (one cycle) ≥ 1.5, CI > 1 | 0.70 [0.44, 1.10] (25 adoptions) | 1 (synthetic nulls: CI > 1 in 0–10% of runs) | fail |
| P1b RR_timely (10 min) | n/a | 1 | — |
| F1 step (adoptions 30 min after / before the seed) | ∞ (no pre-seed adoption) (pre 0, post 23) | ≈ 1 field, < 1 pre-ramp, > 10 read-out-triggered (synthetic) | step |
| F2 other-room / same-room adoption | n/a (0 multi-room seeds) | ≈ 1 field, ≈ 0.3 nucleation | — |
| F3 adopters never exposed to a link before adopting | 0.00 (n = 25) | — | — |
| F4 late-reader read-locking | n = 0 | untestable below 10 | — |
| Waves | mean S 2.27, max 10, zero 55%; mean R 0.64; herded 4, never 6 | — | — |

Decision-rule-v2 label (pooled thresholds applied to this period): seed-locked field (F4 untestable here, so a "seed-locked field" label only means read-out locking could not be shown).
**Verdict: failed** (re-announcing the same repo brings back many agents, but neither the receptive count nor read-out timing predicts who returns, and returns do not step up at re-links).

## Scorecard (period-specific axes)
C: RR_timely for returns vs 1 (fail). D: no step at re-links (fail). Project attractiveness held fixed (within-project design), so this is the cleanest test of timing; it is also tiny (8 re-seeds).

## Notes
- Data: `data/processed/H53-announcement-nucleation/` (`seeds.parquet`, `recipients.parquet`, `round1/period_G30.json`).
