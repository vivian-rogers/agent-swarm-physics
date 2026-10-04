# H115 × G26: Elect a village leader. They choose this week's goal! (2026-01-05 → 01-09)

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** regime I · mode C · 10 agents · one room · 5 days. Leader term 1: 01-05 19:35:22 → 01-09 19:00:43 UTC; term 2 from 01-09 19:00:43 (DQ6 `leader`, agent 17).

## Why this period
A single designated agent with a dated start in a regime-I chat village: the first replication target for the blind sink ranking outside the debate week. H65 found this leader to be a content source and a reply target.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* R1 as it applies here: in each term day window (01-05 post-result, 01-06, 01-07, 01-08, 01-09 pre-T₂, 01-09 post-T₂; windows with ≥ 5 calls per agent), the leader's normalized sink rank u_L ≥ 0.5 (source half) in ≥ 2/3 of windows. [0.55] Against: u_L < 0.5 in ≥ 2/3 of windows (the leader is a sink, like the predicted judge).

## Result
*Run 2026-10-04 22:19–22:22 UTC* (`analysis/run_replication.py`; `data/processed/H115-debate-judge-role-recovery/G26/replication.json`). Additive fit, λ = 4, trimmed calls, 10 agents in every window.

| Window | calls | leader rank (of 10) | u_L | in-flight u_L | skeleton-null mean u_L (p of u ≥ obs) |
| --- | --- | --- | --- | --- | --- |
| 01-05 after the result | 2,773 | 3 | 0.22 | 0.56 | 0.57 (p 0.92) |
| 01-06 | 1,077 | 10 | 1.00 | 0.67 | 0.51 (p 0.09) |
| 01-07 | 2,467 | 10 | 1.00 | 0.78 | 0.54 (p 0.13) |
| 01-08 | 2,191 | 6 | 0.56 | 0.11 | 0.50 (p 0.48) |
| 01-09 before re-election | 198 | 10 | 1.00 | 0.00 | 0.62 (p 0.16) |
| 01-09 after re-election | 2,991 | 10 | 1.00 | 0.22 | 0.54 (p 0.08) |

- **R1 supported:** the leader sits in the source half in 5 of 6 windows (mean u_L 0.80; field-only skeleton null mean 0.55). In four windows it is the largest source of the ten agents. Against the skeleton null the per-window evidence is modest (p 0.08–0.16 in four windows; Fisher combination over the six windows p ≈ 0.08), so this is a consistent direction, not a significant one. On the result day itself (01-05, after 19:35 UTC) the leader still ranks 3rd from the sink end (u_L 0.22); the source role appears from 01-06 on. The in-flight ranking does not show it (mean u^P 0.39), so the source signal is read-gated.
- Consistent with H65 (the elected leader is a content source and a reply target): in talk timing too, other agents talk after reading agent 17, and agent 17 does not talk after reading them.

## Scorecard (period-specific axes)
G (DQ6 leader), I (transfer of the sink reading to leaders).

## Notes
