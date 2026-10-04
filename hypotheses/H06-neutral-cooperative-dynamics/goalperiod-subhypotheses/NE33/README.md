# H06 × NE33: Batch join Muse Spark 1.3, Gemini 3.8 Flash, GPT-6 Astra (+3) (2026-09-03/04)

**Verdict:** failed ((a) failed: post λ̄ outside every model's 95% interval; (b) n/a, < 3 multi-option newcomer choices)
**Role:** exploratory (spanning, inside #51)
**Period:** regime III · #51 (private assigned roles) · pre side 2026-08-31 → 09-02 · post side 09-03 → 09-04 (the only non-holdout days after the join; the #51 tail from 09-07 is held out). ≈ 29 → 32 agents.

## Why this natural experiment
Same goal before and after (no goal confound, unlike NE27), but only two post days, and newcomers receive assigned roles (a field).

## Prediction
*Written 2026-10-04, before running.*
- **(a) Fit before, predict after (axis E).** Each model is fitted on the pre side (intention clusters `km24`, profile synthetic likelihood). At the post side's N and label mask, its (μ, k) predicts the post-side λ̄. **NCD passes** if the observed post λ̄ lies inside its 95% predictive interval, and it is closer to the observation than Hubbell's prediction.
- **(b) Newcomer kernel (P9).** Newcomers' first-day choices, among the projects then held by other slots, give log-likelihoods for the kernels x(1−x) (NCD), x (Hubbell) and x(x + 0.2(1−x)) (conformist). **NCD passes** if its kernel has the highest likelihood (pooled over NE27 and NE33 for the card; per join here).
- **Verdict:** supported if (a) and (b) both pass; failed if both fail; mixed otherwise. "n/a" for (b) if newcomers make < 3 multi-option copy choices.
- **Expectation:** Newcomers get assigned roles, so their first labels should be novel (fields), and (b) n/a or uninformative. (a) is a clean test of the N-scaling of λ only if the fitted μ stays put; expect weak evidence (two post days).

## Result
*Run 2026-10-04 (exploratory round 1).* Data: `data/processed/H06-neutral-cooperative-dynamics/NE33_round1.json`; pre/post fits in `round1_<side>.json`. Script: `analysis/ne_tests.py`.

**(a) Fit before, predict after** (intention clusters km24). Observed λ̄: pre 0.04 (N = 29), post 0.04 (N = 32).

| Model | μ̂, k̂ (pre fit) | predicted post λ̄ [95%] | PPC p of observed post λ̄ | abs. error |
| --- | --- | --- | --- | --- |
| ncd | 0.204, 0.39 | 0.12 [0.09, 0.15] | 0.005 | 0.07 |
| hubbell | 0.081, 0.26 | 0.29 [0.17, 0.58] | 0.005 | 0.25 |
| conformist | 0.110, 0.91 | 0.57 [0.15, 0.75] | 0.005 | 0.53 |

**(b) Newcomer kernel.** Newcomers' first-day label changes: 19; to a novel or unheld project: 18; multi-option copy choices: 1. Log-likelihoods NCD / Hubbell / conformist: -3.25 / -3.26 / -3.28. Incumbents on the same day, for reference: 184 changes, 163 novel or unheld, 21 multi-option choices, log-likelihoods -67.48 / -67.57 / -67.88.

Round-1 outcome: failed ((a) failed: post λ̄ outside every model's 95% interval; (b) n/a, < 3 multi-option newcomer choices). All three models, fitted on the pre side, predict a post-side λ̄ far above the observation: every model over-concentrates, the same misfit as within periods (agents mostly hold projects nobody else holds). Newcomers mostly start projects of their own (novel or unheld labels), so the kernel test has almost no choices to score.

## Notes
- 2026-10-04: folder created; predictions written before running.
- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`.
