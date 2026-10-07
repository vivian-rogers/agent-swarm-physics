# H142 × G37: free 3 days (2026-03-30 → 2026-04-01)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime III · two rooms · 12 agents · 3 days. Units from `period_units`.

## Why this period
Field-identified by H113 in both models (b̂ 0.82 [0.75, 0.88] bge). Three days only: few day folds.

## Prediction
*Written 2026-10-07 ~13:20 UTC by the round-1 agent, before running on this period (copied from the card's replication layer, as the card's "Results by goal period" note asks). Seen: H113's numbers for this period; no aligned count, cluster assignment or directional step.*
- **P1:** ΔLL(Langevin − linear) > 0 with CI above 0. Credence 0.35.
- **P2:** Δ_curv > 0 with CI above 0. Credence 0.25.
- **P3:** n̂_sat ∈ [1.5, 6]. Credence 0.3.
- **P4:** ĝ(1)/f̂(1) ≤ 0.5 and read − in-flight contrast at n = 1 > 0. Credence 0.6.
- Counts against: the card's kill on this period, if the synthetic power against W-L3 is ≥ 0.8 here. Below 200 rows with n_u ≥ 4 or power < 0.8, the period reports a descriptive shape only.

## Result
*Round 1, 2026-10-07 (exploratory). Amendments A1–A4 in the card apply. Figure: `figures/step_curve.pdf`.*
- **bge** (5,368 rows, 76 with n_u ≥ 4, 3 days; power vs W-L3 0.4; scored: no).
  - O1 step curve: f̂(1) 0.0198 [0.0002, 0.0394], f̂(2) 0.0063 [-0.0284, 0.0436], f̂(3) 0.0389 [-0.0214, 0.1013], f̂(4–5) 0.0249 [-0.0364, 0.0860], f̂(6+) 0.0252 [-0.1084, 0.1333].
  - O2 Δ_curv -0.71 [—, —]. f̂(6+)/f̂(3) 0.646 [-7.200, 10.617].
  - O3 out of fold (A1 form): ΔLL(L − line) -0.8 [-2.4, 0.0] nats; ΔLL(L − power) 2.4 [1.7, 3.5]; ΔLL(power − line) -3.2 [-4.4, -1.7]. Card's pooled-amplitude form: ΔLL(L − line) -0.2 [-0.4, -0.0].
  - Fits: ĉ 0.020 [0.020, 30.000], n̂_sat 150.00 [0.100, 150.000] (grid-edge share 0.86); power p̂ 1.20 [0.250, 1.500].
  - Nuisance pulls: newest item 0.0279 [-0.0000, 0.0613]; named count 0.0203 [-0.0072, 0.0505] per aligned named item.
  - O4: ĝ(1) 0.032 [-0.013, 0.087], ĝ(1)/f̂(1) 1.597, read − in-flight at n = 1 -0.012 [-0.066, 0.038]. O5: largest n with ≥ 50 rows 2.
  - Rules: P1 fail, P2 fail, P3 fail, P4 fail; kill (linear curve) True, kill (line as good) True (not applied: unscored); verdict by the card's rule: **descriptive**.
- **gte** (5,368 rows, 64 with n_u ≥ 4, 3 days; power vs W-L3 0.24; scored: no).
  - O1 step curve: f̂(1) 0.0364 [0.0116, 0.0575], f̂(2) 0.0433 [0.0060, 0.0796], f̂(3) 0.0346 [-0.0281, 0.0918], f̂(4–5) -0.0150 [-0.1079, 0.0661], f̂(6+) 0.0289 [-0.0759, 0.0988].
  - O2 Δ_curv 0.36 [-3.501, 3.248]. f̂(6+)/f̂(3) 0.834 [-10.729, 16.196].
  - O3 out of fold (A1 form): ΔLL(L − line) 0.7 [-2.8, 6.0] nats; ΔLL(L − power) 2.1 [-3.3, 9.6]; ΔLL(power − line) -1.4 [-3.5, 0.5]. Card's pooled-amplitude form: ΔLL(L − line) -4.7 [-10.4, 0.5].
  - Fits: ĉ 30.000 [0.020, 30.000], n̂_sat 0.10 [0.100, 150.000] (grid-edge share 0.74); power p̂ 0.05 [0.050, 1.500].
  - Nuisance pulls: newest item 0.0280 [-0.0006, 0.0603]; named count 0.0201 [-0.0032, 0.0499] per aligned named item.
  - O4: ĝ(1) 0.011 [-0.061, 0.088], ĝ(1)/f̂(1) 0.290, read − in-flight at n = 1 0.026 [-0.068, 0.105]. O5: largest n with ≥ 50 rows 2.
  - Rules: P1 fail, P2 fail, P3 fail, P4 fail; kill (linear curve) True, kill (line as good) True (not applied: unscored); verdict by the card's rule: **descriptive**.

## Scorecard (period-specific axes)
Descriptive (not scored: H113 identification, the 200-row count or power < 0.8). C, D, F, H: 0.
