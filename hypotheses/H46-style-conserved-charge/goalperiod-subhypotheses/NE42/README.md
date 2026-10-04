# H46 × NE42: Room events (NE42)

**Verdict:** mixed
**Role:** replication (exploratory)
**Boundaries:** Room events (NE42): the 05-04 merge of #best and #rest (39→40) and the 05-11 split (40→41), both goal-confounded, plus the #51 `#focus` room opening (08-05) and closing (08-24).

## Why this class
A natural-experiment class for the conservation test (exception (c): the transition is the object). Each boundary is scored against the agent's own day-to-day transitions near it.

## Prediction
*Written 2026-10-04 05:45 UTC, before running on this class.*
- content moves (T_c ≥ 0.65); type-controlled style conserved. A merge changes who an agent reads, so this is where accommodation (R1) would show.

## Result
*Run 2026-10-04 06:05 UTC on non-holdout data; `analysis/conservation.py` → `data/processed/H46-style-conserved-charge/conservation.json`, `conservation_rows.parquet`, `fingerprint.parquet`.*

| Channel | T (mean percentile vs own day-to-day) | 95% CI (boundaries, then agents) | randomization p | boundary Wilcoxon p | median z |
| --- | --- | --- | --- | --- | --- |
| style, type-controlled (primary) | 0.572 | [0.451, 0.747] | 0.023 | – | 0.01 |
| style, raw 20 features | 0.572 | [0.460, 0.738] | 0.022 | – | -0.16 |
| content, style-residualized (primary) | 0.612 | [0.441, 0.886] | 0.001 | – | 0.34 |
| content, raw whitened | 0.607 | [0.439, 0.886] | 0.002 | – | 0.16 |
| style, day field removed | 0.562 | [0.443, 0.732] | 0.044 | – | 0.06 |
| content, day field removed | 0.566 | [0.444, 0.744] | 0.034 | – | 0.11 |

- **Agent × boundary rows:** 74 over 4 boundaries.
- **Holm (six classes):** content p = 0.004, style p = 0.094.
- **Pre-registered class verdict:** **partial**.
- **Fingerprint (train before, test after; day-demeaned):** style 0.55 vs content 0.54 at chance 0.06 (ceilings 0.73 / 0.76); style ≥ 3× chance at 100% of boundaries; style > content at 50%. Anthropic-only: style 0.64 vs content 0.67 at chance 0.15.
- **Per boundary (mean percentile, style / content):** 39->40 (NE42 merge) 0.67 / 0.76; 40->41 (NE42 split) 0.78 / 0.97; 51f->51g (#focus opened) 0.43 / 0.42; 51g->51h (#focus closed) 0.55 / 0.51

## Scorecard (period-specific axes)
- **E:** 1. Content moves weakly (goal-confounded merge and split; #focus room); style does not move after Holm but exceeds a third of content's excess (partial).
