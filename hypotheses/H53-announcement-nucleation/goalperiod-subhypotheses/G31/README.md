# H53 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** mixed — AUC(R) 0.70 vs share 0.76; largest waves at R = 1; F1 5.8
**Role:** native
**Period:** regime I · mode F · 12 agents · 5 active days · 34 seeds (first chat link per project, non-holdout days). Units (step changes, `period_units`): 31a 2026-02-16→2026-02-17 (goal_start); 31b 2026-02-18→2026-02-18 (roster_join:Claude Sonnet 4.6); 31c 2026-02-19→2026-02-19 (ne:NE29; roster_leave:Claude 3.7 Sonnet); 31d 2026-02-20→2026-02-20 (ne:NE11). Unit intercepts are not separate fits; the period is the unit (card, exception (d)).

## Why this period
Native test: see the prediction below.

## Prediction
*Written 2026-10-04, before running on this period.*
**Native test (free week: H11's waves vs H06's private projects).** #31 is the clearest herding week (H11; the time-capsule repo reached 11 agents; H27: 4 onsets) and also a week of mostly private projects (H06: singletons 0.79–0.91). Structural note: only ~15% of recipients are uncommitted here, so R averages ≈ 0.5 per seed.
- **N31-a:** ≥ 70% of #31's eligible seeds never herd (max k ≤ 1). Credence 0.7.
- **N31-b:** AUC of R for herded vs never-herded seeds ≥ 0.65. Credence 0.25.
- **N31-c:** the largest 2-h wave in #31 comes from a seed with R ≥ 2. Against: the largest wave at R ≤ 1 (big waves without a receptive crowd). Credence 0.3.
- **N31-d:** herded seeds show a step (F1 ≥ 3); against: a pre-ramp (H28). Credence 0.35.
- **N31-e:** RR_timely within #31: CI includes 1 (33 seeds, low R). Credence it is > 1 with CI: 0.15.

*Templated replication prediction (card P1, P1b, P6, P10 applied here), written 2026-10-04 before running on this period.* 33 eligible seeds; median susceptible in-room recipients 10; mean uncommitted U 1.0; mean receptive R 0.5 (structural counts only). R averages below 1 per seed, so at most about one agent per seed can be receptive; H53 then predicts small waves, and the timing test has little power.
- RR_timely (one cycle): 95% CI includes 1, or RR < 1.5 (card call: H53's P1 fails).
- F1 step ratio ≥ 3 would mark read-out-triggered waves; a ratio < 3 marks a pre-ramp (H28). Expected: 1.5–3.
- F4 read-locking ≥ 2 for late readers if adoptions are triggered at read-out. Expected: unclear.
- Decision rule v2 label: not "nucleation".
- Verdict rule (per period): **supported** = v2 label "nucleation" and RR_timely ≥ 1.5 with CI > 1; **failed** = RR_timely CI includes 1 *and* (F1 < 3 or F4 < 2); **mixed** = otherwise; **descriptive** = fewer than 15 adoption events in the agent-level table (underpowered).

## Result
*Run 2026-10-04 (round 1), after the prediction above.* Verdict mapping for replication periods: Amendment 2 in the card (F4 is untestable per period).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N31-a ≥ 70% of eligible seeds never herd | 18/33 = 55% never; 10 herded | fail (more herding than predicted) |
| N31-b AUC(R) herded vs never ≥ 0.65 | R 0.70; uncommitted U 0.64; current share 0.76; room size 0.41; status 0.62 | pass (small: 10 vs 18; share does better) |
| N31-c largest 2-h wave from a seed with R ≥ 2 | top waves S = [7, 7, 6, 5, 5] at R = [1, 1, 1, 0, 2] | fail: the largest waves had R = 1 |
| N31-d herded seeds show a step (F1 ≥ 3) | 23 / 4 = 5.75 | pass |
| N31-e RR_timely CI includes 1 | see replication row below | as predicted |

**Replication estimator on this period (context):**

| Prediction (templated) | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 RR_timely (one cycle) ≥ 1.5, CI > 1 | 0.84 [0.64, 1.10] (37 adoptions) | 1 (synthetic nulls: CI > 1 in 0–10% of runs) | fail |
| P1b RR_timely (10 min) | 207378515972270.25 [6184008765000.64, 6954364154569005.00] | 1 | — |
| F1 step (adoptions 30 min after / before the seed) | 5.60 (pre 5, post 28) | ≈ 1 field, < 1 pre-ramp, > 10 read-out-triggered (synthetic) | step |
| F2 other-room / same-room adoption | n/a (0 multi-room seeds) | ≈ 1 field, ≈ 0.3 nucleation | — |
| F3 adopters never exposed to a link before adopting | 0.00 (n = 49) | — | — |
| F4 late-reader read-locking | n = 0 | untestable below 10 | — |
| Waves | mean S 1.48, max 7, zero 55%; mean R 0.55; herded 10, never 18 | — | — |

Decision-rule-v2 label (pooled thresholds applied to this period): seed-locked field (F4 untestable here, so a "seed-locked field" label only means read-out locking could not be shown).
**Verdict: mixed** (herded seeds had higher R than never-herded ones (AUC 0.70) and waves step up at the link, but the biggest waves came from seeds with only one receptive agent, and read-out timing did not raise individual adoption).

## Scorecard (period-specific axes)
G: H11's #31 waves are recovered as herded seeds (10 of 33). H: current share beats R as a predictor of herding. D: step at the link holds.

## Notes
- Data: `data/processed/H53-announcement-nucleation/` (`seeds.parquet`, `recipients.parquet`, `round1/period_G31.json`).
