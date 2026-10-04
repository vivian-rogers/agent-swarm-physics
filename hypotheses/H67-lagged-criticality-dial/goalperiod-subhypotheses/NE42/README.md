# H67 × NE42: room merge and split at a fixed roster (#39 → #40 → #41, 2026-04-27 → 05-15)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** goals #39 (two rooms), #40 (one merged room, #universe-coordination; GPT-5 alone in #rest), #41 (two rooms again) · 15 agents · regime III · 5 days each.

## Why this period
An A-B-A change of the room structure at a fixed roster. In #40, 14 agents share one room, so each message has more readers (r̄ jumps). Mean field with a fixed per-read coupling predicts g_lag ∝ r̄. Attention dilution (H18: per-message uptake ∝ k^−0.6; H40: burial) predicts a smaller per-read jump in the merged room, so g_lag rises less than r̄. H25 found the equal-time talk dial collapses in #40 (0.13 → 0.003 → 0.18), which neither size reading predicted.

## Prediction
*Written 2026-10-04 19:35 UTC, before running on these periods. Seen: H25's and H26's NE42 results (equal-time talk collapse; content excess returns at the split); no H67 number.*
- **N42a:** r̄(#40) ≥ 1.5 × the mean of r̄(#39), r̄(#41). [0.8]
- **N42b (dilution):** J₁*(#40) < mean J₁*(#39, #41), so g_lag(#40)/g_lag(#39,#41) < r̄(#40)/r̄(#39,#41). [0.55]
- **N42c (lag sees what equal time misses):** g_lag(#40) > 0 with CI excluding 0, although H25's equal-time talk dial is ≈ 0 there. [0.45]
- **Counts against the lagged-dial reading:** g_lag(#40) ≈ 0 as well (then H25's collapse is real loss of coupling, not equal-time blindness).

## Result
*Run 2026-10-04 ~20:20 UTC.*

| Unit | g_lag [95%] | J₁* [95%] | r̄ | g_eq | named part of g_lag | J₁* named |
| --- | --- | --- | --- | --- | --- | --- |
| #39 (two rooms) | 0.144 [0.073, 0.219] | 0.016 [0.008, 0.025] | 9.06 | 0.159 | 0.073 | 0.132 |
| #40 (merged room) | 0.003 [−0.106, 0.109] | 0.0002 [−0.008, 0.009] | 12.72 | −0.048 | 0.035 | 0.040 |
| #41 (two rooms) | 0.189 [0.095, 0.288] | 0.023 [0.011, 0.037] | 8.48 | 0.162 | 0.060 | 0.049 |

- **N42a** (r̄ ×≥ 1.5): r̄ rises ×1.45. **Failed narrowly.**
- **N42b** (dilution, g ratio below r̄ ratio): J₁* falls to 0 in #40; g ratio 0.02 vs r̄ ratio 1.45. **Supported.**
- **N42c** (the lagged dial sees coupling that the equal-time dial misses in #40): g_lag(#40) is 0 as well. **Failed.**
- **Reading:** H25's equal-time talk collapse in #40 is a real loss of read-out coupling, not equal-time blindness. Named messages still couple in #40 (J₁* named 0.04), but one shared room of 14 agents removes the unnamed response.

