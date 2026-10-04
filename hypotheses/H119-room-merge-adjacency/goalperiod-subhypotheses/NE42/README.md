# H119 × NE42: #best + #rest merged (05-04) and split back (05-11)

**Verdict:** failed
**Role:** exploratory (native)
**Period:** regime III · #39 (04-27 → 05-01) | #40 (05-04 → 05-08, merged in #universe-coordination; GPT-5 alone in #rest) | #41 (05-11 → 05-15) · ~14 eligible agents · goal changes at both boundaries (#40 shared objective).

## Why this period
An A-B-A of the read path with known membership at every minute: 40 cross pairs switch off → on → off, 51 within pairs stay on, 10 GPT-5 × #rest pairs switch on → off → on. The cleanest adjacency intervention in the non-holdout data.

## Prediction
*Written 2026-10-04 22:06 UTC, before running on this period.*
- N1 (P1, P2): M > 0 with CI excluding 0 [0.65]; M_D > 0 [0.55]; J_x(#39), J_x(#41) CIs include 0 [0.55]; Rm CI includes 0 and Rm < M/2 [0.6].
- N2 (P5): merged-day mean J_x > unmerged-day mean (Mann–Whitney p < 0.05) [0.55]; J_x(05-04) above the #39 daily range [0.4].
- N3 (P6): in #40, J^R_x > 0 [0.6], J^R_x − J^U_x > 0 [0.55]; J^U_x CI includes 0 in all three weeks [0.55].
- N4 (P4): GPT-5 × #rest coupling lower in #40 than the #39/#41 mean [0.4].
- N5 (P3): J_x(#40) − J_w(#40) CI includes 0 [0.45].
- Verdict (card): supported if N1's M and Rm clauses and N3's first two clauses hold; failed (HH kill) if M's CI includes 0 or M ≤ 0, or Rm > 0 with CI excluding 0 and Rm ≥ M/2; mixed otherwise.

## Result
*Run 2026-10-04 22:43–22:46 UTC (exploratory, non-holdout).*

| Prediction | Observed (95% CI) | Verdict |
| --- | --- | --- |
| N1 M > 0 | −0.019 [−0.127, 0.088] | **failed (HH kill)** |
| N1 M_D > 0 | 0.024 [−0.076, 0.125] | failed |
| N1 J_x(#39), J_x(#41) ≈ 0 | 0.078 [−0.06, 0.21], 0.092 [−0.01, 0.20] | pass (trivially) |
| N1 Rm ≈ 0 | 0.014 [−0.143, 0.172] | pass (nothing to remain) |
| N2 merged-day J_x > unmerged | 0.002 vs 0.126, Mann–Whitney p 0.95 | failed |
| N3 J^R_x > 0 in #40 | −0.23 [−0.44, −0.02] | failed |
| N3 J^R_x − J^U_x > 0 in #40 | 0.15 [−0.19, 0.48] | failed (n.s.) |
| N3 J^U_x ≈ 0 all weeks | −1.18, −0.38, −0.40 (all CIs below 0) | failed (in-flight term negative) |
| N4 GPT-5 mirror arm | n/a (GPT-5 not eligible) | n/a |
| N5 P_m ≈ 0 | 0.056 [−0.010, 0.122] | pass (trivially) |
| Relabel null | p(M) 0.43, p(M_D) 0.39 (499 partitions) | — |

E1 class couplings (per pair): within −0.03 / 0.01 / 0.14, cross 0.08 / 0.07 / 0.09 (#39 / #40 / #41). Full-J block means (symmetric): within −0.05 / 0.07 / 0.23, cross −0.02 / −0.02 / −0.02. E2 within-class read minus in-flight: 0.29 [−0.07, 0.66] / 0.08 [−0.16, 0.31] / **0.47 [0.27, 0.66]**. 11 eligible agents (62 within, 48 cross directed pairs); minute co-location confirms the classes (cross 0.00 / 1.00 / 0.00).

**Reading.** The merged week shows no coupling of any class: neither the new cross pairs nor the old within pairs couple in #40, by either estimator. Within-room coupling appears in #41 (full-J 0.23 ± 0.04; E2 0.47). The adjacency switched on, but the per-pair coupling in the 14-agent room fell below detection, as H05's attention dilution and H51's g_lag collapse (0.144 → 0.003 → 0.189) predict. The HH's kill rule fires on M. Synthetic power for M at J = 0.3 was 0.95, so real per-pair minute-scale couplings in #40 are well below 0.3.

Post hoc (dry run of `confirm.py`, labelled): the #40 → #41 cut-arm DiD (cross minus within change, 13 agents over the two weeks) is −0.094 [−0.184, −0.005]: coupling separates by class only after the split.

## Scorecard (period-specific axes)
E: the A-B-A fails to show the predicted rise (powered: 0.95 at J 0.3). G: the known adjacency is not recovered in #40; within-room coupling is recovered in #41. H: R-dilution beats the adjacency-gating model in the merged week; R-memory and R-partition untestable (no coupling to remain).

## Notes
