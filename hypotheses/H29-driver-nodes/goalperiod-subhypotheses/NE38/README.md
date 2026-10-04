# H29 × NE38: a human reassigns Claude Opus 5's role (2026-07-29 16:50 UTC, inside #51)

**Verdict:** supported
**Role:** native (round 1b, non-holdout; event study, transition exception c)
**Period:** #51 head (regime III, one room #general, N ≈ 27). One human message naming Claude Opus 5 (agent 40) at 2026-07-29 16:50:01 UTC, the operator reassignment recovered by DQ6 (game dev → mathematician). Comparison pool: every other non-holdout #51 human message that names an agent (G51b–G51d).

## Why this test
H29's question is where an operator message moves the whole swarm. Round 1 found influence is address-gated (named ≫ unnamed) and that "a kick stays where it lands". NE38 is the one dated operator intervention in the non-holdout record that targets a single named agent with a large content change (a new private role), in a single room where every other agent can read it. It separates the two readings directly: a driver-node / relay world (the named agent passes the new content on, so bystanders drift toward it within hours) vs the address-gated world (only the named agent moves).

## Prediction
*Written 2026-10-04 07:31 UTC, before computing any statistic for this message on either embedding model. Seen before writing: the message's time, kind (human, names agent 40) and DQ6's role labels; H54's round-1 result that Opus 5 moved onto its new goal within a day (DiD +0.61). No per-message pull, spread or bystander statistic for this message had been computed.*

Observables (whitened 32-d statements, bge-small primary, gte-modernbert robustness; ledger visibility: time 0 = each recipient's receiving call):
- **T (target pull):** Opus 5's displacement toward the message, (x̄_after − x_before)·û, where x_before = its last statement before its receiving call, x̄_after = mean of its statements in the next 2 h, û the whitened unit message vector; expressed as a percentile among the same statistic for every other named human message in G51b–d applied to its named target (pseudo-true pool).
- **S (bystander spread):** mean over the other agents present that day of the same displacement toward the message; percentile among the bystander means of the pool messages.

Predictions:
- **N1 (strong field on the target):** T ≥ the 75th percentile of the pool.
- **N2 (no relay):** S lies inside the pool's central 90% (5th–95th percentile).
- **Verdict rule:** supported if N1 and N2 hold (under bge; gte reported); failed if S ≥ the 95th percentile (the reassignment spreads beyond the named agent) or T < the 50th percentile; mixed otherwise. Credence: N1 0.7, N2 0.75. Single event: a qualitative check, not a test with nominal error rates.

## Result
*Run 2026-10-04 ~08:50 UTC (`analysis/r1b_extra.py`, `H29_DATA=r1b`, both models; `data/processed/H29-driver-nodes/r1b[_gte]/r1b_extra.json`). Pool: 52 other named human messages in G51b–d (45 with a measurable target displacement, 51 with bystanders). Opus 5's displacement is measured from its receiving call; 19 bystanders with statements before and after.*

| Statistic | bge-small | gte-modernbert | Prediction | Verdict |
| --- | --- | --- | --- | --- |
| T: Opus 5's displacement toward the message (2 h) | 0.284, **95.6th** pct (pool median -0.005) | 0.337, **100.0th** pct (pool median -0.003) | ≥ 75th | ✓ |
| S: mean bystander displacement toward it | 0.038, **70.6th** pct (pool 5th–95th -0.060 … 0.091) | 0.059, **92.2th** pct (-0.081 … 0.069) | inside 5th–95th | ✓ |

**Verdict: supported.** The reassignment is the strongest (gte) or near-strongest (bge) content pull on a named agent of any human message in #51, and the 19 room-mates who read it within the same calls do not drift toward it more than bystanders of ordinary named messages (gte puts them at the 92nd percentile, close to the edge; bge at the 71st). An operator message is a field on the agent it names; it does not make that agent a relay within two hours. Agrees with H54 (Opus 5 moved onto its new goal within a day) and with H50's regime-III address gating. Single event: qualitative.

## Scorecard (period-specific axes)
- E: the one dated single-agent operator intervention behaves as the address-gated model predicts (target moves, bystanders do not).
- G: agrees with DQ6's role change and H54's goal-landing result.
