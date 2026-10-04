# H119 × G51: #focus opens (08-05) and closes (08-24)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime III · #51 · off-switch 08-03, 08-04 | 08-05, 08-06; on-switch 08-20, 08-21 | 08-24, 08-25 · ~25 eligible agents · Gemini 2.5 Pro and Claude Opus 4.8 move to #focus ~17:40 UTC on 08-05 and back ~18:10 UTC on 08-24; hoppers (fractional co-location) are dropped from the pair classes.

## Why this period
An A-B-A for two agents inside one goal: their pairs with #general switch off, then on. NE43's bookend stop (08-05) and nudger-off (08-20) are field steps on the same boundaries; the pair contrast removes them.

## Prediction
*Written 2026-10-04 22:06 UTC, before running on this period.*
- Off-switch: Δ_off < Δ_fixed [0.5]. On-switch: Δ_on > Δ_fixed [0.5]. S (off-switch counted as −Δ_off) > 0 in each [0.5]; one-sided p < 0.05 [0.3].
- Verdict rule (card): **supported** if S > 0 with one-sided p < 0.05; **failed** if S ≤ 0; **mixed** otherwise. (one row per switch)

## Result
*Run 2026-10-04 22:43–22:46 UTC (exploratory, non-holdout).*

| Switch | E1 S (95% CI) | E2 read − in-flight (switched pairs) | Verdict |
| --- | --- | --- | --- |
| #focus opens (off arm, 64 directed pairs, 18 agents) | 0.063 [0.029, 0.097], p₁ < 0.001 | 0.09 [−0.21, 0.38] (before side) | mixed |
| #focus closes (on arm, 48 directed pairs, 14 agents) | 0.050 [0.004, 0.097], p₁ 0.017 | 0.23 [−0.20, 0.66] (after side) | mixed |

The fitted E1 coupling follows co-location at both switches (small, significant). E2 does not attribute it to read-outs (n.s.), and E1's S is not specific here (room-drive false positives 0.93 / 0.58, Amendment 1). Mixed by the amended rule.

## Scorecard (period-specific axes)
G: E1 follows the known A-B-A in sign at both switches. D: no read-gated attribution.

## Notes
