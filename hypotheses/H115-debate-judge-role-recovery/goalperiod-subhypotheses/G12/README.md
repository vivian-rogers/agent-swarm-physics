# H115 × G12: Form two teams and debate each other, while one agent judges (2025-09-01 → 09-05)

**Verdict:** failed
**Role:** native (exploratory)
**Period:** regime I · mode M (teams) · 7 agents · one room · 5 days (units 12a 09-01..09-04, 12b 09-05 at NE04). Ten Asian-Parliamentary debates on 09-01..09-04 (none on 09-05), each with its own judge and re-drafted teams; DQ6 `phase` windows pre / deb / post (debate episodes 13–47 min, 170–630 calls each).

## Why this period
The only period with a one-way role (a judge who listens and rules) that rotates across ten independent episodes with ground truth in DQ6. HH353 ranks it first for blind role recovery; models 02 and 10 are this period's top-ranked models in `goal-periods.md`.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* The card's P1–P3 apply as written:
- **P1 (primary, blind):** the judge has the largest read-gated sink score S^R in its debate: median rank ≤ 2 over 10 debates and rank 1 in ≥ 4, beyond the field-only skeleton null. Kill: median rank ≥ 4. [0.25]
- **P1b:** an agent's S is higher in the debate it judges than in debates where it does not. [0.35]
- **P1c:** the judge ranks better under read-gated S^R than under in-flight S^P. [0.4]
- **P2:** J_ST − J_OT > 0 (team permutation p < 0.05). Kill: ≤ 0 or p > 0.2 with power ≥ 0.8. Rival R-alternation expects J_OT > J_ST in the deb phase. [0.3]
- **P3:** the judge's read-out kick on debaters J_DJ − J^P_DJ ≤ 0.05, and debaters' talk steps at the verdict beyond placebo boundaries. [0.4]
Expected sizes: per-call couplings in 12a are small (H67 J₁\* ≈ 0.007 in probability); only a judge-sink signal well above the synthetic's minimum detectable size can pass P1.

## Result
*Run 2026-10-04 22:18–22:20 UTC.* Ranking frozen at 22:17:44 UTC (SHA-256 `cc87142c…a5a8`) before any role label was read; data `data/processed/H115-debate-judge-role-recovery/G12/` (`frozen_ranking.json`, `results.json`). Additive in/out fit, λ = 4, 3,644 calls in the ten debate windows (7 agents present in every debate).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 judge = top sink (median rank ≤ 2, rank 1 in ≥ 4) | judge ranks 2, 6, 6, 1, 1, 3, 7, 4, 2, 1: median 2.5, rank 1 in 3/10, mean normalized rank u = 0.38 | uniform p(mean u) 0.15; field-only skeleton null mean u 0.46 ± 0.10, p 0.24 | not supported; kill (median ≥ 4) not reached |
| P1b within-agent contrast | S as judge − S as debater = +0.39 | judge-label permutation p 0.12 (SD 0.32) | not supported |
| P1c read beats in-flight | mean rank 3.3 (read) vs 4.0 (in-flight) | — | direction as predicted, weak |
| P2 team blocks J_ST − J_OT > 0 | **−0.16 ± 0.08** (J_ST 0.04 ± 0.06, J_OT 0.20 ± 0.05) | team permutation: p(≥) 0.99, p(≤) 0.01; in-flight −0.06 ± 0.09 | **failed (HH kill fires; reversed)** |
| P3a judge's read-out kick on debaters ≤ 0.05 | J_DJ − J^P_DJ = +0.02 ± 0.11 | — | consistent |
| P3b verdict field step on debaters | Δh_D = −0.12 | placebo splits in deb: \|Δh\| q95 0.24, p 0.81 | failed as specified |

- **Calibration of P1 against the synthetic (post hoc reading):** the observed mean u = 0.38 sits at the median of worlds with a planted judge sink a = 0.15 (P(u ≥ obs) 0.55), and is rare for a = 0.6 (0.01) and a = 0.3 (0.18). A judge sink of ≥ 0.6 Ising units is excluded; a = 0 is not (P 0.89).
- **Variants:** full J median rank 3 (rank 1 in 1/10); untrimmed median 2.5 (2/10); chat-mode clock median 4 (0/10; low power, A1).
- **Pair-type couplings (post hoc, labels known):** the judge reads debaters with J_JD = 0.28 ± 0.09 and debaters read the judge with J_DJ = 0.07 ± 0.07, so the pooled direction is sink-like (difference ≈ +0.22 ± 0.12). Opposite-team coupling J_OT = 0.20 ± 0.05 is the largest debater-debater term; same-team J_ST = 0.04 ± 0.06. By phase the reversal is strongest before the first speech (pre −0.36 ± 0.15; deb −0.11 ± 0.11; post −0.04 ± 0.13).
- **P3b, signed (post hoc):** the placebo splits are not centred at 0. Debaters' talk rises within the deb phase (placebo mean +0.16, 95% [0.07, 0.26]), while it falls at the verdict (−0.12, below all 200 placebos). The pre-registered |Δh| rule missed a sign reversal; read as a post hoc field step of −0.28 relative to the within-debate trend.
- **Reading:** talk coupling in a debate runs across the teams (a speaker talks after reading an opponent), which is R-alternation, the opposite of the co-usage blocks of H101 (+0.15 within, −0.60 across). The judge leans sink-ward but by an amount (a ≈ 0.15) that ten seven-agent debates cannot resolve.

Figure: [`figures/pairtype.pdf`](figures/pairtype.pdf) (pair-type couplings, read and in-flight).

## Scorecard (period-specific axes)
C (rank null, field-only skeleton, in-flight placebo), E (role rotation across debates), G (DQ6 judges and teams).

## Notes
- DQ6 `team` rows carry the values gov / opp / bench / judge; teams were 3 + 3 in 8 debates and 3 + 2 (+1 bench) in two.
- Blind protocol: rankings frozen and hashed (`data/processed/H115-debate-judge-role-recovery/G12/frozen_ranking.json`) before the DQ6 `judge`, `team` and `debate_result` rows are read.
