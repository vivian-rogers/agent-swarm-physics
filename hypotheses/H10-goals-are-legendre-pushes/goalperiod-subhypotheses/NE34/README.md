# H10 × NE34: goal changes as field steps (free → assigned pairs and kickoffs)

**Verdict:** failed (P1 fails in combination: r > 0 in 1/3 pairs, Stouffer p = 0.89; P2 untestable, every push non-perturbative)
**Role:** exploratory
**Period:** spans goal periods (exception (c), the transition is the object). Three primary pairs: #11 → #12a, #16 → #17, #37 → #38a; secondary pairs #3 → #4, #5 → #6 (N = 4); kickoff event study at every non-holdout, within-regime goal change (#23 excluded, to keep #22 → #23 blind).

**Folder choice:** one `NE34/` folder with tables, rather than one folder per pair, so the overview builder (which reads only `G<NN>` and `NE<NN>` names) picks it up. Per-pair figures are in `figures/`, per-period descriptions in the `G<NN>/` folders.

## Why this
A goal change is the only intervention on the field the village ever had. A free week followed by an assigned week is as close as the data come to "same system, field off → field on", so it is where the tilt P_A ∝ P_F·e^{λ·Σy} can be tested.

## Prediction
*Written 2026-10-03, before running on any pair.* Card P1–P4 per pair, with the card's rules. **Per-pair verdict:** supported if P1 (r > 0 and tilt beats translation leave-one-agent-out) and P2 are supported and neither P3 nor P4 fails; failed if r ≤ 0 or P2 fails; mixed otherwise.

| Pair | Mode step | N (expected) | Expected direction |
| --- | --- | --- | --- |
| #11 → #12a | F → M (teams) | 7 | Δ̄ > 0; P1 weakest here (team structure gives two fields, not one); R5 sign unclear |
| #16 → #17 | F → I (own website) | 7 | Δ̄ > 0; cleanest P1 test; R5 predicts g falls |
| #37 → #38a | F → C (charity) | 12 | Δ̄ > 0; largest A segment; R5 predicts g rises |

**Kickoffs (P5, descriptive):** Δm_k > 0 at ≥ 80% of transitions into modes C, I, K, M, D; Spearman(Δm_k, v̄_k) > 0 within regime I.

## Result
Run 2026-10-03 (`analysis/run_pairs.py`, 1,000 day-block bootstrap draws; `analysis/kickoffs.py`). Data: `data/processed/H10-goals-are-legendre-pushes/NE34/` (`pairs.json`, `robustness.json`, `kickoffs.json`, `kickoffs_posthoc_level.json`). Figures: [`figures/pair_<pair>.pdf`](figures/) (shape, P1 scatter, variance, P4) and [`figures/kickoffs.pdf`](figures/kickoffs.pdf). Card: [`../../README.md`](../../README.md).

### Free → assigned pairs
| Pair | N | windows F/A | Δ̄ | λ | ε | P1 r (perm p) | LOAO MSE tilt/transl | P2 ρ [90% CI] | ρ_Gauss | ρ⊥ | g_F → g_A | Δg [90% CI] | P4 D [90% CI] | verdicts P1 / P2 / P3 / P4 → pair |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #11 → #12a | 7 | 30/18 | 0.203 | 46.0 | 3.06 | -0.37 (0.804) | 2.38 | – [1.64, 5.54] | 2.04 | -0.14 | 0.55 → 0.79 | 0.25 [0.15, 0.57] | -0.598 [-0.708, -0.341] | failed / n/a (non-perturbative, eps = 3.06 > 0.34) / failed / failed → **failed** |
| #16 → #17 | 7 | 30/24 | 0.134 | 15.0 | 1.42 | -0.69 (0.969) | 2.07 | 1.73 [0.55, 3.26] | 1.03 | -0.12 | 0.51 → 0.70 | 0.20 [-0.13, 0.72] | -0.195 [-0.376, 0.018] | failed / n/a (non-perturbative, eps = 1.42 > 0.34) / supported / failed → **failed** |
| #37 → #38a | 12 | 24/56 | 0.112 | 28.1 | 1.92 | 0.20 (0.271) | 1.38 | 1.00 [-0.42, 1.94] | 0.66 | -0.12 | 0.62 → 0.58 | -0.04 [-0.53, 0.33] | -0.060 [-0.164, 0.056] | mixed / n/a (non-perturbative, eps = 1.92 > 0.34) / supported / failed → **mixed** |
| #3 → #4a (secondary) | 4 | 12/20 | 0.050 | 4.4 | 0.53 | 0.82 (0.125) | 0.51 | 0.06 [-1.13, 1.28] | -0.48 | -0.12 | 0.57 → 0.28 | -0.30 [-0.66, 0.12] | -0.068 [-0.373, 0.209] | supported / n/a (non-perturbative, eps = 0.53 > 0.34) / supported / failed → **mixed** |
| #5 → #6a (secondary) | 4 | 20/24 | 0.187 | 23.2 | 1.76 | -0.63 (1.000) | 2.12 | 0.44 [-0.18, 1.54] | 1.04 | 0.28 | 0.47 → 0.57 | 0.10 [-0.21, 0.41] | -0.110 [-0.282, 0.085] | failed / n/a (non-perturbative, eps = 1.76 > 0.34) / supported / failed → **failed** |

ρ is against the first-order tilt prediction (undefined for #11 → #12a, where that prediction is negative); ρ_Gauss is against "variance unchanged" (the Gaussian tilt); ρ⊥ is the median over 50 transverse directions. P3 and P4 are descriptive (Amendment 1); their per-pair labels use the original rules.

**Combined (primary pairs):** P1 **failed** (r > 0 in 1/3 pairs; Stouffer p = 0.89; in the synthetic, P1 falsely fails under H in 0–8% of triples at these pushes). P2 **n/a**: every push is non-perturbative (ε = 3.06, 1.42, 1.92 > ε_max = 0.34; also > 1.2, so no "would-be" verdicts either). P3: 2/3 CIs contain 0; #11 → #12a's loop gain rose (Δg = 0.25 [0.15, 0.57]). P4: D < 0 in all pairs, as the synthetic predicted even under H. **Overall: failed.**

**What the assigned weeks did instead** (descriptive, robust across variants):
1. **Agents converge rather than tilt.** In both regime-I pairs the most-fluctuating agents moved least (cross-split r = −0.45, −0.68). In #11 → #12a, Δᵢ fell with μᵢ^F at slope −1.41 (cross-split): every agent ended near the same alignment (rival R2, a common target).
2. **Field-specific dispersal.** Variance along ĝ grew ×1.9–7.7 over the free week, while transverse variance did not change (ρ⊥ ≈ −0.12 in every pair). The tilt of a bounded, saturating F predicts the opposite at these pushes (synthetic median ρ −0.25 to −1.6). The free-week shapes are left-skewed (γ_F = −0.51, −0.30, −0.11), so the on-goal state the assigned week populates leaves no trace in free-week fluctuations.
3. **Collective switching.** Mean pairwise signal correlation along ĝ rose 0.20 → 0.64 (#11 → #12a) and 0.17 → 0.40 (#16 → #17); flat in #37 → #38a (0.15 → 0.13).
4. **Not a step response.** #12a is still relaxing after its kickoff day; #38a is still ramping up after ten days (see G12, G38).

### Robustness (primary pairs, 200 bootstrap draws each)
| Pair: variant | N | Δ̄ | ε | P1 r (p) | P2 ρ | Δg | P4 D | pair |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 11-12:n16 | 7 | 0.166 | 1.02 | -0.29 (0.730) | 1.90 | 0.06 | -0.452 | failed |
| 11-12:n64 | 7 | 0.147 | 2.29 | 0.03 (0.492) | 2.93 | 0.33 | -0.406 | mixed |
| 11-12:goal_only | 7 | 0.144 | 2.61 | -0.67 (0.950) | 1.94 | 0.42 | -0.496 | failed |
| 11-12:kickoff_only | 7 | 0.232 | 3.60 | -0.23 (0.686) | – | 0.20 | -0.603 | failed |
| 11-12:with_day1 | 7 | 0.243 | 3.67 | -0.35 (0.786) | – | 0.25 | -0.601 | failed |
| 11-12:win60 | 7 | 0.195 | 2.96 | -0.52 (0.892) | – | 0.25 | -0.566 | failed |
| 16-17:n16 | 7 | -0.020 | -0.12 | -0.87 (0.993) | -0.23 | 0.02 | -0.085 | failed |
| 16-17:n64 | 7 | 0.099 | 1.19 | -0.77 (0.999) | 0.78 | 0.11 | -0.131 | failed |
| 16-17:goal_only | 7 | 0.117 | 1.32 | -0.73 (0.993) | 0.96 | 0.09 | -0.094 | failed |
| 16-17:kickoff_only | 7 | 0.134 | 1.56 | -0.57 (0.918) | 2.84 | 0.42 | -0.291 | failed |
| 16-17:with_day1 | 7 | 0.139 | 1.47 | -0.58 (0.946) | 1.74 | 0.20 | -0.191 | failed |
| 16-17:win60 | 7 | 0.136 | 1.57 | -0.65 (0.962) | 2.26 | 0.19 | -0.210 | failed |
| 37-38:n16 | 12 | 0.121 | 1.15 | 0.36 (0.134) | -0.09 | 0.23 | 0.196 | mixed |
| 37-38:n64 | 12 | 0.102 | 1.67 | -0.28 (0.812) | 1.63 | 0.26 | 0.017 | failed |
| 37-38:goal_only | 12 | 0.150 | 1.77 | -0.03 (0.533) | 0.18 | -0.03 | -0.058 | failed |
| 37-38:kickoff_only | 12 | 0.047 | 0.58 | 0.21 (0.252) | 0.19 | 0.09 | -0.065 | mixed |
| 37-38:with_day1 | 12 | 0.109 | 1.85 | 0.26 (0.204) | 1.13 | -0.00 | -0.114 | mixed |
| 37-38:win60 | 12 | 0.103 | 1.37 | 0.04 (0.448) | 0.47 | -0.05 | -0.150 | mixed |

P1's negative sign in the regime-I pairs survives every variant except #11 → #12a at n = 64 (r = +0.03). #37 → #38a flips sign across variants (inconclusive). At n = 16 the #16 → #17 push vanishes (Δ̄ = −0.02): the goal content of ĝ₁₇ lives beyond the first 16 whitened components.

### Secondary pairs (N = 4, not counted)
#3 → #4a: r = +0.82 (p = 0.13), ε = 0.53, variance ×0.6. #5 → #6a: r = −0.63, ε = 1.76, variance ×2.8.

### Kickoff event study (P5, descriptive)
| Transition | regime | modes | N | Δm | v̄ (κ2) | ε = Δm/√v̄ |
| --- | --- | --- | --- | --- | --- | --- |
| #2 → #3 | I | F → F | 3 | 0.100 | 0.0142 | 0.84 |
| #3 → #4 | I | F → C | 4 | 0.047 | 0.0143 | 0.39 |
| #4 → #5 | I | C → F | 4 | 0.019 | 0.0085 | 0.21 |
| #5 → #6 | I | F → K | 4 | 0.270 | 0.0057 | 3.56 |
| #6 → #7 | I | K → F | 4 | -0.065 | 0.0136 | -0.56 |
| #7 → #8 | I | F → C | 4 | 0.226 | 0.0032 | 4.02 |
| #10 → #11 | I | I → F | 7 | -0.109 | 0.0079 | -1.23 |
| #11 → #12 | I | F → M | 7 | 0.375 | 0.0044 | 5.65 |
| #12 → #13 | I | M → C | 6 | 0.092 | 0.0071 | 1.09 |
| #16 → #17 | I | F → I | 7 | 0.136 | 0.0090 | 1.43 |
| #17 → #18 | I | I → C | 7 | 0.187 | 0.0082 | 2.08 |
| #18 → #19 | I | C → C | 7 | 0.219 | 0.0056 | 2.92 |
| #19 → #20 | I | C → I | 8 | 0.197 | 0.0104 | 1.93 |
| #20 → #21 | I | I → I | 8 | 0.260 | 0.0109 | 2.50 |
| #24 → #25 | I | C → C | 10 | 0.260 | 0.0053 | 3.56 |
| #25 → #26 | I | C → C | 10 | 0.358 | 0.0089 | 3.80 |
| #26 → #27 | I | C → K | 10 | 0.570 | 0.0038 | 9.24 |
| #30 → #31 | I | C → F | 11 | 0.016 | 0.0110 | 0.16 |
| #35 → #36 | II | C → C | 11 | 0.301 | 0.0044 | 4.53 |
| #37 → #38 | III | F → C | 12 | 0.074 | 0.0047 | 1.08 |
| #38 → #39 | III | C → I | 13 | 0.249 | 0.0053 | 3.43 |
| #39 → #40 | III | I → C | 15 | 0.227 | 0.0139 | 1.93 |
| #40 → #41 | III | C → I | 15 | 0.130 | 0.0077 | 1.49 |
| #41 → #42 | III | I → I | 14 | 0.471 | 0.0071 | 5.60 |

- **Δm > 0 at 19/19 transitions into assigned goals** (P5 part 1 ✓). Transitions *into* free weeks jump little or negatively (#4 → #5 +0.02, #6 → #7 −0.07, #10 → #11 −0.11, #30 → #31 +0.02), which is the expected control.
- **Cross-transition fluctuation–dissipation fails with the opposite sign:** Spearman(Δm, v̄) = **−0.56** (p = 0.015, n = 18) in regime I; +0.20 (n = 5) in regime III. P5 part 2 ✗.
- *Post hoc* (`kickoffs_posthoc_level.json`): in regime I, Δm also falls with the pre-period level along ĝ_new (Spearman −0.55, from the old period's last ≤ 5 days excluding the last day, so no noise is shared with the jump). In a joint rank regression both coefficients stay negative (v̄ −0.43, level −0.41).
- Goal pushes are typically 1–9 pre-period SDs (median ≈ 2.5): **goal changes in the village are almost never small perturbations.**

## Notes
- 2026-10-03: the confirmatory script (`../../analysis/confirm.py`, dry-run on #16 → #17 and #11 → #12a) reproduces these pair numbers exactly through an independent build path (shared tables, goal and kickoff texts re-embedded on the fly).
