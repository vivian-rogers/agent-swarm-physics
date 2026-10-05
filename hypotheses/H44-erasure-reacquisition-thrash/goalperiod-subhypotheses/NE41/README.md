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

## Round 2 (2026-10-05)
*Spanning summary of round 2; predictions in the card (02:45 UTC) and amendments A3–A6 (03:01 UTC), both before real data. Pooled values are DerSimonian–Laird over the 9 periods (exception (c)); `data/processed/H44-erasure-reacquisition-thrash/r2/pooled.json`, `long_arm.json`.*

| Pooled statistic | Value |
| --- | --- |
| Θ_c on blind-checked labels (R1) | +0.106 [+0.089, +0.122], 9/9 > 0.01 |
| Θ_c, mid-segment label rates in both windows | +0.072 [+0.067, +0.078] |
| Y(20)/Y(40) · Y(30)/Y(40) | 0.88 [0.85, 0.91] · 0.95 [0.94, 0.96] |
| write slope β (per call) | +3.8 [+1.4, +6.2] ×10⁻⁴ (8/9 > 0; G51 n.s.) |
| write dip Ω vs far · near · whole · steady · cycle mean | -26% [-29, -23] · -31% [-35, -27] · -20% [-23, -18] · -32% [-35, -28] · -11% [-18, -4] |
| ΔV per reset (write calls, +1…+20) vs far · near · whole · steady · cycle mean | -0.38 [-0.54, -0.23] · -0.59 [-0.77, -0.42] · -0.19 [-0.25, -0.12] · -0.58 [-0.75, -0.41] · +0.07 [-0.04, +0.18] |
| re-open excess vs no reset · vs voluntary (file paths) | -0.039 [-0.085, +0.007] · +0.040 [+0.017, +0.062] |
| reset effect, looping · loop-free · difference (6 periods) | -0.086 [-0.151, -0.022] · -0.057 [-0.076, -0.038] · -0.027 [-0.076, +0.022] |

**Cap difference NE11/NE14 (regime I/II sessions, no 41-record cap; descriptive):**

| Period | sessions (> 40 calls) | W(41–60) − W(31–40) | writes in first 10 calls / calls 11–40 |
| --- | --- | --- | --- |
| G30 (I) | 1,041 (268) | +0.037 [+0.001, +0.066] | 0.49 |
| G31 (I) | 1,250 (318) | +0.043 [+0.013, +0.066] | 0.52 |
| G33 (II) | 706 (134) | +0.052 [+0.003, +0.112] | 0.50 |
| G35 (II) | 1,247 (420) | +0.147 [+0.092, +0.199] | 0.48 |

- Sessions longer than 40 calls end within about 50, so k 41–60 carries the end-of-session write burst; trimming the last 10 calls of each session leaves 1–23 calls. P-R2c is **inconclusive**. The restart dip itself (≈ 0.5 of later writes in the first 10 calls) appears in this different scaffold too.
