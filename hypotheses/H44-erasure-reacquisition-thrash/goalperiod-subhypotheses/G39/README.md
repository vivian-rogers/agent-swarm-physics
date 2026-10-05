# H44 × G39: Build your own interactive world (2026-04-27 → 05-01)

**Verdict:** mixed (re-acquisition up, writes down, no entropy/switching rise)
**Role:** replication
**Period:** regime III · 15 agents · two rooms · 5 non-holdout days · 15 agents with calls · 36,570 model calls. Units: one unit.

## Why this period
Replication layer: the common reset event-study estimator, giving one comparable point per regime-III period (templated, labelled as such).

## Prediction
*Written 2026-10-04 06:40 UTC, before running on this period (templated from the card's P1–P6; replication layer).*
- Forced resets: Θ_c > 0 (CI; ≥ 0.01), ΔR ≥ +0.05, Ω between −0.25 and −0.60, switching σ and/or entropy H up, susceptibility to post-reset items RR > 1, coupling cut log DiD < 0, content-pull D > 0; voluntary resets the same sign; no-reset pseudo-erasures ≈ 0 on every contrast.
- *Counts against:* Θ_c ≤ 0 (pure restart overhead, R1); Ω ≥ 0; σ/H flat or down; RR ≤ 1 with entropy up (temperature pulse, R2).


## Result
*Run 2026-10-04 (`analysis/run_all.py` → `data/processed/H44-erasure-reacquisition-thrash/G39/results.json`; figure `figures/event_study.pdf`).* Events: 736 forced, 252 voluntary, 744 pseudo-erasures (pos 31), 744 (pos 21). Pipeline class (Θ_c / Ω rule): forced **thrash**, voluntary **thrash**, no reset (pos 31) **none**, no reset (pos 21) **none**.

| Statistic (95% agent-day cluster bootstrap CI) | forced | voluntary | no reset (pseudo, pos 31) |
| --- | --- | --- | --- |
| Θ_c re-acquisition rise, non-write calls, agent × previous-call conditioned (post 1–5 vs far −20…−11) | +0.096 [+0.075, +0.121] | +0.128 [+0.074, +0.181] | -0.007 [-0.021, +0.008] |
| Θ raw (same, unconditioned) | +0.127 [+0.091, +0.161] | +0.155 [+0.094, +0.227] | -0.019 [-0.040, +0.001] |
| ΔR re-acquisition share, all calls | +0.127 [+0.098, +0.156] | +0.201 [+0.144, +0.260] | -0.028 [-0.045, -0.011] |
| Ω write dip (post 1–10 vs far) | -25% [-32, -19] | -30% [-38, -21] | +22% [+12, +35] |
| work commits per call (post 1–10 vs far) | -36% [-47, -27] | -50% [-61, -38] | +34% [+16, +71] |
| Δσ switching rate (post 1–5 vs far) | +0.002 [-0.031, +0.036] | -0.027 [-0.097, +0.052] | +0.012 [-0.016, +0.039] |
| ΔH category entropy, nats (post 1–5 vs far) | -0.021 [-0.092, +0.048] | -0.046 [-0.182, +0.098] | +0.048 [-0.001, +0.098] |
| Δ real-failure share (post 1–5 vs far) | -0.001 [-0.008, +0.006] | -0.005 [-0.026, +0.015] | -0.003 [-0.008, +0.003] |
| Δ talk share (post 1–5 vs far) | -0.003 [-0.010, +0.004] | -0.006 [-0.020, +0.007] | +0.003 [-0.003, +0.008] |
| end of segment: Ω near (−10…−1) vs far | +11% [+3, +19] | +2% [-6, +11] | +12% [+6, +22] |

- **Relaxation** after a forced reset: re-acquisition R(k) spikes at the first call (single-exponential ℓ = 0.9 calls [0.4, 2.2], amplitude +0.290) and then decays with a tail ℓ = 23.5 calls [4.7, 60.0] (k ≥ 2); writes recover with ℓ_W = 2.0 calls [1.0, 8.6] (fits capped at 60 calls).
- **Jev v3 windows** (first 5 min after a forced reset vs ≥ 5 min, paired within 69 agent-days): entropy -0.013 [-0.067, +0.042]; research/browse +0.039 [+0.018, +0.061]; execute +0.029 [-0.011, +0.064]; self-maintenance -0.013 [-0.024, -0.004]; progress score +0.094 [+0.009, +0.178]; error rate -0.059 [-0.144, +0.005].
  - density-matched (vs the last 5 min before a forced reset, 69 agent-days): entropy -0.016 [-0.066, +0.028]; research/browse +0.025 [+0.003, +0.049]; execute +0.007 [-0.031, +0.045]; progress score +0.107 [+0.017, +0.196]. Five-minute windows (≈ 15 calls) do not resolve the 1–5-call re-acquisition burst.
- **Replies** (262 talk messages after forced resets vs 344 after the no-reset boundary): susceptibility to post-reset items RR = +1.577 [+1.031, +2.833]; coupling cut log DiD (pre-erased vs post, against pre vs post without a reset) = -2.236 [-4.419, -0.662]; P(has a reply parent) RR = +1.193 [+0.854, +1.685].
- **Content pull** (64 forced pairs vs 84 within pairs, 0.05-decade gap strata): D = (post − pre)_forced − (post − pre)_within = -0.034 [-0.260, +0.082] (bge), +0.091 [-0.072, +0.205] (gte); toward post-read -0.049 [-0.148, +0.081], toward pre-read -0.014 [-0.063, +0.139].
- **Loops:** 44 forced events start inside a loop; the loop command recurs in +1…+10 in 20% vs 91% without a reset (OR +0.03 [+0.00, +0.07]; normalized hash OR +0.04 [+0.01, +0.11]).
- **Output lost per forced erasure** (+1…+20 vs far): -0.61 write calls, -0.235 work commits; × 736 erasures = 5.9% of the period's write calls and 7.8% of its work commits.
- **Memory dose:** within-agent Spearman ρ(lines added / memory size, write dip) = -0.062 (p 0.095, n 724).


## Scorecard (period-specific axes)
- **C adequacy:** contrasts against the no-reset pseudo-erasure and the far-pre reference (pseudo class none).
- **D unfitted:** Θ_c, σ, entropy, replies and pull were not fitted; the write dip (Ω) is H15's statistic (replication).
- **E interventional:** forced resets are timed by the 41-record cap (quasi-random); voluntary resets are the agent's choice.
- **F identifiability:** synthetic recovery at this period's counts: see the card (G51/G38: 100%; G37-size: thrash 62%, no false thrash).

## Notes
- Exploratory, non-holdout. Event windows truncate at the next reset of any kind and at the day edge; a balanced +1…+20 subset is in `results.json` (`forced_balanced`).
- No agent text is stored or quoted; commands were classified in memory (see the card's scheme).

## Round 2 (2026-10-05)
*Prediction: the card's "Round 2 design, predictions and kill rules" (written 2026-10-05 02:45 UTC, before any round-2 statistic) and amendments A3–A6 (03:01 UTC, after the synthetic validation, before real data). Role in round 2: replication. Run 2026-10-05 (`analysis/r2_run.py`, `analysis/r2_label.py` → `data/processed/H44-erasure-reacquisition-thrash/r2/G39/r2_results.json`); figure `figures/r2_sawtooth.pdf`. Period verdict above is unchanged (round-1 rule).*

| Statistic (95% agent-day cluster bootstrap CI) | Value |
| --- | --- |
| R1: Θ_c on blind-checked labels (round-1 classifier: +0.096) | +0.125 [+0.082, +0.182]; mid-segment rates +0.086 [+0.067, +0.113] |
| R2: complete forced sawtooths (40 calls) | 569 |
| R2: re-acquisition R(k): spike ℓ₁, tail ℓ₂ (calls; ℓ₂ capped at 12) | 0.3; 11.8 [4.8, 11.8]; ΔAIC two vs one timescale +12.1 |
| R2: write slope β (per call, after the slow relaxation) | +14.0 [+3.2, +25.0] ×10⁻⁴ |
| R2: output per call, cap 20 / cap 40 (Y(20)/Y(40)) | 0.85 [0.81, 0.88] |
| R2: P(L* = 40) per call · per minute; P(L* < 35) | 0.96 · 1.00; 0.00 |
| R2: write dip Ω (+1…+10) vs far · near · whole segment · steady state · cycle mean | -25% [-30, -18] · -32% [-39, -25] · -20% [-24, -14] · -28% [-36, -22] · -10% [-17, -0] |
| R2: in-loop share slope over k 11–40 (per call) | +2.2 [-0.6, +5.4] ×10⁻⁴ |
| R3: re-open share of post-reset read calls (file paths): forced · no reset · voluntary | 0.78 · 0.82 · 0.72 (1,487 forced read calls) |
| R3: recency-adjusted excess, forced vs no reset · vs voluntary | -0.032 [-0.070, +0.009] · +0.037 [-0.043, +0.123] |
| R3: re-opened object's recency rank (median; share within last 5 calls) | 1.0; 0.80 |
| R4: reset effect on writes per call, looping · loop-free · difference (44 looping forced events) | -0.182 [-0.235, -0.121] · -0.076 [-0.106, -0.045] · -0.106 [-0.163, -0.047] |
| R4: relative (log-ratio) difference | +0.127 [-0.358, +0.298] |

- **R2 reading:** shorter caps lose output here (Y(20)/Y(40) CI < 1); the dip is negative under all five references.
