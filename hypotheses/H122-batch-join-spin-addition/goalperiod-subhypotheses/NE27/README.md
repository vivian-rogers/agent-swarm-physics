# H122 × NE27: batch join of GPT-5, Grok 4 and Claude Opus 4.1 (2025-08-18), #10 (regime I)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime I · day 1 = #10 kickoff · PRE 08-06 … 08-12 (#8; #9 is held out) · P12 08-18, 08-19 · F37 08-20 … 08-26 (5 d; #11 starts 08-25) · N 4 → 7.

## Why this period
The batch join the HH names. It nearly doubles N (4 → 7), so the dilution term is large here ((7/4)^−0.66 ≈ 0.69 on the read coefficients). Three confounds are built in: the #10 kickoff on day 1, NE03 (chat context fetch limited) from 08-20 (the first fitting day), and the #11 kickoff on 08-25.

## Prediction
*Written 2026-10-04 22:22 UTC, before running on this period.*
- **P2 (card, credence 0.5):** J_N (F37) CI includes 0 (regime I has no hop-1 read-out coupling, H67); MC ≥ MJ on P12; and NE27's P12 shift δ_P12 lies inside the range of δ_P12 at non-holdout regime-I kickoffs without a join (kickoff-matched placebo): the incumbents' step is the kickoff's, not the join's.
- **Kill (as in the card):** MC beats MJ with CI < 0. In regime I this outcome is expected and would also count for P2.
- **Dilution (P5):** M0D beats M0 on P12 (credence 0.45 here; the N change is the largest of any event).

## Result
| Event | incumbents | P12 calls (with newcomer read) | ΔLL MC−MJ [95%] | ΔLL MJ_pl−MJ | ΔLL M_same−MJ | ΔLL M0−M0D | J_N F37 [95%] | J_N P12 [95%] | δ F37 | R²_h MC / MJ | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NE27 | 4 | 2063 (471) | -0.52 [-2.07, +0.93] | +0.05 [-1.30, +1.48] | +2.02 [-1.26, +5.96] | +0.25 [-0.11, +0.79] | +0.103 [-0.029, +0.230] | +0.063 [-0.069, +0.177] | +0.09 | 0.14 / 0.09 | mixed |

ΔLL in nats per 1,000 incumbent calls on days 1–2 (positive: the second model is better). J in logit per newcomer read. Data: `data/processed/H122-batch-join-spin-addition/results/events.parquet`.

**Kickoff-matched placebo** (12 non-holdout regime-I kickoffs without a join): δ_P12 range [-0.93, +0.47], median +0.10; NE27 δ_P12 = +0.21 (percentile 75).

## Scorecard (period-specific axes)
C, D, E (with the kickoff placebo as the exogenous-field control).

## Notes
- Regime-I talk happens at scheduled chat-mode calls; a hop-1 read-out estimator may miss a later response (H67 caveat).
