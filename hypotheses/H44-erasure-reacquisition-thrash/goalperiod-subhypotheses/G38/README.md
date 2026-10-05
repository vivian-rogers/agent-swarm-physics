# H44 × G38: Charity fundraiser, year 2 (2026-04-02 → 04-24)

**Verdict:** supported (replication supported (re-acquisition up, writes down, switching up); native test passed)
**Role:** native
**Period:** regime III · 12 → 14 agents · two rooms · 17 non-holdout days · 14 agents with calls · 114,075 model calls. Units: units 38a–38e (NE36, NE17, two joins, NE18).

## Why this period
Native layer. G38 is the longest two-room regime-III period with dense git and the first of the loop-heavy weeks (#38–#40: H12's self-repetition, H46's restatement). If the context window carries a stuck command loop, erasing it should break the loop; if the loop is driven by the task or the environment (a failing build, a polling job), the agent should return to it after re-reading.

## Prediction
*Written 2026-10-04 06:40 UTC, before running on this period (templated from the card's P1–P6; replication layer).*
- Forced resets: Θ_c > 0 (CI; ≥ 0.01), ΔR ≥ +0.05, Ω between −0.25 and −0.60, switching σ and/or entropy H up, susceptibility to post-reset items RR > 1, coupling cut log DiD < 0, content-pull D > 0; voluntary resets the same sign; no-reset pseudo-erasures ≈ 0 on every contrast.
- *Counts against:* Θ_c ≤ 0 (pure restart overhead, R1); Ω ≥ 0; σ/H flat or down; RR ≤ 1 with entropy up (temperature pulse, R2).
**Native prediction** *(written 2026-10-04 06:40 UTC)*: among events whose pre-window is in a loop (≥ 3 calls in loop in −10…−1), the loop recurs in +1…+10 less often after a forced erasure than after a pseudo-erasure with a loop in its pre-window (odds ratio < 0.7, CI < 1).

## Result
*Run 2026-10-04 (`analysis/run_all.py` → `data/processed/H44-erasure-reacquisition-thrash/G38/results.json`; figure `figures/event_study.pdf`).* Events: 2,333 forced, 843 voluntary, 2,330 pseudo-erasures (pos 31), 2,330 (pos 21). Pipeline class (Θ_c / Ω rule): forced **thrash**, voluntary **busy**, no reset (pos 31) **none**, no reset (pos 21) **none**.

| Statistic (95% agent-day cluster bootstrap CI) | forced | voluntary | no reset (pseudo, pos 31) |
| --- | --- | --- | --- |
| Θ_c re-acquisition rise, non-write calls, agent × previous-call conditioned (post 1–5 vs far −20…−11) | +0.068 [+0.056, +0.082] | +0.061 [+0.039, +0.077] | -0.013 [-0.021, -0.006] |
| Θ raw (same, unconditioned) | +0.081 [+0.066, +0.096] | +0.095 [+0.069, +0.121] | -0.018 [-0.029, -0.009] |
| ΔR re-acquisition share, all calls | +0.083 [+0.068, +0.099] | +0.107 [+0.083, +0.129] | -0.019 [-0.029, -0.010] |
| Ω write dip (post 1–10 vs far) | -24% [-32, -15] | -18% [-34, +1] | +13% [+4, +23] |
| work commits per call (post 1–10 vs far) | -29% [-46, -7] | -16% [-55, +33] | +31% [+9, +61] |
| Δσ switching rate (post 1–5 vs far) | +0.032 [+0.014, +0.054] | -0.000 [-0.030, +0.030] | -0.005 [-0.019, +0.010] |
| ΔH category entropy, nats (post 1–5 vs far) | -0.042 [-0.070, -0.010] | -0.028 [-0.077, +0.020] | +0.010 [-0.012, +0.033] |
| Δ real-failure share (post 1–5 vs far) | +0.013 [+0.008, +0.018] | +0.008 [-0.004, +0.020] | +0.001 [-0.003, +0.005] |
| Δ talk share (post 1–5 vs far) | -0.006 [-0.010, -0.002] | -0.011 [-0.019, -0.002] | +0.001 [-0.002, +0.005] |
| end of segment: Ω near (−10…−1) vs far | +4% [-3, +11] | +18% [-1, +43] | +8% [+1, +15] |

- **Relaxation** after a forced reset: re-acquisition R(k) spikes at the first call (single-exponential ℓ = 0.6 calls [0.3, 1.0], amplitude +0.217) and then decays with a tail ℓ = 5.7 calls [3.1, 12.9] (k ≥ 2); writes recover with ℓ_W = 3.6 calls [1.7, 6.6] (fits capped at 60 calls).
- **Jev v3 windows** (first 5 min after a forced reset vs ≥ 5 min, paired within 202 agent-days): entropy -0.026 [-0.053, +0.002]; research/browse +0.008 [-0.004, +0.020]; execute +0.033 [+0.008, +0.056]; self-maintenance -0.030 [-0.038, -0.023]; progress score +0.169 [+0.122, +0.215]; error rate -0.004 [-0.030, +0.022].
  - density-matched (vs the last 5 min before a forced reset, 204 agent-days): entropy -0.045 [-0.079, -0.011]; research/browse +0.003 [-0.006, +0.013]; execute +0.031 [+0.008, +0.054]; progress score +0.156 [+0.094, +0.213]. Five-minute windows (≈ 15 calls) do not resolve the 1–5-call re-acquisition burst.
- **Replies** (1562 talk messages after forced resets vs 1739 after the no-reset boundary): susceptibility to post-reset items RR = +0.963 [+0.871, +1.059]; coupling cut log DiD (pre-erased vs post, against pre vs post without a reset) = -0.037 [-0.361, +0.298]; P(has a reply parent) RR = +1.071 [+0.994, +1.149].
- **Content pull** (626 forced pairs vs 812 within pairs, 0.05-decade gap strata): D = (post − pre)_forced − (post − pre)_within = +0.001 [-0.068, +0.087] (bge), -0.011 [-0.078, +0.079] (gte); toward post-read +0.067 [+0.018, +0.113], toward pre-read +0.066 [-0.006, +0.125].
- **Loops:** 170 forced events start inside a loop; the loop command recurs in +1…+10 in 16% vs 72% without a reset (OR +0.08 [+0.04, +0.13]; normalized hash OR +0.07 [+0.03, +0.12]).
- **Output lost per forced erasure** (+1…+20 vs far): -0.27 write calls, -0.045 work commits; × 2333 erasures = 6.5% of the period's write calls and 7.6% of its work commits.
- **Memory dose:** within-agent Spearman ρ(lines added / memory size, write dip) = -0.035 (p 0.093, n 2297).

## Native test
*Run 2026-10-04.* A forced reset is "in a loop" when ≥ 3 of its last 10 calls repeat an earlier command (exact command hash ≥ 2 times in the previous 10 calls) or are the 3rd real failure within 10 calls. Outcome: the looping command recurs in +1…+10. Control: pseudo-erasures (pos 31) with a loop in their pre-window.

| | events in a loop | loop recurs in +1…+10 | odds ratio vs no reset |
| --- | --- | --- | --- |
| forced | 170 | 16% | +0.08 [+0.04, +0.13] |
| voluntary | 53 | 9% | +0.04 [+0.01, +0.08] |
| no reset (pos 31) | 169 | 72% | 1 |
| forced, normalized hash (cd/export prefixes dropped, digits collapsed) | 194 | 15% (control 72%) | +0.07 [+0.03, +0.12] |

- **Native verdict:** supported: an erasure breaks most command loops (prediction OR < 0.7, CI < 1), and the normalized hash rules out "same command re-typed with a new prefix". Across all periods the pooled odds ratio is in the NE41 folder; the effect weakens in G51 (OR ≈ 0.3).
- **Path → recovery (secondary, as in G51):** calls to first write vs screen-first: artifact -1.13 [-1.89, -0.41], remote -3.04 [-3.97, -1.92], room -1.30 [-2.08, -0.42], direct -4.06 [-5.13, -3.21].

## Scorecard (period-specific axes)
- **C adequacy:** contrasts against the no-reset pseudo-erasure and the far-pre reference (pseudo class none).
- **D unfitted:** Θ_c, σ, entropy, replies and pull were not fitted; the write dip (Ω) is H15's statistic (replication).
- **E interventional:** forced resets are timed by the 41-record cap (quasi-random); voluntary resets are the agent's choice.
- **F identifiability:** synthetic recovery at this period's counts: see the card (G51/G38: 100%; G37-size: thrash 62%, no false thrash).

## Notes
- Exploratory, non-holdout. Event windows truncate at the next reset of any kind and at the day edge; a balanced +1…+20 subset is in `results.json` (`forced_balanced`).
- No agent text is stored or quoted; commands were classified in memory (see the card's scheme).

## Round 2 (2026-10-05)
*Prediction: the card's "Round 2 design, predictions and kill rules" (written 2026-10-05 02:45 UTC, before any round-2 statistic) and amendments A3–A6 (03:01 UTC, after the synthetic validation, before real data). Role in round 2: native (R2 power, R3, R4 at scale). Run 2026-10-05 (`analysis/r2_run.py`, `analysis/r2_label.py` → `data/processed/H44-erasure-reacquisition-thrash/r2/G38/r2_results.json`); figure `figures/r2_sawtooth.pdf`. Period verdict above is unchanged (round-1 rule).*

| Statistic (95% agent-day cluster bootstrap CI) | Value |
| --- | --- |
| R1: Θ_c on blind-checked labels (round-1 classifier: +0.068) | +0.091 [+0.056, +0.131]; mid-segment rates +0.063 [+0.050, +0.076] |
| R2: complete forced sawtooths (40 calls) | 1,693 |
| R2: re-acquisition R(k): spike ℓ₁, tail ℓ₂ (calls; ℓ₂ capped at 12) | 0.3; 11.8 [2.0, 11.8]; ΔAIC two vs one timescale -2.6 |
| R2: write slope β (per call, after the slow relaxation) | +4.2 [-0.0, +8.5] ×10⁻⁴ |
| R2: output per call, cap 20 / cap 40 (Y(20)/Y(40)) | 0.93 [0.89, 0.97] |
| R2: P(L* = 40) per call · per minute; P(L* < 35) | 0.50 · 1.00; 0.00 |
| R2: write dip Ω (+1…+10) vs far · near · whole segment · steady state · cycle mean | -24% [-33, -15] · -27% [-37, -17] · -18% [-27, -11] · -27% [-35, -20] · +2% [-6, +11] |
| R2: in-loop share slope over k 11–40 (per call) | +4.3 [+0.9, +7.2] ×10⁻⁴ |
| R3: re-open share of post-reset read calls (file paths): forced · no reset · voluntary | 0.59 · 0.72 · 0.60 (2,735 forced read calls) |
| R3: recency-adjusted excess, forced vs no reset · vs voluntary | -0.119 [-0.174, -0.070] · +0.026 [-0.073, +0.135] |
| R3: re-opened object's recency rank (median; share within last 5 calls) | 2.0; 0.73 |
| R4: reset effect on writes per call, looping · loop-free · difference (170 looping forced events) | -0.020 [-0.084, +0.022] · -0.022 [-0.035, -0.009] · +0.002 [-0.061, +0.046] |
| R4: relative (log-ratio) difference | +0.195 [-0.204, +0.529] |

- **R2 reading:** shorter caps lose output here (Y(20)/Y(40) CI < 1); the cycle-mean reference includes 0, the pre-reset references do not.
- **G38 native (loops):** R4 has power 0.70 here. The reset effect on looping agents is −0.020 [−0.084, +0.022] writes per call (170 events), no better than for loop-free agents (difference +0.002). Post hoc, stuck loops (96 events) gain +0.024 [−0.017, +0.064], n.s. The cap curve is flat after call 5 (P(L* = 40) = 0.50), but Y(20)/Y(40) = 0.93 [0.89, 0.97] still favours the longer cap. R3: forced reads re-open the erased working set *less* than mid-segment reads (−0.12).
