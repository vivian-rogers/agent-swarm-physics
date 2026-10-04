# H99 × G51: kick kernels against the fluctuation clock (#51 head, 2026-07-06 → 09-04)

**Verdict:** failed
**Role:** native (exploratory)
**Period:** goal #51 · regime III · units 51a–51l (51b has an empty all-present window), N 21 → 32 · the tail (09-07 → 09-21) is locked holdout and is not read. Replication numbers for the #51 units are reported here as well.

## Why this period
#51 has the largest kick sample in the village (H04 round 1b: 697 nudge-target cells, 16,235 bystander cells, read-out-aligned kernels). A nudge kicks one agent. Mean-field Glauber then predicts the target's self-response R_ii(t) = (1/N) e^{−t/τ_c} + (1 − 1/N) e^{−t/τ_⊥} ≈ e^{−t/τ_⊥}: it decays on the single-agent (transverse) clock read from spontaneous fluctuations. Bystanders respond at order g/(N(1 − g)) of the target. H04's and H59's kernels are read as data only.

## Prediction
*Written 2026-10-04 20:42 UTC, before running H99 on #51 (H04's published summaries were known: A30 1.16, t50 14 min, read-out-aligned peak at lag 2).*
- **G51-a (Onsager regression, single agent).** The tail mean delay of H04's read-out-aligned nudge-target kernel (activity, minutes after the peak) lies within [0.5, 2] × the geometric prediction from the #51 activity ρ_⊥(1) (pooled over units), and is closer to it than to the collective prediction from ρ_c(1). [0.4]
- **G51-b (bystanders at order g/N).** H04's bystander/target A30 ratio is ≤ 3 × g_χ/(N(1 − g_χ)) with the #51 activity g_χ and N ≈ 27, or its CI includes that value. [0.6]
- **G51-c (replication).** The #51 talk units are consistent under the A1 rule in ≥ 60% of units with resolved g_χ. [0.45]
- *Against G51-a:* a tail delay > 2 × the transverse prediction (the response persists longer than the agent's own memory: a field or the nudger's selection, H59).

## Result
Data: `natives/g51.json` (H04 and H59 numbers read from their round-1b outputs, not recomputed).

**G51-a failed (the nudge response outlives the agent's own clock).** H04's read-out-aligned nudge-target kernel (697 cells) is G(0) = 0.107 extra active minutes in the read-out minute, then G(1…4) = 0.003, −0.014, −0.016, 0.009, so the immediate part decays within one minute (ratio G(1)/G(0) = 0.03). The #51 activity transverse ratio is ρ_⊥(1) = 0.34 (11 units, minute-weighted), and the Glauber collective ratio 0.37. Onsager regression with that clock predicts an integrated response of G(0)/(1 − 0.34) = 0.16 active minutes. H04 measures A30 = 1.53 [1.13, 1.99]: about 10 times more. About 93% of the response sits in a weak tail over 2–30 min (H04 t50 = 10 min). H59's call-clock kernel has the same shape: 1, 0.44, 0.17, 0.10 (calls 3–5), 0.06 (6–10), 0.09 (11–30). A kick on one agent is not a perturbation that relaxes on the fluctuation clock. H59 reads the tail as the nudger's selection of idle-prone agents.

**G51-b consistent (power-limited).** Bystander/target A30 = 0.052 / 1.158 = 0.045; the bystander CI [−0.018, 0.126] includes the mean-field value g_χ/(N(1 − g_χ)) = 0.003 (g_χ = 0.070 [0.044, 0.096] for #51 activity, N ≈ 27).

**G51-c failed.** #51 talk units (A2 rule): 4 consistent, 4 slow, 1 slow with unresolved gain, 2 unresolved. Consistent in 4/9 resolved units (44% < 60%). The slow calls carry Δρ₁ = 0.05–0.14 (51a 0.136 [0.090, 0.168]; 51g 0.055 [0.028, 0.082]): the collective talk mode keeps memory for minutes while single agents keep none (ρ_⊥(1) ≈ 0), the signature of the read-out coupling H67 measured (g_lag ≈ 0.14 here).

| Unit | g_χ (talk) | Δρ₁ [95%] | call |
| --- | --- | --- | --- |
| 51a | 0.195 | 0.136 [0.090, 0.168] | slow |
| 51c | 0.085 | 0.050 [−0.004, 0.097] | consistent |
| 51d | 0.199 | 0.054 [0.003, 0.106] | slow |
| 51e | 0.175 | 0.104 [0.048, 0.171] | slow |
| 51f | 0.102 | 0.014 [−0.023, 0.049] | consistent |
| 51g | 0.124 | 0.055 [0.028, 0.082] | slow |
| 51h | 0.144 | 0.010 [−0.051, 0.064] | consistent |
| 51i | 0.043 | −0.011 [−0.078, 0.054] | unresolved |
| 51j | 0.110 | 0.070 [−0.007, 0.148] | consistent |
| 51k | 0.148 | 0.223 [0.121, 0.321] | slow (g unresolved) |
| 51l | 0.240 | 0.108 [−0.033, 0.272] | unresolved |

## Scorecard (period-specific axes)
D (an unfitted kernel predicted from fluctuations), G (H04/H59 kernels), H (transverse vs collective clock).

## Notes

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | +0.107 ± 0.020 | +0.123 ± 0.034 | +0.026 [-0.025, +0.082] | +0.187 [-6.793, +13.396] | +0.313 [+0.225, +0.417] | +0.105 [-8.550, +11.390] | +0.41 [+0.32, +0.48] | +0.129 |
| 51c | +0.053 ± 0.027 | +0.017 ± 0.041 | -0.062 [-0.078, -0.047] | +1.052 [-6.270, +2.101] | +0.266 [+0.218, +0.306] | +0.529 [+0.364, +33.472] | +0.12 [+0.02, +0.31] | +0.160 |
| 51d | +0.044 ± 0.028 | +0.020 ± 0.037 | -0.061 [-0.083, -0.036] | +0.143 [-0.351, +0.278] | +0.260 [+0.192, +0.320] | +0.072 [-0.527, +0.090] | +0.14 [+0.00, +0.37] | +0.075 |
| 51e | +0.109 ± 0.028 | +0.049 ± 0.042 | +0.010 [-0.011, +0.030] | +0.487 [+0.285, +22.567] | +0.291 [+0.188, +0.387] | -0.175 [-0.364, +0.242] | +0.38 [+0.31, +0.46] | +0.127 |
| 51f | +0.024 ± 0.021 | +0.047 ± 0.033 | -0.014 [-0.034, +0.006] | +0.021 [-0.065, +0.103] | +0.303 [+0.207, +0.410] | +0.002 [-0.007, +0.009] | +0.05 [+0.00, +0.21] | +0.123 |
| 51g | +0.067 ± 0.015 | +0.056 ± 0.021 | +0.015 [-0.001, +0.033] | +0.233 [+0.177, +0.280] | +0.238 [+0.201, +0.274] | +0.023 [-0.007, +0.045] | +0.24 [+0.13, +0.35] | +0.147 |
| 51h | +0.014 ± 0.038 | -0.022 ± 0.033 | -0.019 [-0.041, +0.004] | +0.272 [-0.131, +0.560] | +0.514 [+0.370, +0.631] | -0.102 [-0.210, -0.034] | +0.05 [+0.00, +0.70] | +0.292 |
| 51i | +0.014 ± 0.049 | +0.012 ± 0.046 | -0.021 [-0.052, +0.013] | -0.048 [-0.175, +0.084] | +0.297 [+0.144, +0.414] | +0.004 [-0.016, +0.033] | +0.10 [+0.00, +0.36] | +0.156 |
| 51j | +0.068 ± 0.049 | +0.070 ± 0.074 | -0.013 [-0.059, +0.055] | +0.039 [-0.026, +0.113] | +0.290 [+0.216, +0.403] | -0.000 [-0.014, +0.021] | +0.18 [+0.00, +0.43] | +0.196 |
| 51k | +0.147 ± 0.043 | +0.129 | +0.149 [+0.091, +0.203] | -0.006 [-0.092, +0.093] | +0.319 [+0.214, +0.415] | +0.026 [+0.013, +0.060] | – | +0.019 |
| 51l | +0.067 ± 0.091 | +0.088 | +0.160 [+0.074, +0.213] | +0.035 [-0.099, +0.144] | +0.320 [+0.249, +0.369] | +0.007 [-0.019, +0.030] | +0.45 [+0.00, +0.95] | +0.152 |

Regime III. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading: the collective talk memory survives scheduler removal where it was present in round 1; reads couple at the next call (room-gated g₁ ≈ H67's g_lag), mostly through named messages. See the card for pooled tests.

**Native R4 (post hoc, Amendment B2): nudges on the receiving call.** 525 primary-target receipts matched to same-agent, same-day, same-class placebo calls.
- Activity response: its peak is one minute after the receiving call. The 30-min integral is 0.44 [−0.41, 1.23] extra active minutes (round 1: 1.53 from H04's message-aligned kernel). Ω = 1.29 (CI uninformative). The round-1 form is 2.7 [−3.6, 6.9].
- Talk on the call clock: the receiving call talks 24 pp more; Ω_call = 1.71 [0.81, 2.71].
- **The round-1 ×9.5 is withdrawn.** In most #51 units one room holds almost every agent, so the room-gated g₁ is unidentified there; use the in-flight-gated and named estimates.

