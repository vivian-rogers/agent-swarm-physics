# H142 × G35: test your game, forked per room (2026-03-16 → 2026-03-20)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime II · two rooms · 12 agents · 5 days. Units from `period_units`.

## Why this period
Field-identified by H113 in gte only (b̂ 0.70 gte).

## Prediction
*Written 2026-10-07 ~13:20 UTC by the round-1 agent, before running on this period (copied from the card's replication layer, as the card's "Results by goal period" note asks). Seen: H113's numbers for this period; no aligned count, cluster assignment or directional step.*
- **P1:** ΔLL(Langevin − linear) > 0 with CI above 0. Credence 0.35.
- **P2:** Δ_curv > 0 with CI above 0. Credence 0.25.
- **P3:** n̂_sat ∈ [1.5, 6]. Credence 0.3.
- **P4:** ĝ(1)/f̂(1) ≤ 0.5 and read − in-flight contrast at n = 1 > 0. Credence 0.6.
- Counts against: the card's kill on this period, if the synthetic power against W-L3 is ≥ 0.8 here. Below 200 rows with n_u ≥ 4 or power < 0.8, the period reports a descriptive shape only.

## Result
*Round 1, 2026-10-07 (exploratory). Amendments A1–A4 in the card apply. Figure: `figures/step_curve.pdf`.*
- **bge** (16,176 rows, 387 with n_u ≥ 4, 5 days; power vs W-L3 0.67; scored: no).
  - O1 step curve: f̂(1) 0.0215 [0.0127, 0.0326], f̂(2) 0.0273 [0.0104, 0.0443], f̂(3) 0.0388 [0.0120, 0.0643], f̂(4–5) 0.0337 [0.0037, 0.0612], f̂(6+) 0.0576 [0.0139, 0.0988].
  - O2 Δ_curv -0.15 [-1.572, 1.271]. f̂(6+)/f̂(3) 1.485 [0.334, 5.951].
  - O3 out of fold (A1 form): ΔLL(L − line) -0.0 [-0.0, 0.0] nats; ΔLL(L − power) 3.3 [0.0, 9.0]; ΔLL(power − line) -3.3 [-9.0, -0.0]. Card's pooled-amplitude form: ΔLL(L − line) 2.6 [-3.1, 7.3].
  - Fits: ĉ 0.020 [0.020, 30.000], n̂_sat 150.00 [0.100, 150.000] (grid-edge share 0.72); power p̂ 1.10 [0.050, 1.500].
  - Nuisance pulls: newest item 0.0282 [0.0132, 0.0450]; named count -0.0108 [-0.0263, 0.0049] per aligned named item.
  - O4: ĝ(1) 0.056 [0.032, 0.084], ĝ(1)/f̂(1) 2.615, read − in-flight at n = 1 -0.035 [-0.063, -0.010]. O5: largest n with ≥ 50 rows 5.
  - Rules: P1 fail, P2 fail, P3 fail, P4 fail; kill (linear curve) True, kill (line as good) True (not applied: unscored); verdict by the card's rule: **descriptive**.
- **gte** (16,176 rows, 405 with n_u ≥ 4, 5 days; power vs W-L3 0.61; scored: no).
  - O1 step curve: f̂(1) 0.0218 [0.0090, 0.0321], f̂(2) 0.0347 [0.0196, 0.0482], f̂(3) 0.0516 [0.0298, 0.0803], f̂(4–5) 0.0553 [0.0229, 0.0866], f̂(6+) 0.0734 [0.0322, 0.1104].
  - O2 Δ_curv 0.11 [-0.616, 1.219]. f̂(6+)/f̂(3) 1.423 [0.690, 2.390].
  - O3 out of fold (A1 form): ΔLL(L − line) 1.5 [-1.1, 4.6] nats; ΔLL(L − power) 1.2 [-1.0, 3.5]; ΔLL(power − line) 0.3 [-4.0, 3.3]. Card's pooled-amplitude form: ΔLL(L − line) -1.4 [-5.1, 2.0].
  - Fits: ĉ 0.141 [0.020, 0.686], n̂_sat 21.34 [4.375, 150.000] (grid-edge share 0.11); power p̂ 0.80 [0.524, 1.250].
  - Nuisance pulls: newest item 0.0189 [0.0061, 0.0325]; named count -0.0001 [-0.0168, 0.0134] per aligned named item.
  - O4: ĝ(1) 0.040 [0.010, 0.071], ĝ(1)/f̂(1) 1.816, read − in-flight at n = 1 -0.018 [-0.055, 0.016]. O5: largest n with ≥ 50 rows 6.
  - Rules: P1 fail, P2 fail, P3 fail, P4 fail; kill (linear curve) True, kill (line as good) True (not applied: unscored); verdict by the card's rule: **descriptive**.

## Scorecard (period-specific axes)
Descriptive (not scored: H113 identification, the 200-row count or power < 0.8). C, D, F, H: 0.
