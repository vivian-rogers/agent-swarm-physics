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
