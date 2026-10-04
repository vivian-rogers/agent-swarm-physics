# H46 × NE43: Nudger off (NE43, 2026-08-21, inside #51)

**Verdict:** mixed
**Role:** replication (exploratory)
**Boundaries:** Nudger off (NE43, 2026-08-21, inside #51): the automated speaker falls silent (no nudges, no daily bookends). Day-level transition 08-20 → 08-21 against #51 placebo transitions.

## Why this class
A natural-experiment class for the conservation test (exception (c): the transition is the object). Each boundary is scored against the agent's own day-to-day transitions near it.

## Prediction
*Written 2026-10-04 05:45 UTC, before running on this class.*
- content barely moves (T_c ≤ 0.6; likely uninformative); style conserved (T_s within band).

## Result
*Run 2026-10-04 06:05 UTC on non-holdout data; `analysis/conservation.py` → `data/processed/H46-style-conserved-charge/conservation.json`, `conservation_rows.parquet`, `fingerprint.parquet`.*

| Channel | T (mean percentile vs own day-to-day) | 95% CI (boundaries, then agents) | randomization p | boundary Wilcoxon p | median z |
| --- | --- | --- | --- | --- | --- |
| style, type-controlled (primary) | 0.551 | [0.403, 0.688] | 0.242 | – | -0.15 |
| style, raw 20 features | 0.579 | [0.447, 0.707] | 0.139 | – | -0.04 |
| content, style-residualized (primary) | 0.721 | [0.603, 0.823] | < 0.001 | – | 0.60 |
| content, raw whitened | 0.706 | [0.592, 0.808] | 0.001 | – | 0.47 |
| style, day field removed | 0.552 | [0.406, 0.686] | 0.237 | – | -0.07 |
| content, day field removed | 0.778 | [0.691, 0.863] | < 0.001 | – | 0.60 |

- **Agent × boundary rows:** 18 over 1 boundaries.
- **Holm (six classes):** content p = 0.004, style p = 0.725.
- **Pre-registered class verdict:** **conserved (equivalence not established)**.
- **Fingerprint (train before, test after; day-demeaned):** style 0.78 vs content 0.83 at chance 0.06 (ceilings 0.83 / 0.93); style ≥ 3× chance at 100% of boundaries; style > content at 0%. Anthropic-only: style 1.00 vs content 1.00 at chance 0.20.
- **Per boundary (mean percentile, style / content):** 51g: 08-20 -> 08-21 (nudger off) 0.55 / 0.72

## Scorecard (period-specific axes)
- **E:** 1. Content moves after the nudger switch-off, style does not; one boundary, so equivalence cannot be established (Amendment 1).
