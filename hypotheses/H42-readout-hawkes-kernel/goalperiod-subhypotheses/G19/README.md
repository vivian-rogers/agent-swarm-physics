# H42 × G19: Regime-I scheduled chat (2025-11-03 → 2025-11-14): is talk read-out-gated once the call type is controlled?

**Verdict:** supported (native prediction N4b, which counts *against* a universal read-out kernel: regime-I talk is not driven by messages read at the call once call type is controlled; the pre-registered estimator's n_cross ≈ 0.89 is a call-type artifact)
**Role:** native (exploratory, non-holdout); 19a also enters the replication table
**Round 2 verdict:** failed (Round 2 below; the line above is round 1's)
**Period:** regime I · mode C · N 7–8 · one room · units 19a (9 days) and 19b (1 day; GPT-5.1 joins).

## Why this period
In regime I agents alternate between scheduled chat-mode calls (about every 74 s; 45% read no new message, DQ1) and computer-use sessions. The read-out clock here is exogenous, set by the scheduler rather than by messages, so read-out gating can be tested without the "messages trigger calls" confound. #19a is the longest one-room regime-I unit not yet fitted (#27 was used in the smoke tests).

## Prediction
*Written 2026-10-04 07:45 UTC, before running #19. Informed by the #27 smoke fits (disclosed): with one global call-clock weight (world pr), B absorbed the call type (chat-mode calls accumulate more messages and talk far more; n_cross(B) 0.67). With class baselines (world B), B went to 0.*
- **N4a:** in world pr, n_cross(B) ≥ 0.3 (the call-type artifact) and exceeds its shift null.
- **N4b (primary):** in world B (class baselines), n_cross(B) is at or below its day-block null maximum, and held-out Δℓ(B − S0) ≤ 0 for #19a. In regime I, talk at scheduled chat calls is not driven by how many new messages the call read.
- **Counts against N4b:** world-B B above the day-block maximum with a positive held-out gain.
- **Reading:** if N4b holds, the read-out kernel is not a universal mechanism. In regime I talk follows the scheduler and call type (consistent with H08's failed regime-I talk clause), and any regime-I "cross-excitation" in models without call classes is a scheduling artifact.

## Result
*Replication row (layer 1, the common estimator):* amended reading **failed** (world-B gain −0.4 nats vs world-A exponential gain +29.7 nats; world-B B does not beat its nulls); the pre-registered rule gives "supported", but that is the artifact described here.

| unit | days | msgs | world pr n_x(B) [shift q95 / day-block max] | world B n_x(B) [shift q95 / day-block max] | world B gain(B), mnats/event | world A n_x(A) |
| --- | --- | --- | --- | --- | --- | --- |
| 19a | 9 | 4786 | 0.886 [0.879 / 0.626] | 0.000 [0.001 / 0.000] | −0.1 | 0.101 |
| 19b | 1 | 565 | 0.869 [0.866 / –] | 0.053 [0.067 / –] | – | 0.093 |

| prediction | observed | verdict |
| --- | --- | --- |
| N4a world pr n_x(B) ≥ 0.3 and above its shift null | 0.886 vs shift q95 0.879 (barely above); far above the day-block max 0.63 | met (the artifact is as predicted) |
| N4b (primary) world-B n_x(B) ≤ day-block max and held-out gain ≤ 0 (#19a) | n_x 0.000 (day-block max 0.000); gain −0.1 mnats/event | **supported** |

- **Reading:** in regime I, whether an agent talks at a call depends on the call type (scheduled chat-mode vs computer use) and the agent-day, not on how many new messages the call read. The pre-registered model (one call-clock weight for all call types) turns the call type into a cross-branching ratio of 0.89. Its shift null (0.88) reproduces almost all of that, which shows it is not message timing.
- **Not a negative for coupling in general.** Messages may still steer *what* is said (H08's addressing, H29's naming), only not *whether* a talk happens. The exponential kernel's n_x ≈ 0.10 here is timing co-movement between others' messages and the recipient's chat-mode calls.

## Round 2 (2026-10-05)

*Prediction (templated from the card's round-2 pre-registration, 2026-10-05 04:05 UTC, written before any round-2 statistic):* in regime III a named read raises talk at the read-out call (≈ 0.08 per read, H67), cold-named messages carry at least half the thread-named jump, the named Hawkes kernel survives a fitted Cox field, and reads move call timing only through the reading call's own decision. In regimes I–II no class switch beyond the call-skeleton null. Round-2 verdict rule: *supported* if the Cox-field named model beats field-only S0 held out (summed over the period's CV units) with n_named > 0 **and** the pooled cold-named talk J has its CI above 0; *failed* if neither; *mixed* otherwise; *descriptive* without a CV unit.

**Round 2 verdict:** failed. Period pools (random effects over units, 95% CI): talk J named -0.008 [-0.018, 0.002], cold -0.008 [-0.022, 0.006], thread -0.009 [-0.023, 0.005], unnamed 0.0046 [-0.0004, 0.0096].
Call class (excess over the call-skeleton null): chat next J unnamed -0.0004 [-0.0072, 0.0064], named -0.0009 [-0.0107, 0.0088].
R3 (Cox field; event-weighted): exponential n_x 0.100 → 0.053; read-out n_x 0.006 → 0.006; named per message 0.003 → 0.001; summed held-out gain of the named model over field-only S0 -0.6 nats.

| unit | calls | talk J named | cold | thread | unnamed | pause J named (excess) | log gap J named (excess) | chat next J unnamed (excess) | R3 n_x(A) r1 → Cox | R3 n_x(B) r1 → Cox | R3 named per msg r1 → Cox | R3 Δcv(Bmu − S0), Cox (mnats/event) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 19a | 27726 | -0.009 [-0.022, 0.001] | -0.010 [-0.027, 0.002] | -0.009 [-0.023, 0.004] | 0.005 [0.000, 0.010] | 0.0002 ± 0.0009 | -0.0000 ± 0.0168 | 0.0005 ± 0.0071 | 0.101 → 0.051 | 0.000 → 0.000 | 0.003 → 0.001 | -0.12 |
| 19b | 3042 | -0.003 [-0.028, 0.009] | 0.002 [-0.021, 0.054] | -0.010 [-0.063, 0.026] | 0.001 [-0.013, 0.018] | – | 0.0055 ± 0.0540 | -0.0092 ± 0.0233 | 0.093 → 0.072 | 0.056 → 0.054 | 0.003 → 0.003 | – |

J = β(read) − β(in flight) per read message (OLS within agent × day × call-class cells; 1-h block bootstrap). Excess = J minus the call-skeleton null mean (8 synthetic message streams on the real call skeleton). R3: 'r1' = round 1's shared 30-min baseline refitted; 'Cox' = free log-rate per day × 10 min (per day × room × 10 min in multi-room units). Data: `data/processed/H42-readout-hawkes-kernel/round2/`.
