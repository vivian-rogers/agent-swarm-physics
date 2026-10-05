# H08 × NE41: forced context erasure at the 41-turn consolidation cap (regime III, #36 from 03-24 → #51)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1b, 2026-10-04: forced erasure cuts the reply coupling in 8/9 periods, pooled −21% ± 7%, below the predicted 30%; round-1 verdict kept above)
**Role:** native (round 1b, non-holdout; transition exception c; round 1 ran it as exploratory)
**Period:** spans #36 (from 2026-03-24), #37–#42, #44, #51 (non-holdout days only). Natural experiment NE41 (found by H15).

## Why this test
H15 found that a forced context erasure (memory kept) cuts write output 33–53% for ~10 turns. If context is the
coupling, the same erasure should cut the coupling to whatever was only in the context: messages read before it.

## Prediction
*Written 2026-10-04 (~02:40 UTC), before running C3 on any period.*

NE41 is the forced consolidation at the 41-turn cap (regime III): the context window is erased and memory kept, at a time
set by the scaffold, not the agent. Each erasure is a transition object (exception (c)); per-period estimates (G cards)
are combined by DerSimonian–Laird random effects.
- **E1:** pooled β_F < 0 with the 95% CI excluding 0 and a relative drop ≥ 30% of the in-context rate at the same age:
  an old sender read before a forced erasure is addressed less than an old sender read after it, in the same
  post-consolidation talk turns.
- **E2:** pooled β_V within ±50% of β_F.
- **E3:** voluntary segments are shorter when inflow per turn is higher (ρ < 0 in ≥ 2/3 of periods).
- **Rivals:** memory-mediated coupling (β_F ≈ 0: what matters is written to memory and read back); restart overhead only
  (absorbed by PC(τ) and the new-sender contrast).

**Verdict rule (fixed now):** supported if E1 holds; failed if the pooled β_F CI includes 0 or is positive; mixed if E1
holds in sign but the relative drop is < 30%.

## Result
*Run 2026-10-04 (`analysis/erasure.py`). Linear probability model with agent×day effects, 5 age bins, engaged flag, post-consolidation turn and new-sender indicators; day-bootstrap CIs; random-effects pooling.*

| Period | forced-erased units | β_F (pp) | relative | β_V (pp) | ρ E3 |
| --- | --- | --- | --- | --- | --- |
| G36 | 759 | -2.95 [-6.46, +0.03] | -0.12 [-0.26, 0.00] | -2.93 [-7.53, +1.68] | +0.36 |
| G37 | 357 | -10.86 [-13.65, -3.78] | -0.38 [-0.48, -0.13] | -7.27 [-9.81, -3.82] | +0.14 |
| G38 | 3028 | -0.98 [-2.39, +1.22] | -0.07 [-0.16, 0.08] | +3.33 [+1.44, +5.43] | +0.02 |
| G39 | 1399 | -2.22 [-9.76, -0.11] | -0.31 [-1.35, -0.02] | +0.14 [-7.47, +6.11] | -0.10 |
| G40 | 3182 | -1.04 [-2.09, -0.02] | -0.10 [-0.21, -0.00] | -2.28 [-3.17, -1.14] | -0.34 |
| G41 | 1825 | -1.27 [-4.60, +2.25] | -0.07 [-0.26, 0.13] | -1.21 [-4.65, +2.17] | +0.06 |
| G42 | 1216 | -4.45 [-8.12, -1.63] | -0.22 [-0.41, -0.08] | -1.79 [-5.05, +0.18] | -0.08 |
| G44 | 1087 | -4.92 [-7.12, -2.38] | -0.23 [-0.33, -0.11] | -6.61 [-9.85, -3.04] | -0.10 |
| G51 | 62966 | -1.74 [-2.00, -1.50] | -0.21 [-0.25, -0.18] | -1.94 [-2.26, -1.62] | -0.11 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| E1 pooled β_F < 0, relative drop ≥ 30% | β_F = -2.53 pp [-3.65, -1.42] (k = 9, I² = 0.69); relative -18% ± 6%; CI excludes 0 in 6/9 periods | sign only |
| E2 β_V within ±50% of β_F | β_V = -2.18 ± 1.51 pp | pass |
| E3 ρ < 0 in ≥ 2/3 of periods | 5/9 | fail |

**Verdict: mixed** (rule fixed in Prediction). Figure: `figures/ne41.pdf`.

## Scorecard (test-specific axes)
| Axis | |
| --- | --- |
| E interventional | forced erasures at the scaffold's 41-turn cap: exogenous timing; pooled β_F -2.53 pp |
| H comparative | memory-mediated coupling (β_F ≈ 0) rejected; restart overhead absorbed by PC and the new-sender contrast |

## Round 1b prediction (native, improved data)
*Written 2026-10-04 06:40 UTC, before the round-1b run.* Same design, rebuilt on the DQ1 context ledger: talk turns are ledger talk calls; "read" = the message's receiving call (`context_ledger_items`); an erasure separates read-out from the talk turn iff a call in (receiving call, talk call] carries `reset_forced` (forced, the 41-turn cap) or `reset_consol & ~reset_forced` (voluntary). The H15 catalog is no longer used. Responses: mention (as round 1) and **reply** (the talk's `reply_pairs` parent was written by the sender; new primary, since mentions are superseded).
- **E1b:** pooled β_F < 0 (CI excludes 0) for the reply response, and for the mention response; relative drop ≥ 30% (as pre-registered).
- **E2b:** β_V within ±50% of β_F.
- **Prior credence (Claude, 2026-10-04):** sign 0.75, size ≥ 30% 0.3 (round 1: −18% ± 6%).

**Verdict rule (fixed now, as round 1):** supported if E1b holds for the reply response; failed if its pooled β_F CI includes 0 or is positive; mixed if the sign holds but the drop is < 30%.

## Round 1b result (2026-10-04)
*Run `analysis/erasure_ledger.py` (ledger reset flags, ledger read-out calls; responses mention and reply author). Data: `data/processed/H08-context-is-the-coupling/r1b/ne41_pooled.json`, `r1b/G<NN>/c3.json`. β in percentage points; day-bootstrap CIs; DerSimonian–Laird pooling over 9 periods.*

| Period | forced-erased units | β_F mention | **β_F reply author** | relative (reply) | β_V reply |
| --- | --- | --- | --- | --- | --- |
| G36 | 834 | -2.78 [-7.28, +1.10] | -2.36 [-3.54, -1.91] | -16% [-24, -13] | -2.01 [-3.52, -0.91] |
| G37 | 539 | -10.44 [-13.60, -7.49] | -7.99 [-12.37, -6.46] | -30% [-47, -24] | -8.10 [-15.10, -5.46] |
| G38 | 4106 | +0.50 [-0.76, +2.12] | -1.29 [-2.69, +0.10] | -9% [-18, +1] | -1.15 [-2.44, +0.26] |
| G39 | 1516 | -1.47 [-7.48, +0.34] | -0.98 [-2.92, -0.21] | -31% [-92, -7] | -0.24 [-1.22, +1.88] |
| G40 | 3693 | -1.13 [-2.16, -0.10] | -0.78 [-1.26, -0.15] | -18% [-29, -3] | -0.09 [-1.41, +1.45] |
| G41 | 2448 | -1.30 [-4.23, +1.59] | -1.48 [-3.16, -0.76] | -16% [-34, -8] | -2.78 [-3.57, -1.70] |
| G42 | 1365 | -3.07 [-7.18, -0.19] | -3.08 [-4.31, -2.27] | -29% [-41, -22] | -2.04 [-2.79, -1.09] |
| G44 | 1296 | -4.48 [-6.83, -1.81] | -2.22 [-3.18, -0.73] | -16% [-23, -5] | -2.15 [-2.83, -1.56] |
| G51 | 91862 | -1.60 [-1.87, -1.34] | -1.69 [-1.94, -1.42] | -33% [-37, -27] | -1.39 [-1.67, -1.08] |

| Pooled | mention | reply author |
| --- | --- | --- |
| β_F (pp) | -2.52 ± 1.36 | -1.97 ± 0.64 |
| β_V (pp) | -1.61 ± 1.38 | -1.70 ± 0.59 |
| relative drop, forced | -16% ± 8 | -21% ± 7 |
| relative drop, voluntary | -10% ± 9 | -19% ± 6 |

- **E1b:** sign holds for both responses (reply: CI excluding 0 in 8/9 periods; G38 touches 0); size fails (−21% vs ≥ 30%). Round 1 (mention, H15 catalog): −2.5 pp, −18% ± 6%.
- **E2b:** β_V within ±50% of β_F for the reply response (−1.70 vs −1.97 pp): holds.
- **Reading:** the result is robust to the erasure catalog (ledger flags instead of H15's segment rule) and to the response measure (reply labels instead of mentions). #51 shows the largest relative cut on replies (−33%).

**Verdict (1b): mixed** (unchanged).

## Round 2 (2026-10-05)
*R4, the memory dose (card "Round 2"; predictions 2026-10-05 02:45 UTC, amendment R4-A1 after the synthetic guard, before real data). Role: native. Data: `r2/r4_pooled.json`, `r2/G<NN>/r4_dose.json`.*

| Prediction | Observed (reply author, pooled over 9 periods, DerSimonian–Laird) | Verdict |
| --- | --- | --- |
| R4-P1 memory protects: CF × dose > 0, π ≥ 0.5 | CF × dose -0.36 ± 0.55 pp (π ≈ -0.26); G51 alone -0.64 [-0.95, -0.28] | not supported; **inconclusive** (synthetic power 0.04 at π = 0.5, 0.22 at π = 1) |
| R4-P2 salience: placebo dose predicts replies | β_z +5.5 ± 1.0 pp; CI > 0 in 7/9 | supported |
| forced-erasure cut in this sample (CF, z = 0) | -1.37 ± 0.29 pp | consistent with round 1b |
| R4-P3 dose rate | 48–90% of forced-erased units have the sender newly written to memory | descriptive |

**Reading:** agents usually write the senders they are engaged with into memory (dose rate 48–90%), and those senders get more replies whether or not an erasure intervened. Writing the name does not measurably restore the coupling the erasure cut; in G51, the only well-powered period, the cut is if anything larger for named senders. The test cannot reject protection (power ≤ 0.22 even for full protection).

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/ne41_pooled.json`, `G<NN>/c3.json`.
- Forced / voluntary labels come from H15's catalog (`data/processed/H15-semantic-information-scrambles/consolidations.parquet`).
