# H99 × NE42: room merge and split at a fixed roster (#39 → #40 → #41, 2026-04-27 → 05-15)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** goals #39 (two rooms), #40 (one merged room), #41 (two rooms again) · 15 agents · regime III · 5 days each.

## Why this period
An A-B-A intervention on the room structure at a fixed roster. H25 found that the equal-time talk dial collapses in the merged room (0.13 → 0.003 → 0.18), and H67 found that read-out coupling vanishes there. Mean-field Glauber says the fluctuation gain and the relaxation gain must move together. If the merge removes coupling, both fall; if it removes a field, only g_χ falls.

## Prediction
*Written 2026-10-04 20:42 UTC, before running on these units (Amendment A1 rule).*
- **NE42-a (gain tracks the merge).** Talk g_χ(#40) < g_χ(#39) and < g_χ(#41), each by ≥ 0.05. [0.6]
- **NE42-b (relaxation tracks it too).** Talk g_τ (lag 1) falls the same way: g_τ(#40) < g_τ(#39), g_τ(#41). [0.45]
- **NE42-c (relation holds on both sides).** No field call (A1 rule) in any of the three units. [0.45]
- *Against:* g_χ falls in #40 but g_τ does not (the collapse is in the fluctuation, not in the dynamics), or field calls flip at the boundary.

## Result
Talk channel, all-present trimmed grids (data: `data/processed/H99-glauber-fluctuation-relaxation/natives/ne42.json`).

| Unit | rooms | trimmed min | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | Δρ₁ [95%] | Δρ₂ | A2 call |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #39 | 2 | 852 | 0.114 [0.028, 0.213] | −0.008 | −0.087 | −0.010 [−0.069, 0.051] | 0.025 | consistent |
| #40 | 1 (merged) | 1172 | −0.012 [−0.100, 0.056] | −0.031 | −0.039 | −0.032 [−0.083, 0.008] | 0.013 | unresolved |
| #41 | 2 | 1024 | 0.206 [0.092, 0.311] | 0.091 | −0.028 | 0.086 [−0.017, 0.199] | 0.080 | slow |

- **NE42-a supported.** The fluctuation gain collapses in the merged room: g_χ(#40) − g_χ(#39) = −0.13 [−0.24, −0.002]; g_χ(#40) − g_χ(#41) = −0.22 [−0.36, −0.09] (independent 1-h block bootstraps). This reproduces H25 and H67 with the mean-field split.
- **NE42-b untestable as written; partly supported with the A2 statistic.** ρ_⊥(1) < 0 in all three units, so the log-ratio g_τ is undefined (Amendment A2). The collective memory falls with the gain against #41 (Δρ₁ #40 − #41 = −0.12 [−0.24, −0.004]) but not against #39 (−0.02 [−0.10, 0.06]).
- **NE42-c failed.** #41 carries a slow call (Δρ₂ = 0.080 above its threshold); #39 is consistent and #40 has nothing to predict.
- Reading: the merge removes the equal-time gain, as both the coupling and the field readings allow. On the two-room side the relation holds in #39 and fails in the slow direction in #41, so the boundary does not flip a sign.

## Scorecard (period-specific axes)
E (A-B-A intervention), G (H25 and H67 saw the collapse).

## Notes
- 2026-10-04: g_τ could not be used (A2, post hoc); the verdict uses Δρ.
