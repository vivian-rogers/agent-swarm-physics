# H44 × G41: Novel research (2026-05-11 → 05-15)

**Verdict:** mixed (re-acquisition up, writes down, no entropy/switching rise)
**Role:** replication
**Period:** regime III · 15 agents · two rooms · 5 non-holdout days · 15 agents with calls · 35,025 model calls. Units: one unit (NE42 split back).

## Why this period
Replication layer: the common reset event-study estimator, giving one comparable point per regime-III period (templated, labelled as such).

## Prediction
*Written 2026-10-04 06:40 UTC, before running on this period (templated from the card's P1–P6; replication layer).*
- Forced resets: Θ_c > 0 (CI; ≥ 0.01), ΔR ≥ +0.05, Ω between −0.25 and −0.60, switching σ and/or entropy H up, susceptibility to post-reset items RR > 1, coupling cut log DiD < 0, content-pull D > 0; voluntary resets the same sign; no-reset pseudo-erasures ≈ 0 on every contrast.
- *Counts against:* Θ_c ≤ 0 (pure restart overhead, R1); Ω ≥ 0; σ/H flat or down; RR ≤ 1 with entropy up (temperature pulse, R2).


## Result
*Run 2026-10-04 (`analysis/run_all.py` → `data/processed/H44-erasure-reacquisition-thrash/G41/results.json`; figure `figures/event_study.pdf`).* Events: 666 forced, 349 voluntary, 671 pseudo-erasures (pos 31), 671 (pos 21). Pipeline class (Θ_c / Ω rule): forced **thrash**, voluntary **dip**, no reset (pos 31) **none**, no reset (pos 21) **none**.

| Statistic (95% agent-day cluster bootstrap CI) | forced | voluntary | no reset (pseudo, pos 31) |
| --- | --- | --- | --- |
| Θ_c re-acquisition rise, non-write calls, agent × previous-call conditioned (post 1–5 vs far −20…−11) | +0.102 [+0.077, +0.130] | +0.008 [-0.038, +0.051] | -0.027 [-0.046, -0.009] |
| Θ raw (same, unconditioned) | +0.132 [+0.092, +0.175] | +0.016 [-0.040, +0.069] | -0.052 [-0.083, -0.026] |
| ΔR re-acquisition share, all calls | +0.161 [+0.124, +0.208] | +0.084 [+0.034, +0.134] | -0.054 [-0.081, -0.032] |
| Ω write dip (post 1–10 vs far) | -37% [-45, -28] | -43% [-53, -32] | +18% [+9, +28] |
| work commits per call (post 1–10 vs far) | -48% [-58, -36] | -64% [-76, -49] | +30% [+17, +46] |
| Δσ switching rate (post 1–5 vs far) | +0.022 [-0.013, +0.056] | +0.035 [-0.014, +0.095] | +0.006 [-0.020, +0.029] |
| ΔH category entropy, nats (post 1–5 vs far) | -0.039 [-0.099, +0.018] | +0.083 [-0.002, +0.179] | +0.013 [-0.022, +0.045] |
| Δ real-failure share (post 1–5 vs far) | +0.010 [-0.002, +0.022] | +0.020 [-0.007, +0.050] | -0.002 [-0.010, +0.008] |
| Δ talk share (post 1–5 vs far) | -0.020 [-0.028, -0.011] | +0.004 [-0.015, +0.027] | +0.004 [-0.003, +0.011] |
| end of segment: Ω near (−10…−1) vs far | +6% [-1, +12] | +7% [-7, +26] | +11% [+2, +19] |

- **Relaxation** after a forced reset: re-acquisition R(k) spikes at the first call (single-exponential ℓ = 3.4 calls [1.6, 5.7], amplitude +0.237) and then decays with a tail ℓ = 7.0 calls [4.1, 22.1] (k ≥ 2); writes recover with ℓ_W = 3.8 calls [2.7, 5.4] (fits capped at 60 calls).
- **Jev v3 windows** (first 5 min after a forced reset vs ≥ 5 min, paired within 73 agent-days): entropy -0.056 [-0.122, +0.005]; research/browse +0.011 [-0.019, +0.039]; execute +0.049 [-0.001, +0.097]; self-maintenance -0.007 [-0.017, +0.003]; progress score +0.082 [-0.005, +0.160]; error rate +0.017 [-0.058, +0.105].
  - density-matched (vs the last 5 min before a forced reset, 73 agent-days): entropy -0.008 [-0.055, +0.043]; research/browse +0.006 [-0.034, +0.039]; execute -0.010 [-0.050, +0.031]; progress score +0.056 [-0.010, +0.128]. Five-minute windows (≈ 15 calls) do not resolve the 1–5-call re-acquisition burst.
- **Replies** (628 talk messages after forced resets vs 778 after the no-reset boundary): susceptibility to post-reset items RR = +1.033 [+0.895, +1.210]; coupling cut log DiD (pre-erased vs post, against pre vs post without a reset) = -1.189 [-1.912, -0.539]; P(has a reply parent) RR = +1.091 [+0.992, +1.200].
- **Content pull** (274 forced pairs vs 269 within pairs, 0.05-decade gap strata): D = (post − pre)_forced − (post − pre)_within = -0.094 [-0.162, +0.005] (bge), -0.090 [-0.184, +0.029] (gte); toward post-read -0.009 [-0.094, +0.077], toward pre-read +0.085 [-0.007, +0.144].
- **Loops:** 68 forced events start inside a loop; the loop command recurs in +1…+10 in 34% vs 72% without a reset (OR +0.20 [+0.07, +0.43]; normalized hash OR +0.15 [+0.06, +0.29]).
- **Output lost per forced erasure** (+1…+20 vs far): -0.89 write calls, -0.297 work commits; × 666 erasures = 8.7% of the period's write calls and 10.9% of its work commits.
- **Memory dose:** within-agent Spearman ρ(lines added / memory size, write dip) = -0.078 (p 0.047, n 650).


## Scorecard (period-specific axes)
- **C adequacy:** contrasts against the no-reset pseudo-erasure and the far-pre reference (pseudo class none).
- **D unfitted:** Θ_c, σ, entropy, replies and pull were not fitted; the write dip (Ω) is H15's statistic (replication).
- **E interventional:** forced resets are timed by the 41-record cap (quasi-random); voluntary resets are the agent's choice.
- **F identifiability:** synthetic recovery at this period's counts: see the card (G51/G38: 100%; G37-size: thrash 62%, no false thrash).

## Notes
- Exploratory, non-holdout. Event windows truncate at the next reset of any kind and at the day edge; a balanced +1…+20 subset is in `results.json` (`forced_balanced`).
- No agent text is stored or quoted; commands were classified in memory (see the card's scheme).

## Round 2 (2026-10-05)
*Prediction: the card's "Round 2 design, predictions and kill rules" (written 2026-10-05 02:45 UTC, before any round-2 statistic) and amendments A3–A6 (03:01 UTC, after the synthetic validation, before real data). Role in round 2: replication. Run 2026-10-05 (`analysis/r2_run.py`, `analysis/r2_label.py` → `data/processed/H44-erasure-reacquisition-thrash/r2/G41/r2_results.json`); figure `figures/r2_sawtooth.pdf`. Period verdict above is unchanged (round-1 rule).*

| Statistic (95% agent-day cluster bootstrap CI) | Value |
| --- | --- |
| R1: Θ_c on blind-checked labels (round-1 classifier: +0.102) | +0.154 [+0.088, +0.235]; mid-segment rates +0.093 [+0.074, +0.120] |
| R2: complete forced sawtooths (40 calls) | 441 |
| R2: re-acquisition R(k): spike ℓ₁, tail ℓ₂ (calls; ℓ₂ capped at 12) | 0.3; 11.8 [3.4, 11.8]; ΔAIC two vs one timescale +8.8 |
| R2: write slope β (per call, after the slow relaxation) | -2.6 [-19.9, +12.3] ×10⁻⁴ |
| R2: output per call, cap 20 / cap 40 (Y(20)/Y(40)) | 0.82 [0.78, 0.87] |
| R2: P(L* = 40) per call · per minute; P(L* < 35) | 1.00 · 1.00; 0.00 |
| R2: write dip Ω (+1…+10) vs far · near · whole segment · steady state · cycle mean | -37% [-45, -27] · -41% [-48, -32] · -29% [-36, -22] · -38% [-44, -31] · -25% [-34, -16] |
| R2: in-loop share slope over k 11–40 (per call) | +7.9 [-0.2, +16.5] ×10⁻⁴ |
| R3: re-open share of post-reset read calls (file paths): forced · no reset · voluntary | 0.63 · 0.75 · 0.63 (2,035 forced read calls) |
| R3: recency-adjusted excess, forced vs no reset · vs voluntary | -0.093 [-0.146, -0.034] · +0.061 [-0.028, +0.147] |
| R3: re-opened object's recency rank (median; share within last 5 calls) | 1.0; 0.85 |
| R4: reset effect on writes per call, looping · loop-free · difference (68 looping forced events) | -0.146 [-0.220, -0.081] · -0.094 [-0.133, -0.063] · -0.052 [-0.133, +0.010] |
| R4: relative (log-ratio) difference | +0.290 [+0.074, +0.529] |

- **R2 reading:** shorter caps lose output here (Y(20)/Y(40) CI < 1); the dip is negative under all five references.
