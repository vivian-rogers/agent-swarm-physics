# H36 × NE34: goal changes (all non-holdout kickoffs, #2–#51)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** spans #2–#51 (35 non-holdout kickoffs; transitions as the object, exception c)

## Why this test
The primary transition class: every goal kickoff whose day 0 is not held out.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's P1: the physics alarm (Z_phys ≥ 2.0) hits ≤ 40% of goal changes, window FAR ≈ 15–30%, AUC(Z_phys, day 0) < 0.65 [0.65]; R1 (content centroid shift) AUC ≥ 0.8 and beats Z_phys [0.75]; content members respond more than activity members [0.6]; hits peak on day 0/+1, not day −1 [0.7]. Synthetic power (Amendment 1): a miss rules out S6-sized content reorganizations but is uninformative about S1-sized activity ones.

**Verdict rule:** Supported if hit rate ≥ 0.6, window FAR ≤ 0.25, AUC ≥ 0.70 with CI excluding 0.5, random-date p < 0.05 and Monday-placebo FAR ≤ 0.25; failed if AUC ≤ 0.60 or random-date p > 0.10; mixed otherwise.

## Result
<!-- RESULT -->
| Score | hit rate (n) | window FAR | per-day FAR | AUC day 0 [95% CI] | AUC window max | random-date p |
| --- | --- | --- | --- | --- | --- | --- |
| Z_phys | 0.30 (33) | 0.10 | 0.033 | 0.68 [0.56, 0.79] | 0.66 | 0.032 |
| Z_I | 0.27 (33) | 0.11 | 0.033 | 0.68 [0.56, 0.80] | 0.63 | – |
| Z_chi | 0.24 (33) | 0.10 | 0.033 | 0.62 [0.48, 0.74] | 0.60 | – |
| Z_C | 0.30 (33) | 0.13 | 0.049 | 0.65 [0.52, 0.77] | 0.63 | – |
| Z_act | 0.27 (33) | 0.11 | 0.033 | 0.55 [0.41, 0.66] | 0.54 | 0.312 |
| Z_cont | 0.42 (33) | 0.00 | 0.000 | 0.77 [0.67, 0.86] | 0.71 | 0.002 |
| R1 | 0.58 (33) | 0.21 | 0.066 | 0.95 [0.90, 0.98] | 0.71 | 0.001 |
| R2 | 0.45 (33) | 0.23 | 0.082 | 0.59 [0.46, 0.71] | 0.67 | 0.157 |
| R1_or_Zphys | 0.73 (33) | 0.31 | 0.098 | 0.83 [0.72, 0.92] | 0.78 | 0.001 |

Monday-placebo window FAR (Z_phys): 0.18; AUC(day 0 vs Monday placebos) 0.62. Rival AUC difference (Z_phys − R1, day 0): -0.26 [-0.39, -0.13].
Unconfounded goal changes only (n = 26): Z_phys hit 0.27, AUC 0.71.

Per-event table: `data/processed/H36-reorganization-alarm/event_table.parquet`; figure `figures/event_locked.pdf`.

**Prediction check:** P1 hit ≤ 40% held (0.30) and AUC came out slightly above the predicted < 0.65 (0.68); window FAR was lower than predicted (0.10 vs 0.15–0.30). R1 AUC ≥ 0.8 and beats Z_phys: held (0.95; difference −0.26, CI excludes 0). Content > activity: held (0.77 vs 0.55). Timing: 7 of 10 hits first fire on day 0/+1, 3 on day −1 (post hoc PH1: day −1 AUC 0.69 vs placebo, 0.68 vs Friday placebos; a weak end-of-goal signal, not predicted). Verdict by the pre-registered rule: **mixed** (hit rate below 0.6; not failed because AUC 0.68 and random-date p 0.03).
<!-- /RESULT -->
