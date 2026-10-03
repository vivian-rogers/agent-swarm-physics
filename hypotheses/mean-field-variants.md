# Mean-field-forward variants of the hypotheses

For each hypothesis, a variant that **fixes a few-parameter mean-field model and tests its forward predictions** instead of learning a full N×N coupling matrix. These are robust at small N and short windows, and falsifiable on statistics not used in the fit (faithfulness axis D). Ideas: HH80–HH89 in [hypohypotheses/HYPOHYPOTHESES.md](hypohypotheses/HYPOHYPOTHESES.md). Model background: the "Mean-field forward version" sections of models 01, 02, 10 and 11.

| Hypothesis | Mean-field variant | Parameters | Forward prediction tested | Ideas |
| --- | --- | --- | --- | --- |
| H01 (superagents) | **D3-MF:** mean-field O(n) or Potts order for group positions; **D1-MF:** a block mean field per candidate group | (βJ₀, h) per group; (J_in, J_out) | polarization response at kickoffs; within- vs. across-group coupling | HH85, HH84, HH82, HH89 |
| H02 (couplings real) | **H02-MF:** Curie–Weiss inversion; leader–follower mean field | βJ₀; (J_lf, J_ff, h) | βJ₀ ≈ 0 in null weeks; P(K) shape; J_lf large in leader weeks | HH80, HH83 |
| H03 (criticality) | already mean-field: univariate Hawkes branching ratio n | n, baseline | — | (HH30, HH32) |
| H04 (reversible forcing) | **H04-MF:** mean-field Glauber relaxation | βJ₀ (from fluctuations), τ₀ | response decay time τ = τ₀/(1 − βJ₀(1−m²)) | HH81 |
| H05 (rooms cut) | **H05-MF:** two-block mean field | J_in, J_out | J_out → 0 after rooms; J_in unchanged | HH82 |
| H09 (thermodynamics) | **T1/T2-MF:** mean-field free energy f(m) and Legendre tilt by the field | βJ₀, h | double well iff βJ₀ > 1; hysteresis under field reversal; occupancies under the field from field-free fits | HH86, HH49 |
| S5 (field vs. coupling) | **S5-MF:** mean-field O(n) with a field | βJ₀ (coupling), h (field) | field-only vs. coupling contributions to polarization | HH85 |
| S6 (neutral cooperation) | already analytic mean field (Piñero et al.) | μ, N | — | HH42 |
| contagion ideas | **Bass / mean-field SIS** | p, q (or λ, γ) | as good as network models at N ≲ 30 until rooms | HH88 |

Status (2026-10-03):
- **H02, H04, H05:** their agents were asked to add the variant to their cards, light.
- **H01 and H09:** variants added directly (see their files).
