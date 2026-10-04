# H06 × NE27: Batch join GPT-5, Grok 4, Opus 4.1 (N 4 → 7) (2025-08-18)

**Verdict:** failed ((a) failed: post λ̄ outside every model's 95% interval; (b) failed: the three kernels are within 0.03 nats)
**Role:** exploratory (spanning: #8 → #10)
**Period:** regime I · pre side #8 (2025-07-18 → 08-12, 4 agents, mode C, benchmark design) · post side #10 (08-18 → 08-22, 7 agents, mode I, games week). #9 (08-13 → 08-15) is held out and skipped. The join coincides with the goal change and with expanded hours.

## Why this natural experiment
Three agents with empty memories arrive at once: a pulse of new individuals. It tests (a) whether a model fitted before the join predicts λ after it at the new N, and (b) how newcomers choose projects, free of their own history (their first choices reveal the recruitment kernel).

## Prediction
*Written 2026-10-04, before running.*
- **(a) Fit before, predict after (axis E).** Each model is fitted on the pre side (intention clusters `km24`, profile synthetic likelihood). At the post side's N and label mask, its (μ, k) predicts the post-side λ̄. **NCD passes** if the observed post λ̄ lies inside its 95% predictive interval, and it is closer to the observation than Hubbell's prediction.
- **(b) Newcomer kernel (P9).** Newcomers' first-day choices, among the projects then held by other slots, give log-likelihoods for the kernels x(1−x) (NCD), x (Hubbell) and x(x + 0.2(1−x)) (conformist). **NCD passes** if its kernel has the highest likelihood (pooled over NE27 and NE33 for the card; per join here).
- **Verdict:** supported if (a) and (b) both pass; failed if both fail; mixed otherwise. "n/a" for (b) if newcomers make < 3 multi-option copy choices.
- **Expectation:** #10 is a games week with individual objectives, so newcomers likely start their own games (novel labels); a goal change at the join means (a) mostly measures the goal's effect, not the join's. Expect mixed or n/a.

## Result
*Run 2026-10-04 (exploratory round 1).* Data: `data/processed/H06-neutral-cooperative-dynamics/NE27_round1.json`; pre/post fits in `round1_<side>.json`. Script: `analysis/ne_tests.py`.

**(a) Fit before, predict after** (intention clusters km24). Observed λ̄: pre 0.29 (N = 4), post 0.20 (N = 7).

| Model | μ̂, k̂ (pre fit) | predicted post λ̄ [95%] | PPC p of observed post λ̄ | abs. error |
| --- | --- | --- | --- | --- |
| ncd | 0.044, 0.91 | 0.51 [0.41, 0.69] | 0.005 | 0.31 |
| hubbell | 0.204, 0.60 | 0.45 [0.34, 0.64] | 0.005 | 0.26 |
| conformist | 0.110, 2.14 | 0.58 [0.41, 0.75] | 0.005 | 0.38 |

**(b) Newcomer kernel.** Newcomers' first-day label changes: 6; to a novel or unheld project: 2; multi-option copy choices: 4. Log-likelihoods NCD / Hubbell / conformist: -5.38 / -5.38 / -5.40. Incumbents on the same day, for reference: 9 changes, 6 novel or unheld, 3 multi-option choices, log-likelihoods -3.77 / -3.91 / -4.18.

Round-1 outcome: failed ((a) failed: post λ̄ outside every model's 95% interval; (b) failed: the three kernels are within 0.03 nats). All three models, fitted on the pre side, predict a post-side λ̄ far above the observation: every model over-concentrates, the same misfit as within periods (agents mostly hold projects nobody else holds). Newcomers mostly start projects of their own (novel or unheld labels), so the kernel test has almost no choices to score.

## Notes
- 2026-10-04: folder created; predictions written before running.
- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`.
