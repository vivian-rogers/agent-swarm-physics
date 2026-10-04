# H14 × G37: Pick your own goal! (2026-03-30 → 2026-04-01)

**Verdict:** failed
**Verdict (1b):** failed (unchanged: the pre-registered coarse chain did not change). Corrected fine classes (shell sub-classes): 100% of test agents irreversible, 75% after scaffold removal with burn-in; pooled Jev v3 arrow not significant (flip p 0.134)
**Role:** exploratory
**Period:** regime III · mode F (free choice) · N = 13 · #best/#rest rooms · 3 days × 4 h. No step change inside.

## Why this period
The first regime-III goal and the only free-choice regime-III period outside the holdout: the 'aimless activity' end of the card's practical payoff (P7). Short (3 days), so the day-fold cross-fit has only 3 folds.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions (`../../README.md`, "Prediction") as they apply here:
- **P2:** ≥ 80% of agents with ≥ 1,000 transitions above the DB-surrogate 95th percentile.
- **P5:** work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75% of agents; one of them dominant.
- **P7 (low credence):** the lowest median Σ_i per transition among the regime-III non-holdout periods.
- **P4:** ΔΣ_MF and ΔΣ_PW within the cross-day null (3 days: power too low, and only 3 day-derangements exist per agent).

Verdict rule: **supported** if P2 and P5 hold (P7 reported separately); **mixed** if P2 holds and P5 fails; **failed** if P2 fails.

## Result
*Run 2026-10-03 (exploratory, non-holdout). Primary single-agent estimator: H05's cross-fitted Newton bound (the pre-registered switch rule did not fire); companion `cfx` = cross-fitted exact dual minus its DB-null mean. DB surrogates: 200 per agent.*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2: ≥ 80% of agents (≥ 1,000 transitions) above the DB-surrogate 95th pct | 0.11 of 9 (cfx: 0.11); median Σ_i 0.002 (Newton), excess 0.003; cfx excess -2.3e-04 nats/transition | 5% expected under the null | ✗ |
| P2 (minute grid): ≥ 60% above null; per-hour lower than on turns for ≥ 80% | 0.11 of 9; per-hour lower for 0.50 | | ✗ |
| P5: work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75%; one dominant | 0.17 and 0.42 positive; dominant: work>chat>cons | sign tests p = 0.039, 0.774 | ✗ |
| P4: ΔΣ_MF within the cross-day null | excess -0.0456 (observed -0.0267), p = 0.980; ΔΣ_PW excess 0.0083, p = 0.446 | null mean 0.0190 ± 0.0250 (MF), 0.0944 ± 0.0334 (PW); N = 12, 3 days | ✓ |
| HH67 strong form: ΔΣ > Σ_1 | ΔΣ_MF excess / Σ_1 = –; ΔΣ_PW excess / Σ_1 = – (Σ_1 = Σ_i cfx on the grid = -0.4054) | | strong form holds |
| P3 (family, descriptive here unless G38/G51) | η²_lab = 0.10 (perm p = 0.811, chance 0.27); adjusted for shell share and log n: 0.41 (p = 0.217); Anthropic − OpenAI = 0.0069 (two-sided p = 0.769) | labs: Anthropic 5, DeepSeek 1, Google 2, OpenAI 4; cfx companion η² 0.15 (p 0.704) | descriptive |

**Verdict: failed.** Other numbers: act-scheme share above null 0.89; order 2 beats order 1 (held-out likelihood) for 0.42 of agents, order-2 bound > pair bound for 0.67; removing consolidate loses a median 0.52 of the excess (the rest stays above null for 0.11); median plug-in EP share in consolidate transitions 0.51.

Per-agent table (eligible agents; excess = estimate − DB-null mean, nats/transition; Newton primary, cfx companion):

| Agent | Lab | Transitions | Σ_i Newton | p | cfx excess | p | Newton excess/h | Minute excess/h | work>chat>idle A | work>chat>cons A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Sonnet 4.5 | Anthropic | 571 | 0.062 | 0.005 | 0.042 | 0.035 | 1.74 | -0.56 | -1.54 | 0.00 |
| Claude Opus 4.5 | Anthropic | 1360 | 0.021 | 0.010 | 0.022 | 0.050 | 1.35 | -0.63 | -1.19 | -0.56 |
| GPT-5.2 | OpenAI | 661 | 0.021 | 0.075 | 0.025 | 0.129 | 0.65 | -0.64 | -0.11 | 2.06 |
| GPT-5.1 | OpenAI | 893 | 0.020 | 0.070 | 0.014 | 0.313 | 0.85 | 1.27 | -1.23 | 1.71 |
| GPT-5.4 | OpenAI | 1172 | 0.003 | 0.303 | -0.037 | 0.975 | 0.20 | 0.56 | 0.08 | 3.4e-03 |
| Gemini 2.5 Pro | Google | 2461 | 0.003 | 0.075 | 0.002 | 0.458 | 0.34 | 0.47 | 0.00 | 0.00 |
| Claude Opus 4.6 | Anthropic | 1526 | 0.002 | 0.289 | -0.012 | 0.876 | 0.17 | -0.32 | -0.19 | -1.26 |
| DeepSeek-V3.2 | DeepSeek | 2215 | 0.002 | 0.299 | -0.012 | 0.950 | 0.15 | -0.09 | 0.52 | 0.52 |
| Claude Haiku 4.5 | Anthropic | 1775 | 6.7e-04 | 0.408 | 0.007 | 0.254 | 0.07 | 1.06 | -1.29 | 0.72 |
| Gemini 3.1 Pro | Google | 2915 | 2.5e-04 | 0.517 | -0.002 | 0.697 | -0.03 | 0.84 | -0.06 | -0.40 |
| Claude Sonnet 4.6 | Anthropic | 1534 | -0.005 | 0.905 | -0.011 | 0.881 | -0.42 | -0.20 | -0.02 | -0.05 |
| GPT-5 | OpenAI | 1592 | -0.007 | 0.965 | -0.041 | 1.000 | -0.49 | -0.94 | 0.00 | -0.03 |

Figures: [`figures/period_summary.pdf`](figures/period_summary.pdf). Data: `data/processed/H14-behavior-entropy-production/G37/` (`agents.parquet`, `results.json`). Code: `analysis/run_period.py --period G37`.

## Scorecard (period-specific axes)
- **C (adequacy):** single-agent arrows beat the DB surrogate for 0.11 of test agents (held-out, day-blocked cross-fit). Collective term vs. cross-day null: p = 0.980 (MF), 0.446 (PW).
- **D (unfitted):** cycle orientations (P5) are not fitted by the EP estimator: not as predicted.
- **G (ground truth):** the consolidate-linked cycle is scaffold-imposed (consolidation cadence); see the card for how much EP it carries.

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods). Predictions: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H14-behavior-entropy-production/r1b/G37/`.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| coarse chain: share of test agents above DB null (median Newton excess) | 0.11 (0.0026) | 0.11 (0.0027), same transitions |
| fine classes: share above null (median excess) | `act`, shell unsplit: 0.89 (0.079) | act_sh, 7 shell sub-classes: 1.00 (0.116) |
| scaffold removed (agent-only chain, 3-transition burn-in): share above null | – | coarse_b3 0.00; act_sh_b3 0.75 |
| share of the median excess kept after scaffold removal | coarse, consolidate decimated: 0.48 | coarse_b3 0.50; act_sh_b3 0.66 |
| Jev v3 pooled EP per 5-min transition (block-flip p) | – | 0.0096 (p 0.134); argmax -0.0043 (DB p 0.726) |
| Jev v3 per agent: share above flip null (n) | – | n/a (0); descriptive (soft tests nearly blind per agent) |

The window-level burn-in variants (v3s_b1, b1c) are selection artifacts (card, Round 1b) and are not reported here.
