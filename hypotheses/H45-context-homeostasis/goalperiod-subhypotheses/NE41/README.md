# H45 × NE41: forced context erasures at the 41-call cap (regime III, 2026-03-24 →)

**Verdict:** failed (no import overshoot: agents talk less after an erasure, 0.74 [0.69, 0.80]; replies per call unchanged)
**Role:** native
**Period:** regime III non-holdout periods #36 (from 03-24), #37–#42, #44 and the #51 head (07-06 → 09-04). Forced erasures: ~20k segments opened by a cap consolidation (DQ1 ledger count, non-holdout); voluntary consolidations as the comparison.

## Why this period
The scaffold forces a consolidation when a context segment reaches 41 calls. The agent keeps its memory but loses its context window at a time it did not choose: thousands of quasi-random erasures (H15 found writes fall ~45% for ~10 turns; H08 found coupling to pre-erasure senders falls 18%; H39 found erasure pushes toward work). A homeostat that holds a room-share set point should, right after an erasure, import room information faster than usual (talk and reply more per item), then relax as the share rebuilds. A passive agent has no reason to.

## Prediction
*Written 2026-10-04 06:32 UTC, before running any NE41 statistic.*
- **N1 (overshoot, H45):** in the pooled regime-III data, k-adjusted talk propensity in calls 1–3 after a forced reset is ≥ 1.2 × the j 20–40 baseline (agent-day fixed effects, flexible k bins), relaxing with τ ≤ 10 calls; per period, ≥ 2/3 of the 8 periods show overshoot ≥ 1.2. Passive: ≈ 1.
- **N2 (engagement):** k-adjusted reply engagement E1 in calls 1–5 after a forced reset exceeds the baseline by ≥ 20% (pooled).
- **N3 (forced vs voluntary):** voluntary resets show the same or a larger overshoot (the agent chose the moment, often after finishing a task).
- **N4 (share trajectory):** the median share rises monotonically through the segment (passive accumulation from a reset), with no hump. A hump (share above its late level at j ≈ 5–15) would be a controller signature.
- **N5 (reset snapshot; scaffold floor):** P at j = 1 (minus the call's own new items) rises with the room characters the agent received in the 30 min before the reset (agent-day fixed effects; slope > 0 with the CI excluding 0): the scaffold re-shows recent room state at a reset, which sets a floor on the share that the agent does not control.
- **Against H45:** N1 and N2 ≈ 1 after k adjustment.

## Result
Pooled regime III (#36–#51 head): 21,165 forced and 16,357 voluntary resets; 777,766 calls in forced-opened segments. k-adjusted ratios to the j 20–40 baseline (agent-day fixed effects, flexible k bins, day-bootstrap CIs).

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| N1 (H45): talk in calls 1–3 after a forced reset ≥ 1.2 × baseline, τ ≤ 10 | **0.74 [0.69, 0.80]**: an undershoot, relaxing with τ 10.1 [7.7, 13.8] calls. Per period 0.49–0.86; 0/9 ≥ 1.2, 5/9 with the CI below 1 (G36 0.51, G38 0.69, G40 0.70, G41 0.49, G51 0.77) | 1 (passive synthetic 0.94–1.06) | **failed (reversed)** |
| N2: reply share E1 in calls 1–5 ≥ 1.2 × baseline | 1.21 [1.15, 1.27] over calls 1–3 (21,473 talk calls), τ 8.1 [5.4, 13.2] | 1 | met (at the threshold) |
| N3: voluntary resets the same or larger | talk 0.66 [0.60, 0.73] (τ 8.5); E1 1.29 [1.22, 1.37] (τ 2.2): same direction, larger | – | met |
| N4: monotone share, no hump | median share 0.093 at j = 1 → 0.103 (j 13) → 0.112 (j 33) → 0.121 (j 41); P 14.9k → 69.4k tokens | a hump would be a controller signature | met (passive accumulation) |
| N5: reset snapshot carries recent room content (scaffold floor) | 5.1 [−0.1, 16.5] tokens per 1k room characters of the previous 30 min (all consolidations, n 19,127); 0.2 [−4.1, 9.9] (forced, n 12,699), against 318 tokens per 1k characters for room content in context; base context median 13.9k tokens | slope > 0 | not met (the fresh context does not re-show recent traffic at any measurable scale) |
| Post hoc PH2: replies per call (talk × E1) after a forced reset | 0.92 [0.82, 1.05]; voluntary 1.00 [0.88, 1.14] | 1 | no net import change |

**Reading.** An erasure does not trigger a homeostatic import burst. For about ten calls agents talk less (k-adjusted −26%), while the talks they do make are more often replies to pending messages (+21%). The product, replies per call, is unchanged (0.92 [0.82, 1.05]): the agent shifts from status-style talk to answering, without importing more room information. This matches H39 (erasure pushes toward work) and H15 (output dips for about ten turns). The share itself does not need restoring. The first call after a reset receives the backlog that arrived during the ~3-min consolidation (raw k_new 5.8 at j = 1 vs ≈ 0.5 after), so the share starts at about 80% of its late-segment level (0.093 vs 0.12) and then grows monotonically. That is a property of the scaffold's timing (arrivals during the memory call roll over to the next call), not of the agent. The reset's fresh context (median 13.9k tokens: system prompt, memory) carries no measurable recent room traffic.

Figures: `figures/summary_obs.pdf` (b), `figures/summary_obs2.pdf` (b). Data: `data/processed/H45-context-homeostasis/NE41/native.json`; PH2 in `posthoc.json`.

## Scorecard (period-specific axes)
- **C:** the k-adjusted talk ratio beats the passive synthetic's range (0.94–1.06) on the low side (CI 0.69–0.80), so there is a real post-erasure effect, opposite in sign to H45's.
- **D:** N4 (monotone share) and N5 (no snapshot) are unfitted statistics consistent with passive accumulation after a scaffold reset.
- **E:** 21k forced erasures at a scaffold-set time are the intervention; the response is a talk undershoot and a reply-share rise with no net import change.
- **H:** controller (overshoot 1.6–1.8 in the synthetic) and competition (2.3–2.5) rejected; passive (≈ 1) closer, but the undershoot is outside every synthetic class.

## Notes
- 2026-10-04 06:32 UTC: prediction written before the run. The synthetic validation (`analysis/synthetic.py`) runs first; the k adjustment uses flexible k bins after the synthetic showed a linear ln(1 + k) control leaves residual excess.
- 2026-10-04: results from `analysis/natives.py` (NE41) and `analysis/posthoc.py` (PH2, labelled post hoc). Amendment A3 applies (per-period overshoot needs its CI above 1).
