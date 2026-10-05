# H44 × G37: Free three days (2026-03-30 → 04-01)

**Verdict:** mixed (re-acquisition up, write dip not significant, no entropy/switching rise)
**Role:** replication
**Period:** regime III · 12 agents · two free rooms · 3 non-holdout days · 12 agents with calls · 19,268 model calls. Units: one unit.

## Why this period
Replication layer: the common reset event-study estimator, giving one comparable point per regime-III period (templated, labelled as such).

## Prediction
*Written 2026-10-04 06:40 UTC, before running on this period (templated from the card's P1–P6; replication layer).*
- Forced resets: Θ_c > 0 (CI; ≥ 0.01), ΔR ≥ +0.05, Ω between −0.25 and −0.60, switching σ and/or entropy H up, susceptibility to post-reset items RR > 1, coupling cut log DiD < 0, content-pull D > 0; voluntary resets the same sign; no-reset pseudo-erasures ≈ 0 on every contrast.
- *Counts against:* Θ_c ≤ 0 (pure restart overhead, R1); Ω ≥ 0; σ/H flat or down; RR ≤ 1 with entropy up (temperature pulse, R2).


## Result
*Run 2026-10-04 (`analysis/run_all.py` → `data/processed/H44-erasure-reacquisition-thrash/G37/results.json`; figure `figures/event_study.pdf`).* Events: 368 forced, 184 voluntary, 369 pseudo-erasures (pos 31), 369 (pos 21). Pipeline class (Θ_c / Ω rule): forced **busy**, voluntary **busy**, no reset (pos 31) **none**, no reset (pos 21) **none**.

| Statistic (95% agent-day cluster bootstrap CI) | forced | voluntary | no reset (pseudo, pos 31) |
| --- | --- | --- | --- |
| Θ_c re-acquisition rise, non-write calls, agent × previous-call conditioned (post 1–5 vs far −20…−11) | +0.061 [+0.027, +0.098] | +0.078 [+0.030, +0.111] | -0.013 [-0.031, +0.004] |
| Θ raw (same, unconditioned) | +0.062 [+0.021, +0.106] | +0.129 [+0.072, +0.181] | -0.000 [-0.025, +0.021] |
| ΔR re-acquisition share, all calls | +0.061 [+0.024, +0.102] | +0.131 [+0.077, +0.177] | -0.000 [-0.023, +0.019] |
| Ω write dip (post 1–10 vs far) | -5% [-36, +35] | -3% [-41, +51] | +11% [-10, +35] |
| work commits per call (post 1–10 vs far) | -18% [-52, +32] | -33% [-71, +14] | +32% [-11, +96] |
| Δσ switching rate (post 1–5 vs far) | +0.036 [-0.016, +0.087] | +0.070 [-0.005, +0.138] | +0.014 [-0.017, +0.043] |
| ΔH category entropy, nats (post 1–5 vs far) | -0.078 [-0.174, +0.028] | +0.009 [-0.104, +0.105] | +0.067 [-0.003, +0.138] |
| Δ real-failure share (post 1–5 vs far) | +0.006 [-0.003, +0.016] | -0.000 [-0.024, +0.024] | -0.004 [-0.016, +0.007] |
| Δ talk share (post 1–5 vs far) | +0.005 [-0.006, +0.016] | -0.009 [-0.030, +0.006] | +0.011 [+0.001, +0.020] |
| end of segment: Ω near (−10…−1) vs far | +36% [+15, +61] | +102% [+37, +226] | -16% [-31, +4] |

- **Relaxation** after a forced reset: re-acquisition R(k) spikes at the first call (single-exponential ℓ = 0.3 calls [0.3, 9.2], amplitude +0.198) and then decays with a tail ℓ = 9.2 calls [0.3, 60.0] (k ≥ 2); writes recover with ℓ_W = 60.0 calls [0.5, 60.0] (fits capped at 60 calls).
- **Jev v3 windows** (first 5 min after a forced reset vs ≥ 5 min, paired within 33 agent-days): entropy +0.046 [-0.023, +0.108]; research/browse -0.005 [-0.076, +0.063]; execute +0.018 [-0.041, +0.081]; self-maintenance -0.019 [-0.053, +0.017]; progress score +0.122 [+0.009, +0.242]; error rate +0.013 [-0.043, +0.085].
  - density-matched (vs the last 5 min before a forced reset, 34 agent-days): entropy -0.018 [-0.086, +0.054]; research/browse +0.016 [-0.017, +0.049]; execute -0.026 [-0.076, +0.026]; progress score +0.015 [-0.102, +0.118]. Five-minute windows (≈ 15 calls) do not resolve the 1–5-call re-acquisition burst.
- **Replies** (203 talk messages after forced resets vs 217 after the no-reset boundary): susceptibility to post-reset items RR = +1.105 [+0.903, +1.409]; coupling cut log DiD (pre-erased vs post, against pre vs post without a reset) = -1.050 [-1.897, -0.065]; P(has a reply parent) RR = +1.028 [+0.921, +1.137].
- **Content pull** (35 forced pairs vs 40 within pairs, 0.05-decade gap strata): D = (post − pre)_forced − (post − pre)_within = -0.181 [-0.287, -0.036] (bge), -0.240 [-0.364, -0.071] (gte); toward post-read -0.145 [-0.275, -0.052], toward pre-read +0.036 [-0.103, +0.114].
- **Output lost per forced erasure** (+1…+20 vs far): +0.10 write calls, +0.000 work commits; × 368 erasures = -3.7% of the period's write calls and -0.0% of its work commits.
- **Memory dose:** within-agent Spearman ρ(lines added / memory size, write dip) = -0.006 (p 0.91, n 362).


## Scorecard (period-specific axes)
- **C adequacy:** contrasts against the no-reset pseudo-erasure and the far-pre reference (pseudo class none).
- **D unfitted:** Θ_c, σ, entropy, replies and pull were not fitted; the write dip (Ω) is H15's statistic (replication).
- **E interventional:** forced resets are timed by the 41-record cap (quasi-random); voluntary resets are the agent's choice.
- **F identifiability:** synthetic recovery at this period's counts: see the card (G51/G38: 100%; G37-size: thrash 62%, no false thrash).

## Notes
- Exploratory, non-holdout. Event windows truncate at the next reset of any kind and at the day edge; a balanced +1…+20 subset is in `results.json` (`forced_balanced`).
- No agent text is stored or quoted; commands were classified in memory (see the card's scheme).

## Round 2 (2026-10-05)
*Prediction: the card's "Round 2 design, predictions and kill rules" (written 2026-10-05 02:45 UTC, before any round-2 statistic) and amendments A3–A6 (03:01 UTC, after the synthetic validation, before real data). Role in round 2: replication. Run 2026-10-05 (`analysis/r2_run.py`, `analysis/r2_label.py` → `data/processed/H44-erasure-reacquisition-thrash/r2/G37/r2_results.json`); figure `figures/r2_sawtooth.pdf`. Period verdict above is unchanged (round-1 rule).*

| Statistic (95% agent-day cluster bootstrap CI) | Value |
| --- | --- |
| R1: Θ_c on blind-checked labels (round-1 classifier: +0.061) | +0.091 [+0.046, +0.142]; mid-segment rates +0.060 [+0.023, +0.097] |
| R2: complete forced sawtooths (40 calls) | 241 |
| R2: re-acquisition R(k): spike ℓ₁, tail ℓ₂ (calls; ℓ₂ capped at 12) | 0.3; 8.2 [2.0, 11.8]; ΔAIC two vs one timescale -3.8 |
| R2: write slope β (per call, after the slow relaxation) | +2.4 [-6.0, +15.2] ×10⁻⁴ |
| R2: output per call, cap 20 / cap 40 (Y(20)/Y(40)) | 1.02 [0.87, 1.21] |
| R2: P(L* = 40) per call · per minute; P(L* < 35) | 0.23 · 0.83; 0.74 |
| R2: write dip Ω (+1…+10) vs far · near · whole segment · steady state · cycle mean | -5% [-33, +38] · -30% [-51, -1] · -17% [-39, +7] · -37% [-54, -14] · +13% [-16, +64] |
| R2: in-loop share slope over k 11–40 (per call) | -1.4 [-6.0, +3.5] ×10⁻⁴ |
| R3: re-open share of post-reset read calls (file paths): forced · no reset · voluntary | 0.41 · 0.53 · 0.45 (674 forced read calls) |
| R3: recency-adjusted excess, forced vs no reset · vs voluntary | -0.114 [-0.290, +0.044] · -0.020 [-0.184, +0.161] |
| R3: re-opened object's recency rank (median; share within last 5 calls) | 3.5; 0.60 |
| R4 | not scored (10 looping forced events < 30) |

- **R2 reading:** Y(20)/Y(40) CI includes 1 (low write share; no cap preference resolved); some references include 0.
