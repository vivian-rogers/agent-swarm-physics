# H70 × NE41: forced context erasures at the 41-call cap: the call-scale κ table (regime III, 2026-03-24 →)

**Verdict:** failed (artifact row ≈ 0 value; the context row carries the value)
**Role:** native
**Period:** see "Why this period".

## Why this period
The scaffold erases the context window when a segment reaches 41 calls, at a time the agent did not choose; memory note, artifact and room stay. 21,165 non-holdout forced erasures and 21,806 pseudo-erasures at position 21 of no-reset runs give the HH307 rows with the same agents, days and estimator. Pooled over regime-III periods with agent-period strata (exception (c): each erasure is a transition object).

## Prediction
*Written 2026-10-04 20:05 UTC, before running this native test.*
- **N1a (artifact row):** I_A ≥ 0.3 bits (shuffle-corrected, CI > 0); ΔV_A > 0 with the CI excluding 0; κ_A finite and positive.
- **N1b (memory-note row):** I_M < I_A with non-overlapping CIs and ΔV_M's CI includes 0 (κ_M ≈ 0; H15).
- **N1c (room row):** I_R < I_A / 3; ΔV_R < ΔV_A.
- **N1d (context row):** ΔV_C = V(P) − V(F) > 0 (H15/H44: about −30 to −40% of commits); I_C < 0.3 × I_A.
- **Order:** κ_A > κ_R > κ_M (HH307's order restricted to the rows H70 estimates).
- **Counts against:** ΔV_A ≤ 0 with the CI excluding 0 (R2: reading precedes writing at least as much without an erasure), or I_M ≥ I_A (R1).

## Result
*Run 2026-10-04 (`analysis/run.py`).* Pooled regime III (#36b–#51 head), agent-period strata, agent-day cluster bootstrap (B = 300). 18,760 forced erasures and 19,886 pseudo-erasures with a known own artifact; 5,917 and 7,461 of them with a commit in the window.

| Channel | I_c (bits) | ΔV_rel | ΔV (commits / 20 calls) | κ_c (commits / 20 calls / bit) |
| --- | --- | --- | --- | --- |
| A artifact (re-read) | +0.138 [+0.12, +0.16] | -0.05 [-0.13, +0.01] | -0.08 [-0.22, +0.02] | -0.60 [-1.66, +0.15] |
| M memory note (intention) | +0.038 [+0.02, +0.06] | +0.05 [-0.07, +0.17] | +0.04 [-0.06, +0.12] | +1.04 [-1.65, +3.52] |
| R room (received items) | +0.020 [+0.01, +0.03] | +0.04 [-0.13, +0.31] | +0.02 [-0.08, +0.14] | +1.18 [-2.83, +5.70] |
| C context (erasure cost; I = info destroyed) | +0.078 [+0.05, +0.10] | +0.41 [+0.38, +0.44] | +0.41 [+0.35, +0.45] | +5.20 [+3.85, +8.37] |

DerSimonian–Laird over 9 periods: I_A 0.098 [0.044, 0.153] bits; ΔV_rel,A -0.069 [-0.147, +0.009]. Return to the own artifact given a commit: F 0.89, P 0.87.

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N1a I_A ≥ 0.3 bits; ΔV_A > 0 | I_A 0.14 [0.12, 0.16]; ΔV_rel −0.05 [−0.13, +0.01] | failed |
| N1b I_M < I_A; ΔV_M CI includes 0 | 0.04 vs 0.14 (non-overlapping); ΔV_M +0.05 [−0.07, +0.17] | supported |
| N1c I_R < I_A / 3; ΔV_R < ΔV_A | 0.02 vs 0.14; ΔV_R +0.04 (CI overlaps ΔV_A) | mixed |
| N1d ΔV_C > 0; I_C < 0.3 I_A | erasure cost 41% [38, 44] of output; I_C 0.078 = 0.56 I_A | mixed |
| order κ_A > κ_R > κ_M | κ_C 5.2 [3.8, 8.4] ≫ κ_A ≈ κ_M ≈ κ_R ≈ 0 (all CIs include 0) | failed |

**Reading.** Across a forced erasure the artifact pointer predicts where the next commit goes (0.14 bits beyond agent identity; 89% return), but opening that channel (re-reading the repo in calls 1–5) adds no output beyond what re-reading adds with the context intact. The context window is the valuable store per bit: losing it costs 41% of the next 20 calls' commits while destroying only 0.08 bits of allocation information, so its value is in *how* to continue, not *where*. The memory note and the room carry little allocation information and no measurable value.

## Scorecard (period-specific axes)
- **E:** 21k scaffold-timed erasures are the intervention; the context row's cost replicates H15/H44 (−41% here vs −39% in H15). **H:** R2 (reading precedes writing) beats the artifact-value model; R1 (memory note) fails too. **F:** call-scale power 1.0 for a +30% channel value, size ≈ 0.1 (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/natives.json` (key `NE41`).
