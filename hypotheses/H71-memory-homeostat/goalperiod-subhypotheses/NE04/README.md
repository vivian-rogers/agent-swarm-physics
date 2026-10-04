# H71 × NE04: NE04: chain-of-thought memory consolidation (and the history-search tool), 2025-09-05

**Verdict:** failed (φ⁺ rose, not fell; removal share unchanged)
**Role:** native
**Period:** see "Why this period".

## Why this period
#12 splits at 09-05 (G12a | G12b), and #13 follows with the same 6–7 agents. The consolidation method changes; the cycle structure (session ends) does not.

## Prediction
*Written 2026-10-04 19:55 UTC, before running this native test.*
- **N2a:** φ⁺ falls by ≥ 0.15 after the switch (paired over agents in #11 + #12a vs #12b + #13): a model that reasons before rewriting pulls harder toward its set point.
- **N2b:** the share of lines removed per compression rises (paired, CI > 0).
- **Counts against:** Δφ⁺ ≥ 0 with the CI excluding −0.15.

## Result
*Run 2026-10-04.* Paired over agents in #11 + #12a (before) and #12b + #13 (after).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N2a φ⁺ falls by ≥ 0.15 | Δφ⁺ +0.15 [+0.04, +0.34] (7 agents; 0.42 → 0.57) | failed (opposite sign) |
| N2b removal share up | 0.517 → 0.505 (lines removed / (removed + kept)) | failed |
| set point (not predicted) | Δ ln μ +0.17 [+0.01, +0.40] | – |

**Reading.** Chain-of-thought consolidation made memory size *more* persistent per cycle and raised the set point by about 18%; it did not change how much each compression removes. Seven agents and one goal change (#12 → #13) inside the comparison make this weak.

## Scorecard (period-specific axes)
- **E:** a scaffold change to the consolidation method moves the set point and the persistence, not the removal fraction. Low power (7 agents).

## Notes
- Data: `data/processed/H71-memory-homeostat/results/natives.json` (key `NE04`).
