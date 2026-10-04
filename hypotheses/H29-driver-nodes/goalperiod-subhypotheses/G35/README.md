# H29 × G35: designated daily leaders (2026-03-16 → 2026-03-20)

**Verdict:** mixed
**Role:** native (round 1b, non-holdout)
**Period:** regime II · two rooms (#best / #rest, NE15 split on 03-16) · 5 days · DQ6 ground truth: two designated "lead designers" per day on 03-16 (agents 18, 23), 03-17 (19, 20) and 03-18 (6, 22).

## Why this period
H29 asks whether some agents are driver nodes. #35 is the only non-holdout period where the role that should make an agent a driver is *assigned* and rotates day by day, so the same agent can be compared with itself on its leader day and on its ordinary days (within-agent design; no ranking needed).

## Prediction
*Written 2026-10-04 07:31 UTC, before running anything on #35. Seen before writing: DQ6's leader rows and the calendar only.*

Per leader agent a, leader day vs a's other #35 days (ledger visibility; DQ2 `reply_pairs` with `pair_set = cand`; whitened regime-II statements, bge-small primary, gte robustness):
- **R (reply attention):** soft replies received per message sent, Σ p_reply over candidate pairs whose parent A is a's message and whose reply B is by another agent, divided by a's messages;
- **P_u (broadcast pull):** field-corrected pull per message of a's messages on recipients they do *not* name, a(V) − a(X_V) (round-1 estimator, ledger-visible rows);
- **P_n (addressed pull):** the same on named recipients (descriptive; few rows);
- **Vol:** a's messages per active hour.
Pooled over the 6 leader agent-days as log ratios (leader day / own other days), with a bootstrap over leader agents.

Predictions:
- **N1:** designation buys attention: R ratio ≥ 1.3 (pooled point) and Vol ratio ≥ 1.2.
- **N2:** designation does not buy broadcast influence: the P_u ratio's 95% CI includes 1 (or lies below it).
- **Verdict rule:** supported if N1 and N2 hold; failed if P_u rises with CI excluding 1 (a designated leader becomes a broadcast driver) or R ratio ≤ 1; mixed otherwise. Credence 0.5 (6 agent-days; regime-II rooms of 6–7 agents).

## Result
*Run 2026-10-04 ~08:50 UTC (`analysis/r1b_extra.py`; ledger rows built by `scheme/build.py --data r1b`, native unit G35; regime-II whitener). Bootstrap over the 6 leader agent-days (2,000 draws).*

| Agent | Leader day | replies per message, leader day / other days | messages per active hour | broadcast pull P_u (bge) | unnamed rows on leader day |
| --- | --- | --- | --- | --- | --- |
| 18 | 2026-03-16 | 0.99 / 0.51 | 7.0 / 5.3 | 0.105 / 0.086 | 188 |
| 23 | 2026-03-16 | 0.73 / 0.48 | 11.5 / 9.8 | 0.064 / 0.063 | 90 |
| 19 | 2026-03-17 | 0.08 / 0.10 | 9.3 / 7.3 | 0.012 / 0.035 | 302 |
| 20 | 2026-03-17 | 0.50 / 0.40 | 7.8 / 12.5 | 0.026 / 0.049 | 47 |
| 6 | 2026-03-18 | 0.52 / 0.35 | 12.1 / 13.7 | 0.076 / 0.038 | 314 |
| 22 | 2026-03-18 | 1.08 / 0.65 | 5.0 / 6.7 | 0.089 / 0.069 | 20 |

| Prediction | bge-small | gte-modernbert | Verdict |
| --- | --- | --- | --- |
| N1a reply attention ratio ≥ 1.3 | 1.39 [1.09, 1.69] | 1.39 [1.09, 1.69] | ✓ |
| N1b volume ratio ≥ 1.2 | 0.97 [0.77, 1.20] | 0.97 [0.77, 1.20] | ✗ |
| N2 broadcast pull ratio CI ∋ 1 | 1.09 [0.76, 1.41] (difference +0.005) | 1.10 [0.91, 1.25] | ✓ |
| named pull difference (descriptive) | +0.033 [-0.017, +0.113] | +0.067 [-0.025, +0.213] | – |

**Verdict: mixed.** Designation buys attention (other agents reply to a leader's messages 1.4× more often on its leader day) but not more talking and not more broadcast influence on what unnamed room-mates write next. Leadership here is an attention role, not a driver node. Six agent-days in regime-II rooms of 6–7 agents: low power.
