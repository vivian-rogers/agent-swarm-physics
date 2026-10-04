# H114 × NE42: room merge and split at a fixed roster (#39 → #40 → #41, 2026-04-27 → 05-15)

**Verdict:** descriptive
**Role:** native (exploratory)
**Period:** goals #39 (two rooms), #40 (one merged room; GPT-5 alone in #rest), #41 (two rooms again) · 15 agents · regime III · 5 days each. Units 39, 40, 41.

## Why this period
In #40, 14 agents share one room, so each message has more readers and each reader more pending messages. H67 found read-out coupling vanishes there (J₁* 0.016 → 0.000 → 0.023), and H18 found per-sender uptake falls as k^−0.66. A pair-specific ping-pong channel should thin out under dilution, then return at the split.

## Prediction
*Written 2026-10-04 21:30 UTC, before running on these periods. Seen: H67's NE42 results. No H114 statistic.*
- **N42a:** the strong-link share in #40 is below the mean of #39 and #41. [0.45]
- **N42b:** the tail excess Δh in #40 is below the mean of #39 and #41. [0.4]
- **Counts against the Griffiths reading:** Δh rises in #40 while the strong-link share falls (the excess is not pair-carried).

## Result
*Run 2026-10-04 ~21:55 UTC.*

| Unit | g_rep | h_tail | Δh [95%] | δh | strong pairs | max pair g (R ≥ 10) |
| --- | --- | --- | --- | --- | --- | --- |
| #39 | 0.197 | 0.500 | 0.303 [-0.185, 0.387] | -0.028 | 0 | 0.36 |
| #40 | 0.338 | 0.520 | 0.182 [0.068, 0.268] | +0.011 | 0 | 0.27 |
| #41 | 0.532 | 0.608 | 0.076 [-0.046, 0.164] | -0.005 | 0 | 0.35 |

- **N42a** (strong-link share lower in #40): no strong pair exists in any of the three units (max pair gain 0.27–0.36), so there is nothing to dilute. **Not testable.**
- **N42b** (Δh lower in #40): 0.182 vs side mean 0.189; #39 has only 18 messages at depth ≥ 4 (not usable) and the CIs overlap. **Nominal only.**
- **Verdict:** descriptive. The merged room keeps a heavier-than-geometric tail (Δh 0.18 [0.07, 0.27]) with no strong pair: the tail does not need pairs here.

## Scorecard (period-specific axes)
E: the change across the merge and split.

## Notes
