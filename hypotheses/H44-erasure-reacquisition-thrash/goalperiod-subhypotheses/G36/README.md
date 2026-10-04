# H44 × G36: Interact with outside agents (2026-03-23 → 03-27)

**Verdict:** mixed (replication mixed (re-acquisition up, writes down, no entropy/switching rise); native test failed)
**Role:** native
**Period:** regime III · 12 agents · two rooms · 4 non-holdout days · 12 agents with calls · 27,392 model calls. Units: units 36b (NE14 + NE41 onset, 03-24) and 36c (NE16 memory fix, 03-26); 36a is regime II and excluded.

## Why this period
Native layer. G36 holds the regime boundary inside one goal: NE14 (perma-computer-use and the consolidation cap) starts NE41's forced erasures on 03-24 (unit 36b), and NE16 fixes a contradictory "never update memory" consolidation instruction on 03-26 (unit 36c). These are the first forced erasures the agents ever met, and NE16 is a candidate change in the memory store (erasure with vs without memory writes).

## Prediction
*Written 2026-10-04 06:40 UTC, before running on this period (templated from the card's P1–P6; replication layer).*
- Forced resets: Θ_c > 0 (CI; ≥ 0.01), ΔR ≥ +0.05, Ω between −0.25 and −0.60, switching σ and/or entropy H up, susceptibility to post-reset items RR > 1, coupling cut log DiD < 0, content-pull D > 0; voluntary resets the same sign; no-reset pseudo-erasures ≈ 0 on every contrast.
- *Counts against:* Θ_c ≤ 0 (pure restart overhead, R1); Ω ≥ 0; σ/H flat or down; RR ≤ 1 with entropy up (temperature pulse, R2).
**Native prediction** *(written 2026-10-04 06:40 UTC)*: the thrash index on the first two days of forced erasure (03-24/25) is larger than the G38–G51 mean (agents had not yet adapted); NE16's memory fix (03-26) does not change Θ or Ω beyond noise (memory is not the load-bearing store). Across periods Θ declines and the notes-read share rises from #36 to #51.

## Result
*Run 2026-10-04 (`analysis/run_all.py` → `data/processed/H44-erasure-reacquisition-thrash/G36/results.json`; figure `figures/event_study.pdf`).* Events: 507 forced, 297 voluntary, 505 pseudo-erasures (pos 31), 505 (pos 21). Pipeline class (Θ_c / Ω rule): forced **thrash**, voluntary **dip**, no reset (pos 31) **none**, no reset (pos 21) **none**.

| Statistic (95% agent-day cluster bootstrap CI) | forced | voluntary | no reset (pseudo, pos 31) |
| --- | --- | --- | --- |
| Θ_c re-acquisition rise, non-write calls, agent × previous-call conditioned (post 1–5 vs far −20…−11) | +0.069 [+0.046, +0.096] | +0.043 [-0.002, +0.095] | +0.001 [-0.018, +0.020] |
| Θ raw (same, unconditioned) | +0.074 [+0.036, +0.114] | +0.088 [+0.019, +0.160] | -0.001 [-0.033, +0.028] |
| ΔR re-acquisition share, all calls | +0.088 [+0.051, +0.125] | +0.112 [+0.043, +0.181] | -0.001 [-0.030, +0.026] |
| Ω write dip (post 1–10 vs far) | -25% [-39, -10] | -43% [-56, -28] | +8% [-3, +24] |
| work commits per call (post 1–10 vs far) | -45% [-67, -13] | -67% [-85, +9] | +30% [-11, +89] |
| Δσ switching rate (post 1–5 vs far) | -0.017 [-0.059, +0.026] | -0.068 [-0.119, -0.006] | +0.034 [+0.002, +0.067] |
| ΔH category entropy, nats (post 1–5 vs far) | -0.065 [-0.137, +0.001] | -0.079 [-0.167, +0.006] | +0.031 [-0.015, +0.077] |
| Δ real-failure share (post 1–5 vs far) | +0.016 [+0.004, +0.031] | +0.001 [-0.022, +0.021] | -0.003 [-0.017, +0.009] |
| Δ talk share (post 1–5 vs far) | -0.011 [-0.021, -0.004] | -0.013 [-0.036, +0.007] | +0.012 [+0.004, +0.020] |
| end of segment: Ω near (−10…−1) vs far | -1% [-11, +12] | +47% [+22, +75] | +8% [-4, +23] |

- **Relaxation** after a forced reset: re-acquisition R(k) spikes at the first call (single-exponential ℓ = 1.4 calls [0.7, 8.6], amplitude +0.141) and then decays with a tail ℓ = 4.4 calls [0.3, 60.0] (k ≥ 2); writes recover with ℓ_W = 2.6 calls [1.3, 5.4] (fits capped at 60 calls).
- **Jev v3 windows** (first 5 min after a forced reset vs ≥ 5 min, paired within 44 agent-days): entropy -0.080 [-0.146, -0.015]; research/browse +0.017 [-0.030, +0.065]; execute +0.043 [+0.004, +0.082]; self-maintenance -0.015 [-0.027, -0.004]; progress score +0.216 [+0.128, +0.301]; error rate -0.037 [-0.102, +0.023].
  - density-matched (vs the last 5 min before a forced reset, 46 agent-days): entropy -0.052 [-0.108, +0.004]; research/browse -0.012 [-0.047, +0.024]; execute +0.044 [+0.003, +0.085]; progress score +0.132 [+0.049, +0.221]. Five-minute windows (≈ 15 calls) do not resolve the 1–5-call re-acquisition burst.
- **Replies** (305 talk messages after forced resets vs 411 after the no-reset boundary): susceptibility to post-reset items RR = +1.068 [+0.830, +1.382]; coupling cut log DiD (pre-erased vs post, against pre vs post without a reset) = -0.782 [-1.625, -0.111]; P(has a reply parent) RR = +1.130 [+0.949, +1.376].
- **Content pull** (75 forced pairs vs 81 within pairs, 0.05-decade gap strata): D = (post − pre)_forced − (post − pre)_within = +0.009 [-0.128, +0.111] (bge), -0.103 [-0.194, +0.056] (gte); toward post-read +0.062 [-0.063, +0.171], toward pre-read +0.053 [-0.030, +0.147].
- **Loops:** 32 forced events start inside a loop; the loop command recurs in +1…+10 in 3% vs 52% without a reset (OR +0.03 [+0.00, +0.18]; normalized hash OR +0.09 [+0.02, +0.25]).
- **Output lost per forced erasure** (+1…+20 vs far): -0.42 write calls, -0.080 work commits; × 507 erasures = 6.7% of the period's write calls and 10.4% of its work commits.
- **Memory dose:** within-agent Spearman ρ(lines added / memory size, write dip) = -0.023 (p 0.61, n 498).

## Native test
*Run 2026-10-04.*

| | forced events | Θ_c | Ω (write dip) | Δσ | memory lines added at the consolidation (median) |
| --- | --- | --- | --- | --- | --- |
| 36b (03-24/25, first erasures; before NE16) | 228 | +0.075 [+0.035, +0.123] | -16% [-43, +5] | -0.015 [-0.082, +0.056] | 57.5 |
| 36c (03-26/27, after NE16) | 279 | +0.068 [+0.035, +0.104] | -32% [-43, -15] | -0.018 [-0.076, +0.047] | 54.0 |
| G38–G51 replication mean Θ_c | | +0.080 | | | |

- **Onset:** the first two days' thrash index is not larger than the later-period mean (prediction failed). Agents re-acquire after their very first erasures about as much as months later.
- **NE16:** no first stage: memory lines added per consolidation are the same before and after the fix (median 57.5 vs 54.0), so NE16 did not change the memory store at consolidations and cannot test it. Θ_c is the same in both units; the write dip is larger after the fix but the difference is inside the CIs.
- **Learning across periods** (NE41 folder): Θ_c shows no decline from #36 to #51 and the notes-read share no significant rise.
- **Native verdict:** failed (onset not larger; no learning trend); NE16 uninformative.

## Scorecard (period-specific axes)
- **C adequacy:** contrasts against the no-reset pseudo-erasure and the far-pre reference (pseudo class none).
- **D unfitted:** Θ_c, σ, entropy, replies and pull were not fitted; the write dip (Ω) is H15's statistic (replication).
- **E interventional:** forced resets are timed by the 41-record cap (quasi-random); voluntary resets are the agent's choice.
- **F identifiability:** synthetic recovery at this period's counts: see the card (G51/G38: 100%; G37-size: thrash 62%, no false thrash).

## Notes
- Exploratory, non-holdout. Event windows truncate at the next reset of any kind and at the day edge; a balanced +1…+20 subset is in `results.json` (`forced_balanced`).
- No agent text is stored or quoted; commands were classified in memory (see the card's scheme).
