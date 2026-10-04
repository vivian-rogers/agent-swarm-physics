# H44 × G51: Maximize your private assigned role (2026-07-06 → 09-04 (non-holdout))

**Verdict:** mixed (replication mixed (re-acquisition up, writes down, switching up, susceptibility opposite); native test passed)
**Role:** native
**Period:** regime III · 21 → 32 agents · one room (#general; #focus from 08-05) · 45 non-holdout days · 32 agents with calls · 900,117 model calls. Units: units 51a–51l (11 joins, NE32, NE38, NE43 bookends/nudges end); the tail 51m is held out.

## Why this period
Native layer. The largest sample by far (14,593 forced resets in 45 non-holdout days; 48k agent work commits), one room, private roles, so the re-acquisition path an agent takes after a reset can be compared within agent and task mode, and the DQ4 work commits measure output directly. Three period-specific tests: which re-acquisition path restores output fastest (the Kolchinsky store question), whether the memory dose written at the consolidation shortens the dip, and whether git work commits dip like write calls.

## Prediction
*Written 2026-10-04 06:40 UTC, before running on this period (templated from the card's P1–P6; replication layer).*
- Forced resets: Θ_c > 0 (CI; ≥ 0.01), ΔR ≥ +0.05, Ω between −0.25 and −0.60, switching σ and/or entropy H up, susceptibility to post-reset items RR > 1, coupling cut log DiD < 0, content-pull D > 0; voluntary resets the same sign; no-reset pseudo-erasures ≈ 0 on every contrast.
- *Counts against:* Θ_c ≤ 0 (pure restart overhead, R1); Ω ≥ 0; σ/H flat or down; RR ≤ 1 with entropy up (temperature pulse, R2).
**Native prediction** *(written 2026-10-04 06:40 UTC, card "Native predictions")*: among forced erasures, a first re-acquisition call on local artifacts or notes is followed by an earlier first write (within agent) than a first call that looks at the screen, browses or reads the room; memory dose does not shorten the dip (|ρ| < 0.1); work commits dip like write calls (relative dip within ±0.2 of Ω).

## Result
*Run 2026-10-04 (`analysis/run_all.py` → `data/processed/H44-erasure-reacquisition-thrash/G51/results.json`; figure `figures/event_study.pdf`).* Events: 14,593 forced, 13,306 voluntary, 15,100 pseudo-erasures (pos 31), 15,100 (pos 21). Pipeline class (Θ_c / Ω rule): forced **thrash**, voluntary **thrash**, no reset (pos 31) **none**, no reset (pos 21) **none**.

| Statistic (95% agent-day cluster bootstrap CI) | forced | voluntary | no reset (pseudo, pos 31) |
| --- | --- | --- | --- |
| Θ_c re-acquisition rise, non-write calls, agent × previous-call conditioned (post 1–5 vs far −20…−11) | +0.081 [+0.073, +0.088] | +0.042 [+0.033, +0.049] | -0.012 [-0.016, -0.008] |
| Θ raw (same, unconditioned) | +0.101 [+0.093, +0.109] | +0.064 [+0.053, +0.074] | -0.017 [-0.022, -0.011] |
| ΔR re-acquisition share, all calls | +0.107 [+0.099, +0.114] | +0.095 [+0.084, +0.105] | -0.019 [-0.024, -0.014] |
| Ω write dip (post 1–10 vs far) | -24% [-27, -21] | -33% [-36, -31] | +12% [+10, +15] |
| work commits per call (post 1–10 vs far) | -38% [-42, -34] | -49% [-52, -44] | +31% [+26, +36] |
| Δσ switching rate (post 1–5 vs far) | +0.028 [+0.019, +0.036] | -0.002 [-0.012, +0.009] | +0.005 [-0.001, +0.011] |
| ΔH category entropy, nats (post 1–5 vs far) | +0.003 [-0.012, +0.016] | +0.096 [+0.078, +0.114] | +0.014 [+0.004, +0.021] |
| Δ real-failure share (post 1–5 vs far) | +0.017 [+0.014, +0.021] | +0.017 [+0.013, +0.022] | -0.004 [-0.006, -0.003] |
| Δ talk share (post 1–5 vs far) | +0.000 [-0.002, +0.003] | -0.002 [-0.007, +0.003] | +0.003 [+0.002, +0.005] |
| end of segment: Ω near (−10…−1) vs far | +4% [+3, +6] | -1% [-4, +2] | +7% [+5, +9] |

- **Relaxation** after a forced reset: re-acquisition R(k) spikes at the first call (single-exponential ℓ = 1.5 calls [1.2, 2.0], amplitude +0.211) and then decays with a tail ℓ = 7.0 calls [5.4, 9.2] (k ≥ 2); writes recover with ℓ_W = 3.1 calls [2.7, 3.8] (fits capped at 60 calls).
- **Jev v3 windows** (first 5 min after a forced reset vs ≥ 5 min, paired within 924 agent-days): entropy -0.014 [-0.031, +0.003]; research/browse +0.017 [+0.009, +0.025]; execute +0.035 [+0.023, +0.047]; self-maintenance -0.017 [-0.021, -0.013]; progress score +0.148 [+0.122, +0.174]; error rate -0.007 [-0.022, +0.008].
  - density-matched (vs the last 5 min before a forced reset, 885 agent-days): entropy -0.027 [-0.044, -0.010]; research/browse +0.005 [-0.003, +0.013]; execute +0.020 [+0.008, +0.033]; progress score +0.099 [+0.072, +0.125]. Five-minute windows (≈ 15 calls) do not resolve the 1–5-call re-acquisition burst.
- **Replies** (8485 talk messages after forced resets vs 10184 after the no-reset boundary): susceptibility to post-reset items RR = +0.903 [+0.854, +0.954]; coupling cut log DiD (pre-erased vs post, against pre vs post without a reset) = -0.257 [-0.411, -0.090]; P(has a reply parent) RR = +1.079 [+1.049, +1.112].
- **Content pull** (4446 forced pairs vs 7208 within pairs, 0.05-decade gap strata): D = (post − pre)_forced − (post − pre)_within = -0.027 [-0.047, -0.007] (bge), -0.023 [-0.042, -0.003] (gte); toward post-read -0.013 [-0.031, +0.007], toward pre-read +0.014 [-0.003, +0.030].
- **Loops:** 741 forced events start inside a loop; the loop command recurs in +1…+10 in 51% vs 75% without a reset (OR +0.34 [+0.23, +0.43]; normalized hash OR +0.24 [+0.17, +0.32]).
- **Output lost per forced erasure** (+1…+20 vs far): -0.37 write calls, -0.159 work commits; × 14593 erasures = 3.7% of the period's write calls and 4.8% of its work commits.
- **Memory dose:** within-agent Spearman ρ(lines added / memory size, write dip) = -0.033 (p 6.4e-05, n 14457).

## Native test
*Run 2026-10-04.* **Path → recovery** (forced resets with ≥ 20 pre and ≥ 10 post calls, n = 14,051). The first substantive call in +1…+3 defines the path: artifact = local file or notes read, remote = web/API/git-remote read, screen = screenshot or GUI, room = history search or talk, direct = write or run. Shares: screen 51%, artifact 19%, direct 17%, remote 7%, room 5%, none 1%. Outcome: write rate in +4…+10 minus the pre-reset rate (−20…−1), and calls to the first write; strata agent × pre-reset mode (shell / GUI / mixed); differences against the screen path, agent-day cluster bootstrap:

| First path | n | Δ write rate vs screen | Δ calls to first write vs screen |
| --- | --- | --- | --- |
| artifact | 2,694 | +0.085 [+0.070, +0.101] | -2.56 [-2.78, -2.28] |
| remote | 1,016 | +0.044 [+0.020, +0.065] | -1.44 [-1.82, -1.04] |
| room | 657 | +0.034 [+0.016, +0.048] | -0.53 [-0.79, -0.26] |
| direct | 2,405 | +0.062 [+0.040, +0.083] | -3.79 [-4.25, -3.40] |
| none | 159 | -0.021 [-0.070, +0.024] | +0.47 [+0.07, +0.87] |

- **Memory dose:** within-agent ρ(lines added at the consolidation / memory size, write dip) = -0.033 (n 14,457): |ρ| < 0.1, as predicted.
- **Work commits:** relative dip over +1…+10 -38% [-42, -34] vs write calls -24% [-27, -21] (difference 0.14; predicted ≤ 0.2).
- **Output lost to the cap:** 0.37 write calls and 0.159 work commits per forced reset, 3.7% of G51's write calls and 4.8% of its work commits.
- **Native verdict:** path prediction supported (artifact-first resumes writing 2.6 calls sooner than screen-first, room-first only 0.5); dose prediction supported; work-commit prediction supported. Caveat: the path is chosen by the agent, so this is observational within strata, not an intervention.

## Scorecard (period-specific axes)
- **C adequacy:** contrasts against the no-reset pseudo-erasure and the far-pre reference (pseudo class none).
- **D unfitted:** Θ_c, σ, entropy, replies and pull were not fitted; the write dip (Ω) is H15's statistic (replication).
- **E interventional:** forced resets are timed by the 41-record cap (quasi-random); voluntary resets are the agent's choice.
- **F identifiability:** synthetic recovery at this period's counts: see the card (G51/G38: 100%; G37-size: thrash 62%, no false thrash).

## Notes
- Exploratory, non-holdout. Event windows truncate at the next reset of any kind and at the day edge; a balanced +1…+20 subset is in `results.json` (`forced_balanced`).
- No agent text is stored or quoted; commands were classified in memory (see the card's scheme).
