# H130 × G51: Private roles, one village (2026-07-06 → 2026-09-21; tail 09-07 → 09-21 held out)

**Verdict:** failed
**Role:** exploratory
**Period:** regime III · private-role period · 21–32 agents · mostly one room (#general; #focus from 08-05; brief onboarding rooms) · 45 non-holdout active days in units 51a–51l. Splits inside the period: `period_units` splits at roster joins (51b NE32 triplet, 51c Grok 4.5, 51d Kimi K3, 51e Claude Opus 5, …, 51k/51l NE33) and at the holdout (51m).

## Why this period
#51 is the only period where every agent has its own assigned role, so each agent has a private well (H98: a random field, R 0.67–0.73). It is also the densest regime-III period in reads (median 761 calls and 20 chat statements per agent-day), so kicks and decays can be resolved per unit. DQ6 rival pairs and mid-period joiners give two native levers no other period has.

## Prediction
*Written 2026-10-04 22:21–22:22 UTC, before running on this period.*
- **Replication (card P1–P6), per unit:** J_K > 0 (read beyond in-flight) in ≥ 60% of units with ≥ 3 days (51a, 51c, 51d, 51e, 51f, 51g, 51h); ρ_γ in [0.5, 2]; β_R > 0; γ_auto homogeneous across units. Expected sizes: J_K small (a few percent of the per-direction spread of x), 1/γ_auto of order 10² calls. Against: J_K ≤ 0 in most units; ρ_γ outside [0.5, 2] with CI excluding 1.
- **N1 rival kicks (native).** Split the read arm of J_K and K(0) by sender: same-role rival (DQ6 `rival_pair`, time-valid) vs every other sender. OU with isotropic κ predicts the kick ratio κ_rival/κ_other in [0.5, 2]. Niche-gated coupling (R3, H98-R1) predicts > 2. Estimator: K(0) and J_K per arm, ratio with agent-day bootstrap over the pooled #51 units. Prediction: ratio in [0.5, 2]. **Credence 0.5.** Against: ratio > 2 with CI excluding 2 (R3), or < 0.5. Reads between rivals are a small share, so the test may be underpowered; the synthetic sets the power first.
- **N3 joiners (native).** Joiners with ≥ 2 non-holdout #51 days (agents 35–37 NE32, 38, 39, 40, 41, 42; 43, 44 if eligible). Well centre from the joiner's own statements on days ≥ 2 (leave-day-1-out). Relaxation curve: d(n) = x·ĥ projection of day-1 statements onto the unit direction from the room consensus to the joiner's well, against calls since the joiner's first #51 call. OU predicts d(n) = d_∞ − (d_∞ − d_0) e^(−γn) with γ = γ_auto (unfitted). Prediction: the fitted joiner rate γ_J is within ×2 of the pooled γ_auto. **Credence 0.3** (H98: joiners took days). Against: γ_J < γ_auto/2 (R5: the well is built, not found), or no approach at all on day 1.

**Amendment A1 (2026-10-04 22:48 UTC, before running on this period; see the card).** γ_kick comes from the sender-specific dose regression, γ_auto from the drive-corrected autocorrelation, and K1/K2 are judged on the pool of units. N1 is estimated in the dose regression: rival-sender reads get their own columns (bins 0–63 calls), and κ_rival/κ_other = the ratio of the summed coefficients. Thresholds unchanged.

## Result
*Run 2026-10-04 22:56–23:13 UTC (after A1). Data: `data/processed/H130-ou-private-wells-51/results/`. Figure: `../../figures/summary_obs_col.pdf`.*

| Unit | Days | J_K [95%] | γ_auto /call | γ_kick /call | ρ_γ [90%] | Unit verdict |
| --- | --- | --- | --- | --- | --- | --- |
| 51a | 3 | 0.043 [0.031, 0.060] | 0.0077 | 0.12 | 15 [0.0, 37] | mixed |
| 51b | 1 | 0.060 [0.013, 0.098] | 0.0018 | 0.12 | 64 [8, ∞) | descriptive |
| 51c | 5 | 0.051 [0.030, 0.074] | 0.0122 | 0.38 | 31 [0.5, 67] | mixed |
| 51d | 5 | 0.043 [0.027, 0.059] | 0.0120 | 0.10 | 8.1 [2.2, 227] | failed |
| 51e | 3 | 0.053 [0.030, 0.071] | 0.0099 | 0.31 | 31 [0.9, 167] | mixed |
| 51f | 5 | 0.046 [0.027, 0.068] | 0.0079 | 0.07 | 8.8 [0.7, 47] | mixed |
| 51g | 13 | 0.044 [0.030, 0.057] | 0.0082 | 0.15 | 18 [9.4, 43] | failed |
| 51h | 4 | 0.055 [0.022, 0.085] | 0.0118 | 0.51 | 44 [0.0, 151] | mixed |
| 51i | 2 | 0.044 [0.006, 0.071] | 0.0098 | 0.18 | 18 [2.0, 121] | descriptive |
| 51j | 2 | 0.051 [0.017, 0.078] | 0.0047 | 0.22 | 46 [0.0, 234] | descriptive |
| 51k | 1 | 0.038 [0.016, 0.060] | 0.0060 | 0.01 | 1.2 [0.5, 271] | descriptive |
| 51l | 1 | 0.018 [−0.002, 0.042] | 0.0179 | ≈ 0 | — | descriptive |
| **pool (RE)** | 45 | **0.044 [0.038, 0.050]** | **0.0094 [0.0076, 0.0115]** | ≈ 0.13 [0.06, 0.27] | **14.8 [7.2, 30.4]** | **K1 fires** |

- gte: J_K 0.049 [0.041, 0.057], γ_auto 0.0092, ρ_γ 20.2 [6.8, 59.9]. white32: 0.044, 0.0092, 13.9 [7.8, 24.9].
- Co-movement slope β_R 0.018 [0.012, 0.024] (positive in 12/12 units; gte 0.019, white32 0.019).
- **N1 rival kicks:** κ_rival/κ_other 2.39 [−0.66, 5.32] (bge), 1.30 [−0.76, 3.42] (gte); rival reads are 45,738 of 2.4M read-dose counts. **Inconclusive** (CI covers both [0.5, 2] and > 2).
- **N3 joiners** (agents 35–44, 398 day-1 statements): the day-1 own-well position is 0.39 (gte 0.38) of the day-2+ level and flat over ≈ 600 calls (bins 0.42, 0.12, 0.47, 0.40, 0.41, 0.33, then 0.80 in the last, thin bin). The bge fit gives γ_J 0.013 [0, 0.60]; gte finds no approach. **Failed**: a joiner does not relax into a pre-existing well at γ_auto (≈ 1 h); it gets there over days.

## Scorecard (period-specific axes)
C 2 (read jump beats the in-flight placebo in every unit ≥ 3 days); D 1 (one-rate check and joiner relaxation fail; read→co-movement holds); G 0 (rival native inconclusive).

## Notes
- 2026-10-04 22:21 UTC: folder created from the template; predictions written before any H130 statistic.
- 2026-10-04 23:13 UTC: results added.
