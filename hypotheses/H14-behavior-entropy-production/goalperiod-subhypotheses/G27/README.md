# H14 × G27: Hack the OWASP Juice Shop playground (2026-01-12 → 2026-01-23)

**Verdict:** mixed
**Verdict (1b):** mixed (unchanged: the pre-registered coarse chain did not change). Corrected fine classes (shell sub-classes): 100% of test agents irreversible, 90% after scaffold removal with burn-in; pooled Jev v3 arrow significant (flip p 0.005)
**Role:** replication (exploratory)
**Period:** regime I · mode K (competition turned collaboration) · N = 10 · #general only (rooms arrive 02-25) · 10 days × 4 h. No step change inside.

## Why this period
The regime comparison (O7, P6). Regime I runs discrete computer sessions (START/STOP_USING_COMPUTER) with chat mostly outside them, and idling is message-triggered (H09 E6: escape hazard ×3.06 after a room message). It is the longest regime-I non-holdout period with a stable roster of 10 from 4 labs. Model ranking: 02 Nonequilibrium Ising is #27's top model in `goal-periods.md`.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions (`../../README.md`, "Prediction") as they apply here:
- **P2:** ≥ 80% of agents with ≥ 1,000 transitions have Σ_i (coarse, turns) above the DB-surrogate 95th percentile.
- **P5 (regime I):** the dominant `lump4` cycle is consolidate (session start/stop) → chat → work → consolidate, with that orientation in ≥ 75% of agents.
- **P6:** the median Σ_i per transition is ≥ 2× every regime-III period's median.
- **P4 (period-specific):** ΔΣ_MF above the cross-day null 95th percentile. Regime I is message-triggered, so others' chat should asymmetrically precede one's own chat or work. ΔΣ_PW: no prediction (45 pairs × 2 + 150 single observables vs. ~2,300 bins).
- Family (P3) is descriptive here: 10 agents, 4 labs.

Verdict rule: **supported** if P2, P5 and P6 hold; **mixed** if P2 holds and one of P5/P6 fails; **failed** if P2 fails. P4 is reported against its stated direction.

## Result
*Run 2026-10-03 (exploratory, non-holdout). Primary single-agent estimator: H05's cross-fitted Newton bound (the pre-registered switch rule did not fire); companion `cfx` = cross-fitted exact dual minus its DB-null mean. DB surrogates: 200 per agent.*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2: ≥ 80% of agents (≥ 1,000 transitions) above the DB-surrogate 95th pct | 1.00 of 10 (cfx: 0.90); median Σ_i 0.073 (Newton), excess 0.073; cfx excess 0.145 nats/transition | 5% expected under the null | ✓ |
| P2 (minute grid): ≥ 60% above null; per-hour lower than on turns for ≥ 80% | 1.00 of 10; per-hour lower for 0.50 | | ✗ |
| P5: consolidate → chat → work → consolidate in ≥ 75%, dominant | reverse-orientation share 0.60; dominant cycle: work>chat>cons | sign test p = 0.754 | ✗ |
| P6: median ≥ 2× every regime-III median | holds: G27 median 0.0729 vs. regime-III medians G37 0.0025, G38 0.0032, G39 0.0048, G40 0.0064, G41 0.0100, G42 0.0075, G44 0.0083, G51 0.0090 | | ✓ |
| P4: ΔΣ_MF above the cross-day null | excess 0.0260 (observed 0.0500), p = 0.050; ΔΣ_PW excess -0.0104, p = 0.663 | null mean 0.0240 ± 0.0132 (MF), 0.0059 ± 0.0200 (PW); N = 10, 10 days | ✓ |
| HH67 strong form: ΔΣ > Σ_1 | ΔΣ_MF excess / Σ_1 = 0.021; ΔΣ_PW excess / Σ_1 = -0.009 (Σ_1 = Σ_i cfx on the grid = 1.2238) | | strong form fails |
| P3 (family, descriptive here unless G38/G51) | η²_lab = 0.61 (perm p = 0.133, chance 0.33); adjusted for shell share and log n: 0.49 (p = 0.232); Anthropic − OpenAI = 0.1424 (two-sided p = 0.053) | labs: Anthropic 4, DeepSeek 1, Google 2, OpenAI 3; cfx companion η² 0.67 (p 0.080) | descriptive |

**Verdict: mixed.** Other numbers: act-scheme share above null 1.00; order 2 beats order 1 (held-out likelihood) for 1.00 of agents, order-2 bound > pair bound for 0.80; removing consolidate loses a median 0.73 of the excess (the rest stays above null for 0.80); median plug-in EP share in consolidate transitions 0.55.

Per-agent table (eligible agents; excess = estimate − DB-null mean, nats/transition; Newton primary, cfx companion):

| Agent | Lab | Transitions | Σ_i Newton | p | cfx excess | p | Newton excess/h | Minute excess/h | work>chat>idle A | work>chat>cons A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Sonnet 4.5 | Anthropic | 5701 | 0.277 | 0.005 | 0.424 | 0.005 | 39.37 | 18.86 | -2.88 | -7.17 |
| Claude 3.7 Sonnet | Anthropic | 6108 | 0.186 | 0.005 | 0.330 | 0.005 | 28.27 | 11.28 | -2.23 | -9.05 |
| Gemini 2.5 Pro | Google | 6923 | 0.131 | 0.005 | 0.245 | 0.005 | 22.63 | 3.46 | -3.18 | -10.45 |
| Claude Haiku 4.5 | Anthropic | 9780 | 0.122 | 0.005 | 0.208 | 0.005 | 29.62 | 3.82 | -1.90 | -6.40 |
| Claude Opus 4.5 | Anthropic | 4975 | 0.096 | 0.005 | 0.193 | 0.005 | 11.91 | 14.51 | -0.80 | -6.93 |
| GPT-5 | OpenAI | 3176 | 0.050 | 0.005 | 0.097 | 0.005 | 3.94 | 1.80 | 0.09 | 0.15 |
| DeepSeek-V3.2 | DeepSeek | 5177 | 0.029 | 0.005 | 0.029 | 0.005 | 3.74 | 3.94 | 2.56 | 2.33 |
| Gemini 3 Pro | Google | 6112 | 0.020 | 0.005 | 0.030 | 0.005 | 3.05 | 8.35 | 3.82 | -0.12 |
| GPT-5.2 | OpenAI | 4900 | 0.019 | 0.005 | 0.021 | 0.005 | 2.28 | 4.01 | 1.28 | 1.01 |
| GPT-5.1 | OpenAI | 3581 | 0.015 | 0.005 | 0.001 | 0.413 | 1.32 | 4.91 | 1.56 | 0.56 |

Figures: [`figures/period_summary.pdf`](figures/period_summary.pdf). Data: `data/processed/H14-behavior-entropy-production/G27/` (`agents.parquet`, `results.json`). Code: `analysis/run_period.py --period G27`.

## Scorecard (period-specific axes)
- **C (adequacy):** single-agent arrows beat the DB surrogate for 1.00 of test agents (held-out, day-blocked cross-fit). Collective term vs. cross-day null: p = 0.050 (MF), 0.663 (PW).
- **D (unfitted):** cycle orientations (P5) are not fitted by the EP estimator: not as predicted.
- **G (ground truth):** the consolidate-linked cycle is scaffold-imposed (consolidation cadence); see the card for how much EP it carries.

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods). Predictions: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H14-behavior-entropy-production/r1b/G27/`.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| coarse chain: share of test agents above DB null (median Newton excess) | 1.00 (0.0730) | 1.00 (0.0729), same transitions |
| fine classes: share above null (median excess) | `act`, shell unsplit: 1.00 (0.148) | act_sh, 7 shell sub-classes: 1.00 (0.154) |
| scaffold removed (agent-only chain, 3-transition burn-in): share above null | – | coarse_b3 0.80; act_sh_b3 0.90 |
| share of the median excess kept after scaffold removal | coarse, consolidate decimated: 0.27 | coarse_b3 0.12; act_sh_b3 0.41 |
| Jev v3 pooled EP per 5-min transition (block-flip p) | – | 0.0115 (p 0.005); argmax 0.0055 (DB p 0.080) |
| Jev v3 per agent: share above flip null (n) | – | 0.20 (10); descriptive (soft tests nearly blind per agent) |

The window-level burn-in variants (v3s_b1, b1c) are selection artifacts (card, Round 1b) and are not reported here.
