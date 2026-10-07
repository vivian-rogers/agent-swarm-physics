# H142 × G36: interact with outside agents (2026-03-23 → 2026-03-27)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime II (36a) then III (36b, 36c) · two rooms · 12 agents · 5 days. The regime-II whitener is used for the whole period, as in H113; the regime step at 03-24 is noted as a limitation. Units from `period_units`.

## Why this period
Field-identified by H113 in both models (b̂ 0.67 [0.61, 0.73] bge).

## Prediction
*Written 2026-10-07 ~13:20 UTC by the round-1 agent, before running on this period (copied from the card's replication layer, as the card's "Results by goal period" note asks). Seen: H113's numbers for this period; no aligned count, cluster assignment or directional step.*
- **P1:** ΔLL(Langevin − linear) > 0 with CI above 0. Credence 0.35.
- **P2:** Δ_curv > 0 with CI above 0. Credence 0.25.
- **P3:** n̂_sat ∈ [1.5, 6]. Credence 0.3.
- **P4:** ĝ(1)/f̂(1) ≤ 0.5 and read − in-flight contrast at n = 1 > 0. Credence 0.6.
- Counts against: the card's kill on this period, if the synthetic power against W-L3 is ≥ 0.8 here. Below 200 rows with n_u ≥ 4 or power < 0.8, the period reports a descriptive shape only.

## Result
*Round 1, 2026-10-07 (exploratory). Amendments A1–A4 in the card apply. Figure: `figures/step_curve.pdf`.*
- **bge** (12,224 rows, 153 with n_u ≥ 4, 5 days; power vs W-L3 0.4; scored: no).
  - O1 step curve: f̂(1) 0.0166 [0.0045, 0.0300], f̂(2) 0.0351 [0.0086, 0.0609], f̂(3) 0.0341 [-0.0040, 0.0678], f̂(4–5) 0.0533 [0.0166, 0.0958], f̂(6+) -0.0061 [-0.0524, 0.0406].
  - O2 Δ_curv undefined (a bin ≤ 0). f̂(6+)/f̂(3) -0.179 [-4.249, 1.573].
  - O3 out of fold (A1 form): ΔLL(L − line) 0.0 [-0.0, 0.0] nats; ΔLL(L − power) 1.2 [0.4, 1.8]; ΔLL(power − line) -1.2 [-1.8, -0.4]. Card's pooled-amplitude form: ΔLL(L − line) 5.8 [-1.7, 12.4].
  - Fits: ĉ 0.020 [0.020, 30.000], n̂_sat 150.00 [0.100, 150.000] (grid-edge share 0.79); power p̂ 1.10 [0.050, 1.500].
  - Nuisance pulls: newest item 0.0157 [-0.0072, 0.0342]; named count 0.0251 [0.0057, 0.0451] per aligned named item.
  - O4: ĝ(1) 0.025 [-0.007, 0.061], ĝ(1)/f̂(1) 1.500, read − in-flight at n = 1 -0.008 [-0.049, 0.024]. O5: largest n with ≥ 50 rows 4.
  - Rules: P1 fail, P2 fail, P3 fail, P4 fail; kill (linear curve) False, kill (line as good) True (not applied: unscored); verdict by the card's rule: **descriptive**.
- **gte** (12,224 rows, 159 with n_u ≥ 4, 5 days; power vs W-L3 0.4; scored: no).
  - O1 step curve: f̂(1) 0.0161 [0.0056, 0.0280], f̂(2) 0.0122 [-0.0118, 0.0344], f̂(3) 0.0361 [0.0020, 0.0658], f̂(4–5) 0.0333 [-0.0006, 0.0686], f̂(6+) -0.0290 [-0.0763, 0.0179].
  - O2 Δ_curv undefined (a bin ≤ 0). f̂(6+)/f̂(3) -0.802 [-7.194, 0.704].
  - O3 out of fold (A1 form): ΔLL(L − line) -0.7 [-4.6, 2.5] nats; ΔLL(L − power) 1.1 [-2.2, 4.7]; ΔLL(power − line) -1.7 [-4.6, 0.9]. Card's pooled-amplitude form: ΔLL(L − line) 2.0 [-4.3, 7.5].
  - Fits: ĉ 0.259 [0.020, 30.000], n̂_sat 11.60 [0.100, 150.000] (grid-edge share 0.14); power p̂ 1.50 [0.050, 1.500].
  - Nuisance pulls: newest item 0.0386 [0.0189, 0.0584]; named count 0.0180 [-0.0027, 0.0385] per aligned named item.
  - O4: ĝ(1) 0.038 [0.000, 0.071], ĝ(1)/f̂(1) 2.359, read − in-flight at n = 1 -0.022 [-0.058, 0.020]. O5: largest n with ≥ 50 rows 4.
  - Rules: P1 fail, P2 fail, P3 fail, P4 fail; kill (linear curve) False, kill (line as good) True (not applied: unscored); verdict by the card's rule: **descriptive**.

## Scorecard (period-specific axes)
Descriptive (not scored: H113 identification, the 200-row count or power < 0.8). C, D, F, H: 0.
