# H54 × NE34: the kickoff as quench target, across all eligible goal changes

**Verdict:** mixed (P1 supported in both embedding models; P2 mixed; P3 failed; round 2: human-message re-quench is read-out coupling (R3), the first plan is not a target (R2))
**Role:** replication (cross-kickoff tests; exception (c), the transition is the object)
**Period:** 33 eligible non-holdout kickoffs (#3–#51 minus holdout and #23), regimes I (22), II (3), III (8). Each period is compared in its own regime's whitened basis.

## Why this
A goal change replaces the field. Across many kickoffs a swap design is possible: each day-1 centroid can be scored against its own kickoff and 32 others. The specificity, remanence and family questions need many kickoffs.

## Prediction
*Written 2026-10-04 in the card (P1–P7, credences there) before any real-data run; Amendment 1 after the synthetic run.*

## Result
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 median π ≥ 0.9, top-1 ≥ 50%, Wilcoxon p < 0.001 | median 1.00, top-1 0.55 (within regime 0.70), p = 3.0e-06 | **supported** |
| P1b beats both neighbouring kickoffs in ≥ 80% | 0.85 | supported |
| P1c displacement median π ≥ 0.85; jump > 0 in ≥ 80% | 0.91 (n = 25); 0.92 (median jump 0.33) | supported |
| P1d kickoff beats goal text in ≥ 60% | 0.55 (goal text alone: median π 1.00, top-1 0.52) | failed (equally good targets) |
| P2 precision ≥ 0.6, enrichment ≥ 2, Fisher p < 0.05 | precision 0.69 (9/13), base 0.35, enrichment 1.95, p = 0.010 (stratified permutation 0.080) | **mixed** (power ≈ 0.3–0.5) |
| P2, goal-text naming only (secondary) | precision 0.69, base 0.22, enrichment 3.22, p = 1.3e-04 (stratified 0.006); leave-one-period-out min enrichment 2.97 | strong |
| P2b ≥ half of frozen projects are carry-overs (rival R1) | pre-existing 0.08 (1/13); carry-over 1/9 known | failed (R1 rejected) |
| P2c same pattern, own rule on deterministic labels | any naming: enrichment 2.68, p = 0.0010; goal text: enrichment 4.40, p = 1e-5 | holds |
| P3 Spearman(S_text, σ) ≤ −0.35 | 0.17 (partial 0.29); S_count -0.08 | **failed** |
| P3, embedding distinctiveness S_emb (secondary) | spread -0.47 (p = 0.003; partial -0.36, p = 0.06); regime I -0.16, regime III -0.64 | weak, regime-III driven |
| P3b Spearman(S_text, depth) ≥ 0.35 | 0.12 | failed (S_emb +0.58 is partly mechanical) |
| P3c frozen share rises with S_text (per-project, n_named controlled) | coefficient 0.59 ± 0.56; per-period ρ 0.39 (count-inflated) | failed |
| P4 human re-quench median Δ > 0 (HH180) | 0.039, positive 0.57, sign p = 0.033 (n = 171); vs specificity ρ 0.02; vs receptive fraction ρ -0.16 (75% of messages read by all within 30 min) | main part holds; moderators failed |
| P5 remanence (HH182): last-day excess > 0 in ≥ 70% | 0.89 (n = 28); plateau A∞ median 0.11 from 0.27; τ_K median 1.18 active days | supported |
| P5 τ_K ≥ 3 τ_H | τ_K ≈ 5.1 active h vs τ_H < 1 h (grid floor) | supported (rough) |
| P5 previous-kickoff remanence on day 1 | median 0.011, p = 0.34 | failed (the new kickoff erases the old one) |
| P6 first plan central in ≥ 60% (HH181) | 0.70 (median percentile 0.69, p = 0.003); vs S_text ρ 0.14 (predicted < 0); plans name no frozen project | central: holds; moderator and naming: failed |
| P7 family susceptibility (HH184) | lab effect p = 0.66; agent split-half r = 0.09 (style-residualized 0.27); individual moves toward the kickoff in 0.87 of agent-kickoffs | failed |

**Robustness (post hoc, `robustness.json`).** P1 without near-echo statements (cosine to own kickoff > 0.5 dropped, 9% of statements): median π 0.97, top-1 0.45. At > 0.3 dropped (28%): 0.91 / 0.30. With DQ5 style-residualized vectors: 1.0 / 0.52. Chat only: 1.0 / 0.52.

**Post hoc moderator.** P1 fails exactly where the kickoff names no shared target: free-choice weeks #3 (π 0.0) and #16 (0.13), #51's private goals (0.25), #44's half-free week (0.47). Free-mode median π 0.81 vs 1.0 elsewhere (Mann–Whitney p = 0.02).

Data: `data/processed/H54-kickoff-quench-target/NE34/` (`periods.parquet`, `S_kick.npy`, `projects` via `../projects.parquet`, `human.parquet`, `remanence.parquet`, `plans.parquet`, `chi.parquet`, `results.json`, `robustness.json`). Figures: `../../figures/summary_obs.pdf`, `remanence.pdf`, `synthetic_validation.pdf`.

## Scorecard (period-specific axes)
- **C:** swap null beaten (P1); base-rate and stratified nulls for naming (P2); decoy-message null for human re-quenches.
- **D:** unfitted: displacement direction, neighbour decoys, frozen-project naming, remanence plateau.
- **E:** each kickoff is a step; predicted target identified in 29/33 (π ≥ 0.75).
- **H:** rival R1 (carry-over, inertia) and R0 rejected; R2 (genre) controlled by genericness correction; R3 (first plan) partly (plans are central but name no frozen project); R4 (family) shows no susceptibility differences.

## Round 2 (2026-10-04): embedding swap and read-out tests across kickoffs
*Predictions in the card's "Round 2" section, written before any round-2 statistic; Amendment R2-1 after synthetic S6.*

| Prediction | bge | gte | Verdict |
| --- | --- | --- | --- |
| R5-P1 P1 rule | median π 1.0, top-1 18/33, p 3e-6 | median π 1.0, top-1 20/33, p 2e-7 | supported |
| per-period π agreement | – | Spearman 0.75 (p 6e-7); verdicts agree 29/33 | supported |
| R5-P1c move points at the kickoff | 0.91 | 0.97 (jump > 0 in 21/25) | supported |
| R3-A read-out re-quench (181 human messages) | mean Δ 0.090 [0.071, 0.109], 75% > 0 | 0.088 [0.069, 0.107], 71% > 0 | supported |
| R3-B read minus in flight, matched lag × age | +0.11 [0.05, 0.17] | +0.12 [0.07, 0.18] | supported |
| convergence share (in flight / read) | 0.48 | 0.40 | – |
| R3-C named minus unnamed | +0.02 [−0.03, 0.08] | +0.03 [−0.03, 0.09] | failed |
| R2-A first-plan readers (36 plans) | −0.105 [−0.153, −0.059] | −0.099 [−0.135, −0.062] | failed (reversed) |
| R2-B plans, read minus in flight | −0.11 [−0.28, 0.12] | −0.00 [−0.17, 0.12] | inconclusive (power 0.05) |

Post hoc: the read-out pull falls from 0.22 (first message < 30 s after reading) to ≈ 0 by 10 min; round-1 P4 (room centroids) does not replicate under gte (median 0.012, p 0.18). Data: `data/processed/H54-kickoff-quench-target/r2/` (`r3.json`, `r2.json`) and `r2_gte/NE34/`.

## Notes
- 2026-10-04: written after the round-1 run by `analysis/period_folders.py`.
