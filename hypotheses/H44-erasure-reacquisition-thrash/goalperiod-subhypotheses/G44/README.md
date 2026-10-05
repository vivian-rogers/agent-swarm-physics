# H44 × G44: #best fine-tunes a leader; #rest picks its own goals (2026-05-26 → 05-29)

**Verdict:** supported (re-acquisition up, writes down, switching up)
**Role:** replication
**Period:** regime III · 17 → 18 agents · two rooms · 4 non-holdout days · 18 agents with calls · 26,175 model calls. Units: units 44a, 44b (two joins).

## Why this period
Replication layer: the common reset event-study estimator, giving one comparable point per regime-III period (templated, labelled as such).

## Prediction
*Written 2026-10-04 06:40 UTC, before running on this period (templated from the card's P1–P6; replication layer).*
- Forced resets: Θ_c > 0 (CI; ≥ 0.01), ΔR ≥ +0.05, Ω between −0.25 and −0.60, switching σ and/or entropy H up, susceptibility to post-reset items RR > 1, coupling cut log DiD < 0, content-pull D > 0; voluntary resets the same sign; no-reset pseudo-erasures ≈ 0 on every contrast.
- *Counts against:* Θ_c ≤ 0 (pure restart overhead, R1); Ω ≥ 0; σ/H flat or down; RR ≤ 1 with entropy up (temperature pulse, R2).


## Result
*Run 2026-10-04 (`analysis/run_all.py` → `data/processed/H44-erasure-reacquisition-thrash/G44/results.json`; figure `figures/event_study.pdf`).* Events: 366 forced, 394 voluntary, 470 pseudo-erasures (pos 31), 470 (pos 21). Pipeline class (Θ_c / Ω rule): forced **thrash**, voluntary **thrash**, no reset (pos 31) **none**, no reset (pos 21) **none**.

| Statistic (95% agent-day cluster bootstrap CI) | forced | voluntary | no reset (pseudo, pos 31) |
| --- | --- | --- | --- |
| Θ_c re-acquisition rise, non-write calls, agent × previous-call conditioned (post 1–5 vs far −20…−11) | +0.059 [+0.021, +0.105] | +0.055 [+0.026, +0.082] | -0.035 [-0.059, -0.014] |
| Θ raw (same, unconditioned) | +0.068 [+0.028, +0.119] | +0.056 [+0.022, +0.088] | -0.045 [-0.077, -0.016] |
| ΔR re-acquisition share, all calls | +0.084 [+0.046, +0.128] | +0.091 [+0.060, +0.120] | -0.045 [-0.071, -0.019] |
| Ω write dip (post 1–10 vs far) | -33% [-47, -16] | -44% [-55, -32] | +16% [+2, +33] |
| work commits per call (post 1–10 vs far) | -41% [-58, -21] | -56% [-70, -37] | +39% [+21, +62] |
| Δσ switching rate (post 1–5 vs far) | +0.061 [+0.010, +0.114] | -0.012 [-0.053, +0.035] | -0.016 [-0.049, +0.018] |
| ΔH category entropy, nats (post 1–5 vs far) | -0.050 [-0.119, +0.020] | -0.043 [-0.134, +0.044] | +0.021 [-0.031, +0.067] |
| Δ real-failure share (post 1–5 vs far) | +0.010 [-0.003, +0.024] | +0.021 [-0.001, +0.041] | -0.011 [-0.023, -0.000] |
| Δ talk share (post 1–5 vs far) | -0.009 [-0.024, +0.004] | -0.025 [-0.041, -0.008] | +0.008 [-0.004, +0.020] |
| end of segment: Ω near (−10…−1) vs far | +6% [-8, +23] | +19% [-0, +45] | +8% [-3, +21] |

- **Relaxation** after a forced reset: re-acquisition R(k) spikes at the first call (single-exponential ℓ = 1.8 calls [0.3, 5.4], amplitude +0.160) and then decays with a tail ℓ = 4.7 calls [1.4, 14.7] (k ≥ 2); writes recover with ℓ_W = 2.9 calls [2.1, 4.7] (fits capped at 60 calls).
- **Jev v3 windows** (first 5 min after a forced reset vs ≥ 5 min, paired within 59 agent-days): entropy -0.068 [-0.168, +0.016]; research/browse +0.018 [-0.011, +0.056]; execute +0.080 [+0.030, +0.132]; self-maintenance -0.043 [-0.062, -0.026]; progress score +0.111 [+0.016, +0.200]; error rate +0.053 [+0.007, +0.105].
  - density-matched (vs the last 5 min before a forced reset, 58 agent-days): entropy -0.051 [-0.159, +0.064]; research/browse +0.009 [-0.027, +0.046]; execute +0.054 [-0.024, +0.130]; progress score +0.049 [-0.101, +0.220]. Five-minute windows (≈ 15 calls) do not resolve the 1–5-call re-acquisition burst.
- **Replies** (332 talk messages after forced resets vs 465 after the no-reset boundary): susceptibility to post-reset items RR = +0.848 [+0.700, +1.034]; coupling cut log DiD (pre-erased vs post, against pre vs post without a reset) = -0.912 [-1.785, -0.243]; P(has a reply parent) RR = +0.993 [+0.901, +1.097].
- **Content pull** (88 forced pairs vs 115 within pairs, 0.05-decade gap strata): D = (post − pre)_forced − (post − pre)_within = +0.116 [-0.048, +0.222] (bge), +0.058 [-0.096, +0.204] (gte); toward post-read +0.111 [-0.071, +0.194], toward pre-read -0.005 [-0.124, +0.117].
- **Output lost per forced erasure** (+1…+20 vs far): -0.54 write calls, -0.332 work commits; × 366 erasures = 5.6% of the period's write calls and 8.2% of its work commits.
- **Memory dose:** within-agent Spearman ρ(lines added / memory size, write dip) = -0.051 (p 0.34, n 361).


## Scorecard (period-specific axes)
- **C adequacy:** contrasts against the no-reset pseudo-erasure and the far-pre reference (pseudo class none).
- **D unfitted:** Θ_c, σ, entropy, replies and pull were not fitted; the write dip (Ω) is H15's statistic (replication).
- **E interventional:** forced resets are timed by the 41-record cap (quasi-random); voluntary resets are the agent's choice.
- **F identifiability:** synthetic recovery at this period's counts: see the card (G51/G38: 100%; G37-size: thrash 62%, no false thrash).

## Notes
- Exploratory, non-holdout. Event windows truncate at the next reset of any kind and at the day edge; a balanced +1…+20 subset is in `results.json` (`forced_balanced`).
- No agent text is stored or quoted; commands were classified in memory (see the card's scheme).

## Round 2 (2026-10-05)
*Prediction: the card's "Round 2 design, predictions and kill rules" (written 2026-10-05 02:45 UTC, before any round-2 statistic) and amendments A3–A6 (03:01 UTC, after the synthetic validation, before real data). Role in round 2: replication. Run 2026-10-05 (`analysis/r2_run.py`, `analysis/r2_label.py` → `data/processed/H44-erasure-reacquisition-thrash/r2/G44/r2_results.json`); figure `figures/r2_sawtooth.pdf`. Period verdict above is unchanged (round-1 rule).*

| Statistic (95% agent-day cluster bootstrap CI) | Value |
| --- | --- |
| R1: Θ_c on blind-checked labels (round-1 classifier: +0.059) | +0.101 [+0.039, +0.174]; mid-segment rates +0.065 [+0.033, +0.104] |
| R2: complete forced sawtooths (40 calls) | 191 |
| R2: re-acquisition R(k): spike ℓ₁, tail ℓ₂ (calls; ℓ₂ capped at 12) | 0.6; 11.8 [2.0, 11.8]; ΔAIC two vs one timescale -3.9 |
| R2: write slope β (per call, after the slow relaxation) | +6.3 [-20.2, +26.9] ×10⁻⁴ |
| R2: output per call, cap 20 / cap 40 (Y(20)/Y(40)) | 0.84 [0.73, 0.94] |
| R2: P(L* = 40) per call · per minute; P(L* < 35) | 0.60 · 0.94; 0.07 |
| R2: write dip Ω (+1…+10) vs far · near · whole segment · steady state · cycle mean | -33% [-47, -19] · -37% [-51, -26] · -26% [-38, -16] · -34% [-47, -21] · -15% [-31, +6] |
| R2: in-loop share slope over k 11–40 (per call) | -3.6 [-13.1, +3.2] ×10⁻⁴ |
| R3: re-open share of post-reset read calls (file paths): forced · no reset · voluntary | 0.50 · 0.57 · 0.50 (573 forced read calls) |
| R3: recency-adjusted excess, forced vs no reset · vs voluntary | -0.042 [-0.131, +0.043] · +0.090 [+0.018, +0.160] |
| R3: re-opened object's recency rank (median; share within last 5 calls) | 3.0; 0.61 |
| R4 | not scored (13 looping forced events < 30) |

- **R2 reading:** shorter caps lose output here (Y(20)/Y(40) CI < 1); the cycle-mean reference includes 0, the pre-reset references do not.
