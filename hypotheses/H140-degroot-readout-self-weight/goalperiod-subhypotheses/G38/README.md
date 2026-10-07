# H140 × G38: the long shared week, two rooms (#38, 2026-04-02 → 2026-04-27)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime III · mode C · 12 agents · two rooms (#best / #rest, room-specific kickoffs) · 17 days. Units from `period_units`.

## Why this period
The longest non-reserved regime-III shared-goal week, with computer-use context segments (so s_self exists) and H113's field identification (#38 is a scored period in both models). Two rooms give two read streams on the same days.

## Prediction
*Written 2026-10-07 ~10:50 UTC, before running on this period. Seen: H113's #38 information values (1.07 → 1.70 → 1.13 bits over k bins); no s_self value and no self-weight.*
- **P1:** ŵ₁ ∈ [0.5, 1.5] with CI above 0. Credence 0.15.
- **P2:** â ∈ [0.15, 0.40], CI excluding 1. Credence 0.6.
- **P3:** ŵ₂ (call-gap term) > 0 with CI. Credence 0.5.
- **P4:** γ̂_F / γ̂₁ ≤ 0.5 and read − in-flight contrast > 0. Credence 0.65.
- Counts against: the card's kill clauses evaluated on this unit (per-unit verdicts are descriptive for the kill; the pool decides).

## Result
Data: `data/processed/H140-degroot-readout-self-weight/G38/`, results `results/units_G38.json`. Run 2026-10-07 (exploration data; reserved days never enter the scheme). Estimator: Amendment A1 spec (primary) and the registered spec; agent-day cluster bootstrap, 300 draws.

| Prediction | Observed (bge; gte) | Verdict |
| --- | --- | --- |
| P1 ŵ₁ ∈ [0.5, 1.5], CI > 0 | 38a (416 rows): −0.62 [−1.19, −0.20]; −0.36 [−0.74, 0.08]. Registered spec −0.17 [−0.58, 0.18]. 38b–38e have 33–137 rows (pool only). DL pool of the 5 units −0.62 [−1.09, −0.14]; gte −0.31 [−0.68, 0.05] | failed |
| P2 â ∈ [0.15, 0.40] | 38a â 0.46 [0.20, 0.83], but not identified (contrast −0.037 [−0.155, 0.067]); not scored | not scored |
| P3 ŵ₂ > 0 (registered) | 0.22 [−1.45, 1.77] | failed |
| P4 γ̂_F/γ̂₁ ≤ 0.5, contrast > 0 | γ̂_F/γ̂₁ 1.66; contrast CI includes 0 | failed |

- N2 permutation null for 38a: null mean −0.29 (sd 0.19); the observed −0.62 has p = 0.08. Part of the negative slope is structural (the null itself sits below 0).
- In #38 s_self is high (median 0.82: few items arrive per own call), so its range is narrow.

## Scorecard (period-specific axes)
C 0, D 0, H 0 (the convergence placebo fails here).

## Notes
- The room-kickoff directions are projected out per room (P_c uses the reader's room kickoff).
