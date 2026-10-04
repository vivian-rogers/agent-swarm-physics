# H71 × NE32: Newcomers relax from an empty memory (Onsager regression; anchored on NE32, all non-holdout joins)

**Verdict:** mixed (relaxation follows the slow set-point mode, not φ⁺)
**Role:** native
**Period:** see "Why this period".

## Why this period
A newcomer starts with no memory: the largest displacement from a set point in the data. Onsager's regression hypothesis says a linear homeostat relaxes from a large displacement with the same law as its small spontaneous fluctuations. Joins: every roster join whose first memory snapshot is non-holdout and which has ≥ 40 compression cycles (#38 Opus 4.7, Kimi K2.6; #42 Gemini 3.5 Flash; #44 joins; #51's NE32 trio and later joins).

## Prediction
*Written 2026-10-04 19:55 UTC, before running this native test.*
- **N4a:** fitting μ_i and φ_i on cycles 21+ only, the first 20 cycles follow x̂⁺_n = μ_i + φ_iⁿ (x⁺_0 − μ_i): the fitted relaxation factor φ_relax lies within ±0.2 of φ_i for ≥ 2/3 of newcomers.
- **N4b:** the displacement d_n = x⁺_n − μ_i shrinks to below half of d_0 within 3 cycles for ≥ 2/3 of newcomers (φ⁺ ≤ 0.8).
- **Counts against:** φ_relax > φ_i + 0.2 for most newcomers (slow growth from empty, i.e. accumulation, not regulation).

## Result
*Run 2026-10-04.* 28 newcomers (roster join with the first memory snapshot within 3 days, ≥ 40 cycles, non-holdout).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N4a φ_relax within ±0.2 of φ_i for ≥ 2/3 | 0.68 | met (at the threshold) |
| N4b displacement halves within 3 cycles for ≥ 2/3 | 0.32 | failed |

Every newcomer starts *below* its later set point (first post-compression size 7.6k–25k characters vs set points 10k–77k; d₀ −0.23 to −1.29 in ln units). Median φ_relax 0.92 vs median φ_i 0.79.

**Reading (post hoc).** Memory grows from a newcomer's first compression toward its set point over 5–20 cycles, slower than the small-fluctuation φ⁺ predicts. The relaxation factor (≈ 0.9) matches the slow set-point persistence ρ_s of the two-timescale model (0.7–0.9 per cycle; `results/posthoc.json`), not the fast compression. Onsager regression holds for the slow mode only.

## Scorecard (period-specific axes)
- **D:** the relaxation from the largest displacement is an unfitted statistic; it agrees with the post hoc slow mode, not with the pre-registered single loop.

## Notes
- Data: `data/processed/H71-memory-homeostat/results/natives.json` (key `NE32`).
