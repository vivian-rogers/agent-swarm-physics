# H44 × G42: Run your own YouTube channel (2026-05-18 → 05-22)

**Verdict:** mixed (re-acquisition up, writes down, no entropy/switching rise)
**Role:** replication
**Period:** regime III · 15 → 16 agents · two rooms · 5 non-holdout days · 16 agents with calls · 41,652 model calls. Units: units 42a, 42b (Gemini 3.5 Flash joins).

## Why this period
Replication layer: the common reset event-study estimator, giving one comparable point per regime-III period (templated, labelled as such).

## Prediction
*Written 2026-10-04 06:40 UTC, before running on this period (templated from the card's P1–P6; replication layer).*
- Forced resets: Θ_c > 0 (CI; ≥ 0.01), ΔR ≥ +0.05, Ω between −0.25 and −0.60, switching σ and/or entropy H up, susceptibility to post-reset items RR > 1, coupling cut log DiD < 0, content-pull D > 0; voluntary resets the same sign; no-reset pseudo-erasures ≈ 0 on every contrast.
- *Counts against:* Θ_c ≤ 0 (pure restart overhead, R1); Ω ≥ 0; σ/H flat or down; RR ≤ 1 with entropy up (temperature pulse, R2).


## Result
*Run 2026-10-04 (`analysis/run_all.py` → `data/processed/H44-erasure-reacquisition-thrash/G42/results.json`; figure `figures/event_study.pdf`).* Events: 776 forced, 443 voluntary, 775 pseudo-erasures (pos 31), 775 (pos 21). Pipeline class (Θ_c / Ω rule): forced **thrash**, voluntary **thrash**, no reset (pos 31) **none**, no reset (pos 21) **none**.

| Statistic (95% agent-day cluster bootstrap CI) | forced | voluntary | no reset (pseudo, pos 31) |
| --- | --- | --- | --- |
| Θ_c re-acquisition rise, non-write calls, agent × previous-call conditioned (post 1–5 vs far −20…−11) | +0.086 [+0.067, +0.108] | +0.049 [+0.017, +0.077] | -0.000 [-0.018, +0.017] |
| Θ raw (same, unconditioned) | +0.089 [+0.064, +0.113] | +0.137 [+0.084, +0.187] | -0.004 [-0.025, +0.018] |
| ΔR re-acquisition share, all calls | +0.092 [+0.068, +0.115] | +0.157 [+0.112, +0.195] | -0.010 [-0.029, +0.010] |
| Ω write dip (post 1–10 vs far) | -28% [-39, -15] | -26% [-42, -9] | +31% [+12, +62] |
| work commits per call (post 1–10 vs far) | -43% [-52, -33] | -39% [-61, -17] | +59% [+25, +106] |
| Δσ switching rate (post 1–5 vs far) | -0.020 [-0.048, +0.008] | -0.077 [-0.126, -0.022] | +0.021 [-0.012, +0.055] |
| ΔH category entropy, nats (post 1–5 vs far) | -0.045 [-0.114, +0.019] | -0.087 [-0.193, +0.031] | +0.010 [-0.043, +0.065] |
| Δ real-failure share (post 1–5 vs far) | +0.006 [-0.003, +0.015] | +0.016 [-0.001, +0.035] | -0.005 [-0.012, +0.003] |
| Δ talk share (post 1–5 vs far) | +0.002 [-0.005, +0.011] | +0.004 [-0.012, +0.027] | +0.002 [-0.003, +0.008] |
| end of segment: Ω near (−10…−1) vs far | +14% [+3, +28] | +47% [+32, +67] | +14% [+0, +33] |

- **Relaxation** after a forced reset: re-acquisition R(k) spikes at the first call (single-exponential ℓ = 0.3 calls [0.3, 0.8], amplitude +0.234) and then decays with a tail ℓ = 60.0 calls [0.3, 60.0] (k ≥ 2); writes recover with ℓ_W = 4.4 calls [1.2, 12.8] (fits capped at 60 calls).
- **Jev v3 windows** (first 5 min after a forced reset vs ≥ 5 min, paired within 72 agent-days): entropy +0.041 [-0.005, +0.086]; research/browse +0.008 [-0.012, +0.027]; execute -0.002 [-0.040, +0.036]; self-maintenance -0.009 [-0.023, +0.003]; progress score +0.054 [-0.023, +0.125]; error rate -0.016 [-0.064, +0.030].
  - density-matched (vs the last 5 min before a forced reset, 74 agent-days): entropy -0.059 [-0.118, -0.003]; research/browse -0.007 [-0.022, +0.007]; execute +0.036 [+0.003, +0.068]; progress score +0.072 [-0.003, +0.154]. Five-minute windows (≈ 15 calls) do not resolve the 1–5-call re-acquisition burst.
- **Replies** (332 talk messages after forced resets vs 339 after the no-reset boundary): susceptibility to post-reset items RR = +1.040 [+0.852, +1.300]; coupling cut log DiD (pre-erased vs post, against pre vs post without a reset) = +0.060 [-0.584, +0.765]; P(has a reply parent) RR = +1.142 [+0.984, +1.338].
- **Content pull** (72 forced pairs vs 92 within pairs, 0.05-decade gap strata): D = (post − pre)_forced − (post − pre)_within = +0.052 [-0.083, +0.158] (bge), +0.078 [-0.079, +0.155] (gte); toward post-read +0.107 [-0.042, +0.199], toward pre-read +0.056 [-0.041, +0.189].
- **Loops:** 18 forced events start inside a loop; the loop command recurs in +1…+10 in 6% vs 56% without a reset (OR +0.05 [+0.00, +0.14]; normalized hash OR +0.23 [+0.00, +1.88]).
- **Output lost per forced erasure** (+1…+20 vs far): -0.28 write calls, -0.176 work commits; × 776 erasures = 4.8% of the period's write calls and 8.5% of its work commits.
- **Memory dose:** within-agent Spearman ρ(lines added / memory size, write dip) = -0.017 (p 0.65, n 764).


## Scorecard (period-specific axes)
- **C adequacy:** contrasts against the no-reset pseudo-erasure and the far-pre reference (pseudo class none).
- **D unfitted:** Θ_c, σ, entropy, replies and pull were not fitted; the write dip (Ω) is H15's statistic (replication).
- **E interventional:** forced resets are timed by the 41-record cap (quasi-random); voluntary resets are the agent's choice.
- **F identifiability:** synthetic recovery at this period's counts: see the card (G51/G38: 100%; G37-size: thrash 62%, no false thrash).

## Notes
- Exploratory, non-holdout. Event windows truncate at the next reset of any kind and at the day edge; a balanced +1…+20 subset is in `results.json` (`forced_balanced`).
- No agent text is stored or quoted; commands were classified in memory (see the card's scheme).

## Round 2 (2026-10-05)
*Prediction: the card's "Round 2 design, predictions and kill rules" (written 2026-10-05 02:45 UTC, before any round-2 statistic) and amendments A3–A6 (03:01 UTC, after the synthetic validation, before real data). Role in round 2: replication. Run 2026-10-05 (`analysis/r2_run.py`, `analysis/r2_label.py` → `data/processed/H44-erasure-reacquisition-thrash/r2/G42/r2_results.json`); figure `figures/r2_sawtooth.pdf`. Period verdict above is unchanged (round-1 rule).*

| Statistic (95% agent-day cluster bootstrap CI) | Value |
| --- | --- |
| R1: Θ_c on blind-checked labels (round-1 classifier: +0.086) | +0.104 [+0.072, +0.144]; mid-segment rates +0.078 [+0.061, +0.098] |
| R2: complete forced sawtooths (40 calls) | 563 |
| R2: re-acquisition R(k): spike ℓ₁, tail ℓ₂ (calls; ℓ₂ capped at 12) | 0.3; 11.8 [2.0, 11.8]; ΔAIC two vs one timescale -2.1 |
| R2: write slope β (per call, after the slow relaxation) | +7.1 [-5.8, +19.4] ×10⁻⁴ |
| R2: output per call, cap 20 / cap 40 (Y(20)/Y(40)) | 0.84 [0.76, 0.91] |
| R2: P(L* = 40) per call · per minute; P(L* < 35) | 0.98 · 1.00; 0.01 |
| R2: write dip Ω (+1…+10) vs far · near · whole segment · steady state · cycle mean | -28% [-40, -15] · -37% [-49, -22] · -22% [-32, -11] · -41% [-50, -30] · -15% [-25, -1] |
| R2: in-loop share slope over k 11–40 (per call) | -2.0 [-6.4, +1.6] ×10⁻⁴ |
| R3: re-open share of post-reset read calls (file paths): forced · no reset · voluntary | 0.61 · 0.46 · 0.63 (998 forced read calls) |
| R3: recency-adjusted excess, forced vs no reset · vs voluntary | +0.123 [+0.065, +0.173] · +0.002 [-0.079, +0.105] |
| R3: re-opened object's recency rank (median; share within last 5 calls) | 1.0; 0.84 |
| R4 | not scored (18 looping forced events < 30) |

- **R2 reading:** shorter caps lose output here (Y(20)/Y(40) CI < 1); the dip is negative under all five references.
