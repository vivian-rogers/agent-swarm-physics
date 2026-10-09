# H147 × NE41: forced context erasures of memeplex hosts in #51 (07-06 → 09-04)

**Verdict:** supported
**Role:** exploratory
**Period:** #51 non-reserved days; 14,593 forced erasures (F, `reset_forced`, set by the 41-call cap) and 15,100 placebo calls (P, call 21 of a segment of ≥ 40 calls). The test spans the whole period (strata agent × unit).

## Why this period
NE41's erasures arrive on a clock set by the call cap, not by content, so each one is a quasi-random scramble of the host's context. If a memeplex lives in its hosts' contexts, a wipe should lower the host's expression of it (Kolchinsky–Wolpert value of the context information).

## Prediction
*Written 2026-10-09 (card), before running.* P1: for distributed memeplexes (h_K < 0.5), ΔV_K,F within ±5% of placebo, κ not identified or ≈ 0; falsified if ≥ 1/2 lose ≥ 10% with the CI below 0. Amendment A1 (before real data): ΔV is measured as the expression share (rate form), with both a bootstrap CI and the pseudo-pattern band. K1: the wiped host's own output dips.

## Result
| Prediction | Observed (95% CI) | Null | Verdict |
| --- | --- | --- | --- |
| K1 self-dip | own commits −0.40 [−0.42, −0.36]; statements −0.62 [−0.64, −0.59] | placebo calls | passes |
| P1 falsifier | 1/14 (K06 −0.17 [−0.27, −0.06]) | placebo calls + 100 pseudo-patterns | not met |
| P1 median | +0.05 [+0.00, +0.12] over 14 memeplexes | same | at the +5% edge |
| others' response | 0/14 CIs exclude 0 | same | no absorption or loss detected |
| κ_K,F | I_K identified for 1/14 (K05) | permutation floor | not identified |

Post hoc: K03, K12 and K13 gain share after a wipe beyond both bands (re-expression). Synthetic power: 0.90 at −30%, 0.65 at −20%; size 0.00.

## Scorecard (period-specific axes)
E 1 (NE41 used as an intervention) · F 2 · H 1 (wipes cost nothing: W_artifact/W_egregore over context-held).

## Notes
- 2026-10-09: the card's count forms fail here: a forced erasure halves the host's statements in calls 1…20 (0.70 vs 1.47), so every pattern's count halves (synthetic). Amendment A1 fixed this before real data.
