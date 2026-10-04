# H44 × G40: Connect your worlds into a 3D universe (2026-05-04 → 05-08)

**Verdict:** mixed (re-acquisition up, writes down, no entropy/switching rise)
**Role:** replication
**Period:** regime III · 15 agents · one merged room · 5 non-holdout days · 15 agents with calls · 41,379 model calls. Units: one unit (NE42 merge).

## Why this period
Replication layer: the common reset event-study estimator, giving one comparable point per regime-III period (templated, labelled as such).

## Prediction
*Written 2026-10-04 06:40 UTC, before running on this period (templated from the card's P1–P6; replication layer).*
- Forced resets: Θ_c > 0 (CI; ≥ 0.01), ΔR ≥ +0.05, Ω between −0.25 and −0.60, switching σ and/or entropy H up, susceptibility to post-reset items RR > 1, coupling cut log DiD < 0, content-pull D > 0; voluntary resets the same sign; no-reset pseudo-erasures ≈ 0 on every contrast.
- *Counts against:* Θ_c ≤ 0 (pure restart overhead, R1); Ω ≥ 0; σ/H flat or down; RR ≤ 1 with entropy up (temperature pulse, R2).


## Result
*Run 2026-10-04 (`analysis/run_all.py` → `data/processed/H44-erasure-reacquisition-thrash/G40/results.json`; figure `figures/event_study.pdf`).* Events: 820 forced, 289 voluntary, 842 pseudo-erasures (pos 31), 842 (pos 21). Pipeline class (Θ_c / Ω rule): forced **thrash**, voluntary **thrash**, no reset (pos 31) **none**, no reset (pos 21) **none**.

| Statistic (95% agent-day cluster bootstrap CI) | forced | voluntary | no reset (pseudo, pos 31) |
| --- | --- | --- | --- |
| Θ_c re-acquisition rise, non-write calls, agent × previous-call conditioned (post 1–5 vs far −20…−11) | +0.070 [+0.045, +0.096] | +0.088 [+0.035, +0.132] | -0.002 [-0.019, +0.015] |
| Θ raw (same, unconditioned) | +0.097 [+0.067, +0.128] | +0.144 [+0.097, +0.184] | -0.020 [-0.042, +0.001] |
| ΔR re-acquisition share, all calls | +0.113 [+0.089, +0.139] | +0.203 [+0.153, +0.252] | -0.026 [-0.044, -0.006] |
| Ω write dip (post 1–10 vs far) | -25% [-32, -19] | -46% [-54, -38] | +15% [+9, +23] |
| work commits per call (post 1–10 vs far) | -32% [-43, -23] | -50% [-59, -39] | +16% [+8, +27] |
| Δσ switching rate (post 1–5 vs far) | +0.020 [-0.007, +0.045] | -0.008 [-0.056, +0.045] | +0.014 [-0.007, +0.035] |
| ΔH category entropy, nats (post 1–5 vs far) | +0.018 [-0.036, +0.075] | -0.031 [-0.095, +0.039] | -0.018 [-0.053, +0.011] |
| Δ real-failure share (post 1–5 vs far) | +0.016 [+0.007, +0.025] | +0.009 [-0.008, +0.030] | -0.000 [-0.006, +0.005] |
| Δ talk share (post 1–5 vs far) | -0.014 [-0.024, -0.004] | -0.032 [-0.046, -0.019] | +0.004 [-0.002, +0.010] |
| end of segment: Ω near (−10…−1) vs far | +8% [+5, +12] | +15% [+5, +25] | +6% [+2, +11] |

- **Relaxation** after a forced reset: re-acquisition R(k) spikes at the first call (single-exponential ℓ = 2.0 calls [0.6, 3.4], amplitude +0.222) and then decays with a tail ℓ = 4.7 calls [2.9, 9.2] (k ≥ 2); writes recover with ℓ_W = 3.6 calls [2.6, 5.0] (fits capped at 60 calls).
- **Jev v3 windows** (first 5 min after a forced reset vs ≥ 5 min, paired within 71 agent-days): entropy -0.035 [-0.083, +0.014]; research/browse -0.002 [-0.020, +0.015]; execute +0.049 [+0.017, +0.086]; self-maintenance -0.035 [-0.052, -0.019]; progress score +0.189 [+0.101, +0.280]; error rate -0.033 [-0.089, +0.016].
  - density-matched (vs the last 5 min before a forced reset, 70 agent-days): entropy -0.046 [-0.111, +0.027]; research/browse -0.005 [-0.030, +0.018]; execute +0.016 [-0.021, +0.053]; progress score +0.125 [+0.048, +0.200]. Five-minute windows (≈ 15 calls) do not resolve the 1–5-call re-acquisition burst.
- **Replies** (572 talk messages after forced resets vs 670 after the no-reset boundary): susceptibility to post-reset items RR = +0.984 [+0.803, +1.194]; coupling cut log DiD (pre-erased vs post, against pre vs post without a reset) = -0.394 [-1.237, +0.379]; P(has a reply parent) RR = +1.093 [+0.933, +1.269].
- **Content pull** (209 forced pairs vs 164 within pairs, 0.05-decade gap strata): D = (post − pre)_forced − (post − pre)_within = -0.034 [-0.111, +0.024] (bge), -0.030 [-0.119, +0.022] (gte); toward post-read -0.033 [-0.114, +0.047], toward pre-read +0.001 [-0.062, +0.080].
- **Loops:** 49 forced events start inside a loop; the loop command recurs in +1…+10 in 33% vs 86% without a reset (OR +0.08 [+0.03, +0.22]; normalized hash OR +0.17 [+0.06, +0.35]).
- **Output lost per forced erasure** (+1…+20 vs far): -0.58 write calls, -0.278 work commits; × 820 erasures = 5.1% of the period's write calls and 7.7% of its work commits.
- **Memory dose:** within-agent Spearman ρ(lines added / memory size, write dip) = +0.020 (p 0.57, n 808).


## Scorecard (period-specific axes)
- **C adequacy:** contrasts against the no-reset pseudo-erasure and the far-pre reference (pseudo class none).
- **D unfitted:** Θ_c, σ, entropy, replies and pull were not fitted; the write dip (Ω) is H15's statistic (replication).
- **E interventional:** forced resets are timed by the 41-record cap (quasi-random); voluntary resets are the agent's choice.
- **F identifiability:** synthetic recovery at this period's counts: see the card (G51/G38: 100%; G37-size: thrash 62%, no false thrash).

## Notes
- Exploratory, non-holdout. Event windows truncate at the next reset of any kind and at the day edge; a balanced +1…+20 subset is in `results.json` (`forced_balanced`).
- No agent text is stored or quoted; commands were classified in memory (see the card's scheme).
