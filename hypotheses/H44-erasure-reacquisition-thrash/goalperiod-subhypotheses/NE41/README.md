# H44 × NE41: forced context erasures at the 41-record cap (regime III, spanning)

**Verdict:** mixed (re-acquisition and output dip supported in 9/9 and 8/9 periods, forced ≥ voluntary, no excess pre-trend; temperature pulse, susceptibility rise and content-pull rise not found)
**Role:** native (exploratory; spans G36–G51, named exception (c): the reset is the object)
**Events:** regime-III non-holdout resets from DQ1 `context_ledger_turns` (21,165 forced, 16,357 voluntary) and 21,806 no-reset pseudo-erasures of each kind.

## Why this NE
The scaffold erases the context window when a segment reaches 41–42 records (40 model calls), keeping memory. Its timing is set by the cap, not by the agent, so each forced reset is a quasi-random scramble of the context store (H15's natural-scramble variant). Voluntary consolidations, chosen by the agent at task boundaries, are the contrast (rival R3).

## Prediction
*Written 2026-10-04 06:40 UTC, before any reset-aligned statistic (card P1–P6 and the NE41 native prediction).* Forced resets: Θ_c > 0 with ΔR ≥ +0.05; Ω −0.25…−0.60; switching/entropy up; susceptibility to post-reset items up (RR > 1); coupling to pre-reset items down (log DiD < 0); content pull toward post-read items up (D > 0); Θ_c(forced) ≥ 0.5 × Θ_c(voluntary); **no pre-trend in writes or re-acquisition beyond the pseudo-erasure band** (quasi-random timing), while voluntary resets show a pre-window write excess.

## Result
*Run 2026-10-04 (`analysis/run_all.py` → `data/processed/H44-erasure-reacquisition-thrash/NE41/results.json`; figure `figures/forest.pdf`).* DerSimonian–Laird random effects over the nine per-period estimates (never a pooled fit), 95% CI, number of periods with the predicted sign, between-period SD τ.

| Statistic | forced | voluntary | no reset (pos 31) |
| --- | --- | --- | --- |
| Θ_c (re-acquisition, non-write, agent × previous call) | +0.079 [+0.071, +0.086] (9/9 > 0; τ 0.006) | +0.057 [+0.041, +0.072] (9/9 > 0; τ 0.017) | -0.011 [-0.016, -0.006] (1/9 > 0; τ 0.004) |
| ΔR (all calls) | +0.101 [+0.087, +0.115] (9/9 > 0; τ 0.016) | +0.126 [+0.102, +0.151] (9/9 > 0; τ 0.031) | -0.021 [-0.029, -0.013] (0/9 > 0; τ 0.008) |
| Ω write dip (+1…+10) | -26% [-29, -23] (0/9 > 0) | -36% [-42, -30] (0/9 > 0) | +13% [+11, +15] (9/9 > 0) |
| work commits per call (+1…+10) | -38% [-41, -35] (0/9 > 0) | -50% [-55, -46] (0/9 > 0) | +29% [+22, +36] (9/9 > 0) |
| Δσ switching | +0.018 [+0.004, +0.031] (7/9 > 0; τ 0.014) | -0.010 [-0.031, +0.011] (2/9 > 0; τ 0.022) | +0.006 [+0.000, +0.011] (7/9 > 0; τ 0.002) |
| ΔH entropy (nats) | -0.027 [-0.050, -0.004] (2/9 > 0; τ 0.022) | -0.010 [-0.070, +0.051] (3/9 > 0; τ 0.081) | +0.013 [+0.004, +0.022] (8/9 > 0; τ 0.004) |
| pre-trend: writes −10…−1 vs −20…−11 | +7% [+4, +10] (8/9 > 0) | +18% [+6, +29] (8/9 > 0) | +7% [+5, +10] (8/9 > 0) |

| Susceptibility and coupling (pooled) | forced | voluntary |
| --- | --- | --- |
| reply rate per visible post-reset item, vs no reset (RR) | 0.97 [0.91, 1.04] (5/9 > 1) | 0.99 [0.90, 1.09] (4/9 > 1) |
| coupling cut: (pre-erased : post) ÷ (pre-in-context : post), ratio | 0.60 [0.44, 0.81] (1/9 > 1) | 0.62 [0.46, 0.83] (3/9 > 1) |
| P(talk message has a reply parent), RR | 1.07 [1.05, 1.10] (8/9 > 1) | 1.02 [0.96, 1.08] (7/9 > 1) |
| content pull D (bge) | -0.026 [-0.064, +0.012] (4/9 > 0; τ 0.036) | -0.028 [-0.065, +0.010] (3/8 > 0; τ 0.022) |
| content pull D (gte) | -0.028 [-0.072, +0.017] (3/9 > 0; τ 0.046) | – |
| loop recurrence, odds ratio vs no reset | 0.11 [0.05, 0.26] (0/7 > 1) | – |

- **Forced vs voluntary (R3):** Θ_c forced +0.079 ≥ 0.5 × voluntary +0.057: the erasure, not the task boundary, drives re-acquisition (P5 supported). Voluntary resets follow a wind-down (talk share rises to 0.17 at −1 in G51, reads fall, writes peak at −10…−2): the agent posts a status and consolidates at a boundary; the post-reset write dip is larger after voluntary resets (−36% vs −26%).
- **Quasi-random timing:** the forced pre-trend in writes (+7%) equals the no-reset pseudo band (+7%): writes ramp up through every segment, so a forced reset arrives at an ordinary point of that ramp (supported). The ramp itself means the post-reset dip is the low phase of a 40-call sawtooth, not a 10-call blip.
- **Past-only control (DQ8):** pseudo-erasures at pos 31 without conditioning on the segment reaching 40 calls give the same answer (G38/G41/G51 Θ_c −0.015 to −0.025, class none; `robustness_pseudo_past.json`).
- **Cross-period trend (phase-diagram points):** Θ_c by period G36 +0.069, G37 +0.061, G38 +0.068, G39 +0.096, G40 +0.070, G41 +0.102, G42 +0.086, G44 +0.059, G51 +0.081; Spearman vs period order ρ +0.23 (p 0.55); notes-read share ρ +0.58 (p 0.10). No learning trend.

## Scorecard (period-specific axes)
- **C:** beats the pseudo-erasure null in 9/9 periods (Θ_c) and 8/9 (Ω); past-only control agrees.
- **D:** Θ_c, σ, entropy, the reply contrasts and pull were not fitted; ℓ (5–7 calls for the re-acquisition tail, ~3 for writes) was predicted 3–15.
- **E:** forced resets are the intervention; forced ≥ voluntary rejects the task-boundary rival.
- **H:** rejects R0 (no effect) and R1 (pure restart overhead: Θ_c ≫ the synthetic dip residual); rejects R2 (temperature pulse: entropy falls); the predicted susceptibility rise also fails.

## Notes
- Exploratory, non-holdout; per-period numbers are in the G folders. The write dip (Ω) is H15's statistic (replication).
