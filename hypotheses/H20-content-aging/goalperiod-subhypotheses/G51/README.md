# H20 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-18)

**Verdict:** failed (stationary within power: μ = 0.5 aging rejected) (Amendment-2 null; pre-registered null: mixed)
**Verdict (1b):** failed (replication); native: mixed
**Role:** native (round 1b: newcomers' own clock; also carries the replication row; round 1 was exploratory)
**Period:** regime III · mode I/K · 32 agents with statements · 4 rooms with agent statements · 45 active days (1080 agent-days with ≥ 8 statements). Step changes inside (kept in one unit; tested as rejuvenation, exception (c)): 2026-07-09, 2026-08-05, 2026-08-25, 2026-09-03. Holdout tail 09-07 → 09-18 excluded; non-holdout days 07-06 → 09-04 (d = 1–45).

## Why this period
One of the four long goals named in HH101 (t_w reaches 45 active days). Primary aging test. Private, stable individual roles (HH102: glassy); 21 → 32 agents (joins at 07-09/10, 07-17, 07-24/29, 08-28/31, 09-01, 09-03/04); the longest window. Joiners test the agent's own clock vs the kickoff clock.

## Prediction
*Written 2026-10-03, before running on this period (card predictions with Amendment 1).* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.42 / 0.48 / 0.48 against μ = 0.5 aging, 0.86 against μ = 1 (a² = 0.15). 
- **P1:** K > 0 (kickoff transient).
- **P2:** A > 0 or A_c > 0 with parametric-bootstrap one-sided p < 0.025 (co-primary; t_w ≥ 2, lags ≤ ⌊(T − 1)/2⌋, weekend covariate). The original rule (A at p < 0.05) is reported too.
- **P3:** if P2 holds, the passing statistic stays > 0 with p < 0.10 after removing ĝ and the agent's own goal ĝ_i.
- **P4:** if P2 holds, μ̂'s 90% CI excludes 0 and A_late > 0 (LODO-CV model ranking reported, not decisive).
- **P5:** 0 < μ̂ ≤ 1 if aging is found. **P6:** A_m has the same sign as A.
- **Secondary:** β_wk < 0; the active-day clock beats the calendar clock (M1 CV); S3 robustness signs.
- **#51:** high plateau q; aging present (credence 0.5). A_c is the better-powered statistic here (many agents). Joiners: A_i on the own-join clock vs the kickoff clock, descriptive. Rejuvenation at 07-09 / 08-05 / 08-25 / 09-03, descriptive.
- **Verdict rule (card + Amendment 1):** supported if P2, P3, P4 hold and A > 0 in chat-only and in the median A_i; failed if neither A nor A_c is significant and either both lie below the 5th percentile of their μ = 0.5 alternative (fitted nuisance parameters) or the co-primary design power is ≥ 0.8; failed also if A < 0 with one-sided p < 0.05; mixed otherwise (labelled by cause).

## Result
A = +0.012 (p = 0.078), A_c = +0.009 (p = 0.146), A_g = +0.014 (p = 0.060), A_late = +0.111, K = +0.060; co-primary design power vs μ = 0.5: 1.00 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | +0.060 | < 0.002 | < 0.002 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.012 | 0.048 | 0.078 | > 0 (P2, co-primary) |
| A_c common removed | +0.009 | 0.124 | 0.146 | > 0 (P2, co-primary) |
| A_g field removed | +0.014 | 0.026 | 0.060 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.111 | < 0.002 | < 0.002 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | -0.020 | 0.764 | 0.743 | P7 input |
| A_m swarm mean | +0.046 | 0.124 | 0.150 | sign of A (P6) |
| A_m roster-stable | +0.003 | 0.469 | 0.461 | reported |
| β_wk weekend gap | +0.006 | 0.940 | 0.926 | < 0 (S1) |

Verdict under the pre-registered isotropic null: **mixed (underpowered: not significant, μ = 0.5 aging not rejected)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 9.4/25.2; see the card): **failed (stationary within power: μ = 0.5 aging rejected)**.
Model fits (t_w ≥ 2, all lags): LODO-CV error × 10³ — M0 2.07, M0b 1.95, MQ 1.91, M1 2.00, MT 2.02 (best: MQ; descriptive per Amendment 1). μ̂ = +0.22, 90% CI [+0.08, +0.39] (Amendment-2 null: [+0.07, +0.41]). M1: q = 0.50, c0 − q = 0.34, τ0 = 4.5 d. Clock (S2): M1 CV × 10³ calendar 2.10 vs active-day 2.00.
Rejuvenation (S5) at 2026-07-09, 2026-08-05, 2026-08-25, 2026-09-03: straddling-pair M1 residual +0.007 (M1-simulated null -0.000 ± 0.008; p_lower 0.806).
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.83, 0.86, 0.85, 0.83, 0.84, 0.84, 0.86, 0.83, 0.84, 0.73, 0.82, 0.83, 0.79, 0.86, 0.86, 0.83, 0.79, 0.83, 0.81, 0.81, 0.78, 0.80, 0.77, 0.76, 0.83, 0.83, 0.74, 0.87, 0.88, 0.82, 0.86, 0.87, 0.87, 0.82, 0.88, 0.84, 0.88, 0.88, 0.83, 0.84, 0.88, 0.90, 0.90, 0.90.
Per-agent slopes: n = 27, median A_i +0.020, share > 0 0.59, Wilcoxon p (greater) 0.140.
Robustness of A (S3): chat -0.001; n16 +0.008; n64 +0.001; rarefied +0.012; calendar clock +0.010; p under a two-timescale isotropic null 0.045.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.50, r = 0.33, τ = 8.9 d, mean S = 0.356): co-primary 1.00 (pre-registered null), 1.00 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.007 ± 0.002 (n = 1189).
Joiners (S4, n = 6): median A_i on the kickoff clock +0.045, on their own clock -0.010.

Data: `data/processed/H20-content-aging/G51/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G51.pdf](figures/aging_G51.pdf).

## Scorecard (period-specific axes)
C (beats the stationary null): 0 — A p = 0.078, A_c p = 0.146. D (unfitted signature: A_late, μ̂ > 0): 1. H (rivals R1 quench, R2 field, R3 common): 0. G: –.

## Notes
- 2026-10-03: aging of μ = 0.5 size is rejected; a weak late slowing remains (A_late +0.11, μ̂ 0.22 [0.07, 0.41]), carried by the intention stream (chat-only A ≈ 0). Joins and the #focus room cause no rejuvenation detectable at this resolution.

## Round 1b (improved data, 2026-10-04): replication
*Inputs: shared goal fields, gte-modernbert (DQ5), DQ5 dedupe (copies, restatements), style-residualized vectors. Data: `data/processed/H20-content-aging/G51/r1b/result_aniso_<config>.json`. Role of this row: replication.*

| Input | Statistics (Amendment-2 null) |
| --- | --- |
| round 1 (bge, H01-derived goal vectors) | see Result above |
| bge-small, shared goal fields | A +0.012 (p 0.078); A_c +0.009 (p 0.146); A_late +0.111; K +0.060; μ̂ +0.22 [+0.07, +0.41]; power 1.00 |
| gte-modernbert | A +0.007 (p 0.192); A_c +0.001 (p 0.477); A_late +0.093; K +0.053; μ̂ +0.16 [+0.00, +0.37]; power 1.00 |
| restatement-deduped (bge / gte) | A +0.009 / +0.003 |
| style-residualized (bge / gte) | A +0.009 / -0.001 |

A across the 7 configurations: -0.001 to +0.012. The shared goal fields give the same ĝ as round 1 (cos 1.0000 at n = 32: H20 averaged the room kickoffs, so H01's #38 room swap cancels), so bge numbers reproduce exactly.

## Round 1b native test: newcomers' own clock (onboarding transient)
*Prediction written 2026-10-04 07:25 UTC, before computing any own-clock K or placebo statistic. Seen before: the round-1 numbers above (including S4: median A_i +0.045 on the kickoff clock, −0.010 on the own clock, n = 6) and H48's native note that #51 newcomers start generic and individuate within a day (H54: each agent lands on its own private goal).*
- **Design.** Joiners = agents whose first valid agent-day (≥ 8 statements) is on d ≥ 3 of #51 and who have ≥ 6 valid days (expected: the three GPT-5.6 agents, Grok 4.5, Kimi K3, Claude Opus 5). Per joiner, the two-time matrix C_i on its own clock (k = 1 is its first valid day). **Onboarding transient** K_i = mean over τ = 1…3 of C_i(2, 2 + τ) − C_i(1, 1 + τ) (the same statistic as the card's K, on the agent's own clock). **Placebo:** for each incumbent (valid on d ≤ 2, ≥ 12 valid days), the same K computed from 20 random start days s ≥ 4 (a clock that starts nowhere special); the placebo distribution is the pooled incumbent values. Own-clock aging A_i (t_w ≥ 2) is reported again with both models.
- **N1a.** K_i > 0 in ≥ 4 of 6 joiners and the joiners' median K exceeds the placebo's 90th percentile. Credence 0.55.
- **N1b.** No own-clock aging: the joiners' median A_i is not > 0 at Wilcoxon p < 0.05 (both models). Credence 0.8.
- **Verdict rule (native):** "onboarding relaxation, no aging" (= consistent with round 1's "settle quickly, then stationary", **failed** for H20's aging claim) if N1a and N1b hold; **supported** (aging on the agent's own clock) if the joiners' median own-clock A_i > 0 with p < 0.05 in both models; **mixed** otherwise.

**Result (native, run 2026-10-04 after the prediction; `data/processed/H20-content-aging/r1b/natives_<model>.json`, `analysis/natives_r1b.py`).**

| Joiner (first valid day) | C(1, 2) own clock, bge / gte | C(2, 3), bge / gte | K_i, bge / gte | own-clock A_i, bge / gte |
| --- | --- | --- | --- | --- |
| GPT-5.6 Sol (07-09, isolated room) | 0.70 / 0.75 | 0.85 / 0.98 | +0.16 / +0.20 | −0.013 / −0.046 |
| GPT-5.6 Terra (07-09, isolated room) | 0.66 / 0.75 | – | – | −0.015 / −0.034 |
| GPT-5.6 Luna (07-09, isolated room) | 0.61 / 0.58 | 0.87 / 0.76 | +0.35 / +0.26 | −0.033 / +0.004 |
| Grok 4.5 (07-10, onboarding room) | 0.32 / 0.43 | 0.93 / 0.90 | +0.64 / +0.50 | +0.046 / +0.055 |
| Kimi K3 (07-17) | 0.68 / 0.75 | 0.71 / 0.62 | −0.23 / −0.24 | −0.007 / +0.047 |
| Claude Opus 5 (07-24) | 0.94 / 0.85 | 0.84 / 0.80 | −0.18 / −0.22 | +0.19 / +0.23 |

| Prediction | bge-small | gte-modernbert | Verdict |
| --- | --- | --- | --- |
| N1a K_i > 0 in ≥ 4 of 6 and median K > placebo q90 | 3 of 5 computable; median +0.16 vs placebo q90 +0.16 (median −0.01, n = 398) | 3 of 5; median +0.20 vs q90 +0.16 | ✗ / ✗ (count) |
| N1b no own-clock aging (median A_i not > 0 at p < 0.05) | median −0.010, Wilcoxon p 0.50 | +0.026, p 0.16 | ✓ / ✓ |

**Native verdict: mixed** (N1a fails on the count, N1b holds). Post hoc: the three clear onboarding transients (first-day content unlike the agent's later content, then a jump to its stationary level) belong to agents that started in isolated onboarding rooms (the GPT-5.6 trio, NE32; Grok 4.5); the two that joined straight into #general show none. No joiner ages on its own clock in either model.
