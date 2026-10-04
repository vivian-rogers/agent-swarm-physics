# H30 × G05: Holiday: do whatever you like! Next goal will begin soon (2025-06-19 → 2025-06-26)

**Verdict:** mixed — content 0.023*, named 0.046; human activity ≈ 0; low power
**Verdict (1b):** mixed (r1 mixed) · native dilution: failed
**Role:** native (round 1b: human dose and dilution; round-1 role: exploratory replication)
**Period:** regime I · mode F · 4 agents at start · 5 active days.

## Why this period
Regime I holiday week with very dense human chat (≈ 176 messages/day over 5 days): many kicks per day, few days.

## Prediction
*Written 2026-10-03, before running on this period.*

- P3: χ_act(H_men) > χ_act(H_und), ratio ≥ 2; χ_act(H_und) > 0 (CI excluding 0 counts toward the 2-of-3 rule over G04–G06).
- P4: χ_con(H_und or H_men) > 0 with CI excluding 0, size 0.02–0.10; H_men ≥ H_und.
- P6: the daily human *content* gauge has permutation-calibrated R₁ < 0.5; the activity heterogeneity test is not run (dense chat, A1).
- Against: χ_con ≤ 0 or χ_act(H_men) ≤ χ_act(H_und).

## Round 1b native test: human dose and dilution (prediction)
*Written 2026-10-04 07:31 UTC, before computing any round-1b statistic on #5. Seen before writing: DQ9's catalog entry (881 human messages from 86 speakers, ~88 per active hour, 145 naming an agent) and the round-1 G05 numbers above.*

**Why #5:** it is the only period where an agent's model call routinely reads several human messages at once (chat-mode calls about every 74 s against ~88 human messages an hour), so the per-message content susceptibility can be measured as a function of how many human messages share the same read-out. No goal field competes with the messages (holiday week).

**Design.** Round-1b content estimator (orthogonalized χ_con, receiving-call timing from the DQ1 ledger, bge-small primary, gte-modernbert robustness). Each (message, recipient) pair gets k_h = the number of human messages that entered the same receiving call. Bins k_h ∈ {1}, {2–3}, {4–7}, {8+}; mean χ_con per bin with a day-block bootstrap; log-log slope of χ_con on the bin's mean k_h (weighted least squares on bin means, bootstrap CI).

**Predictions:**
- **N1 (dilution):** χ_con falls with k_h: slope < 0 with CI excluding 0, and χ_con(k_h = 1) ≥ 2 × χ_con(k_h ≥ 8).
- **N2 (address premium survives dilution):** H_men > H_und at matched k_h in at least 2 of the bins that hold ≥ 30 named pairs.
- **Verdict rule (native):** supported if N1 holds (N2 reported); failed if the slope is ≥ 0; mixed otherwise. Credence 0.55 (if agents answer only the newest or most salient message, dilution could be steeper than 1/k; if they summarise, flatter).

### Round 1b native result (dilution)
*Run 2026-10-04 ~08:20 UTC (`analysis/r1b_extra.py`; `data/processed/H30-operator-susceptibility/r1b/natives.json`). k_h from the DQ1 ledger (human items in the same receiving call); day-block bootstrap over the 5 days.*

| Class (model) | k_h = 1 | 2–3 | 4–7 | 8+ | log-log slope |
| --- | --- | --- | --- | --- | --- |
| all (bge) | 0.025 [0.019, 0.033] (n 1501) | 0.020 [0.017, 0.024] (n 1207) | 0.013 [0.005, 0.016] (n 435) | 0.047 [-0.023, 0.074] (n 196) | 0.19 [-1.17, 0.46] |
| all (gte) | 0.030 [0.026, 0.035] (n 1501) | 0.022 [0.017, 0.025] (n 1207) | 0.015 [0.007, 0.020] (n 435) | 0.043 [-0.017, 0.071] (n 196) | 0.09 [-1.40, 0.35] |
| H_und (bge) | 0.024 [0.017, 0.034] (n 1424) | 0.019 [0.015, 0.022] (n 1158) | 0.012 [0.004, 0.016] (n 423) | 0.042 [-0.023, 0.072] (n 190) | 0.15 [-1.32, 0.46] |
| H_und (gte) | 0.030 [0.026, 0.034] (n 1424) | 0.020 [0.015, 0.023] (n 1158) | 0.016 [0.005, 0.021] (n 423) | 0.040 [-0.017, 0.071] (n 190) | 0.08 [-1.35, 0.37] |
| H_men (bge) | 0.030 [0.017, 0.042] (n 77) | 0.039 [0.015, 0.057] (n 49) | 0.046 [0.033, 0.118] (n 12) | 0.195 [0.127, 0.262] (n 6) | – |
| H_men (gte) | 0.041 [0.030, 0.050] (n 77) | 0.066 [0.034, 0.097] (n 49) | 0.009 [-0.024, 0.083] (n 12) | 0.117 [0.094, 0.140] (n 6) | – |

- **N1 (dilution):** slope +0.19 [-1.17, 0.46] (bge), ratio k=1 / k≥8 0.53: **not met**. Over the three well-sampled bins the per-message pull falls monotonically (0.025 → 0.020 → 0.013, roughly ∝ k^−0.4, in both models), but the 8+ bin (196 pairs, concentrated on a few busy hours) is high and noisy and flips the fitted slope.
- **N2 (address premium):** H_men > H_und in both bins with ≥ 30 named pairs (k = 1: 0.030 vs 0.024; k = 2–3: 0.039 vs 0.019). ✓
- **Native verdict: failed** by the pre-registered rule (slope ≥ 0). Post hoc reading: dilution holds over 1–7 messages per read-out; the claim fails at the largest doses, where the agent may answer only one salient message.

## Result
Days: 5; kicks by class: {'H_men': 151, 'H_und': 3329}; content pairs with statements on both sides: 3352.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P3 χ_act(H_men) vs χ_act(H_und), min per message-recipient | H_men -0.96 [-1.63, -0.46]; H_und -0.06 [-0.68, 0.21]; ratio 14.89 | day-swap H_und 0.02 [-0.11, 0.16] | failed |
| P4 χ_con(H_und), cosine | 0.023 [0.019, 0.027] (n = 3206; matched 0.028 [0.021, 0.034]) | pseudo-true null 0.001 [-0.002, 0.005] | supported |
| P4 χ_con(H_men), cosine | 0.046 [0.035, 0.054] (n = 146; matched 0.073 [0.049, 0.098]) | pseudo-true null -0.008 [-0.022, 0.007] | supported |
| P6 daily χ_con(H_und) stability | perm p (msg) 0.395 (kick-level 0.265); R₁(perm, msg) 0.04; lag-1 -0.56; 5 days, median 557 pairs/day | constant χ | supported (R₁ < 0.5) |
| P6 daily χ_con(H_men) stability | perm p (msg) 0.784 (kick-level 0.794); R₁(perm, msg) 0.00; lag-1 -0.17; 5 days, median 33 pairs/day | constant χ | supported (R₁ < 0.5) |

Daily gauge: `data/processed/H30-operator-susceptibility/G05/daily.parquet`; figure: `figures/daily_gauge.pdf`.

## Scorecard (period-specific axes)
- C: χ_act does not beat the day-swap / zero null at the period level.
- D: the bystander (N_by / H_und) response and the pre-window placebo are unfitted checks of the mapping (see rows P2, P11).
- F: estimator validated on synthetic swarms at this period's sampling class (card, Synthetic validation).

## Notes
- 2026-10-03: folder and prediction written before the run (card Amendment A1 applies).
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.

## Round 1b (improved data, 2026-10-04)
Fixed activity bins, leading-@ nudge target, kicks at the DQ1 receiving call, past-only kick adjustment with a day fixed effect, content also with gte-modernbert. Numbers in `data/processed/H30-operator-susceptibility/r1b/G05/results.json`; verdict rule unchanged.

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| χ_con(H_und) bge (gte) | 0.023 [0.019, 0.027] | 0.022 [0.019, 0.025] (0.025 [0.024, 0.026]) |
| χ_con(H_men) bge (gte) | 0.046 [0.035, 0.054] | 0.041 [0.029, 0.049] (0.050 [0.032, 0.068]) |
| χ_act(H_und) | -0.06 [-0.68, 0.21] | 0.02 [-0.11, 0.10] |

Round-1b prediction rows: P3 failed; P4 supported; P4 supported; P6 supported (R₁ < 0.5); P6 supported (R₁ < 0.5).
