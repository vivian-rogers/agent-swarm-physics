# H142 × G39: build your own interactive world (2026-04-27 → 2026-05-01)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime III · two rooms · 15 agents · 5 days. Also the first side of NE42. Units from `period_units`.

## Why this period
Field-identified by H113 in bge (b̂ 0.81 [0.65, 0.96]). Also the pre-merge side of NE42 (native N2).

## Prediction
*Written 2026-10-07 ~13:20 UTC by the round-1 agent, before running on this period (copied from the card's replication layer, as the card's "Results by goal period" note asks). Seen: H113's numbers for this period; no aligned count, cluster assignment or directional step.*
- **P1:** ΔLL(Langevin − linear) > 0 with CI above 0. Credence 0.35.
- **P2:** Δ_curv > 0 with CI above 0. Credence 0.25.
- **P3:** n̂_sat ∈ [1.5, 6]. Credence 0.3.
- **P4:** ĝ(1)/f̂(1) ≤ 0.5 and read − in-flight contrast at n = 1 > 0. Credence 0.6.
- Counts against: the card's kill on this period, if the synthetic power against W-L3 is ≥ 0.8 here. Below 200 rows with n_u ≥ 4 or power < 0.8, the period reports a descriptive shape only.

## Result
*Round 1, 2026-10-07 (exploratory). Amendments A1–A4 in the card apply. Figure: `figures/step_curve.pdf`.*
- **bge** (6,360 rows, 210 with n_u ≥ 4, 5 days; power vs W-L3 0.47; scored: no).
  - O1 step curve: f̂(1) -0.0109 [-0.0227, -0.0002], f̂(2) -0.0037 [-0.0287, 0.0216], f̂(3) -0.0266 [-0.0619, 0.0038], f̂(4–5) 0.0199 [-0.0152, 0.0550], f̂(6+) -0.0318 [-0.0729, 0.0154].
  - O2 Δ_curv undefined (a bin ≤ 0). f̂(6+)/f̂(3) 1.195 [-3.796, 9.559].
  - O3 out of fold (A1 form): ΔLL(L − line) 0.1 [0.0, 0.3] nats; ΔLL(L − power) 6.2 [-4.0, 24.1]; ΔLL(power − line) -6.1 [-23.8, 4.0]. Card's pooled-amplitude form: ΔLL(L − line) -2.3 [-5.1, 0.2].
  - Fits: ĉ 0.020 [0.020, 30.000], n̂_sat 150.00 [0.100, 150.000] (grid-edge share 0.97); power p̂ 1.50 [0.050, 1.500].
  - Nuisance pulls: newest item 0.0201 [0.0027, 0.0398]; named count 0.0296 [0.0124, 0.0526] per aligned named item.
  - O4: ĝ(1) -0.005 [-0.041, 0.030], ĝ(1)/f̂(1) undefined (f̂(1) CI includes 0), read − in-flight at n = 1 -0.005 [-0.043, 0.032]. O5: largest n with ≥ 50 rows 4.
  - Rules: P1 pass, P2 fail, P3 fail, P4 fail; kill (linear curve) True, kill (line as good) False (not applied: unscored); verdict by the card's rule: **descriptive**.
  - Sensitivity (K = 12): ΔLL(L − line) 0.0 [-0.0, 0.1], Δ_curv — [—, —], n̂_sat 150.00.
  - Sensitivity (copies and templates removed): ΔLL(L − line) -0.3 [-0.9, 0.1], Δ_curv — [—, —], n̂_sat 24.10.
  - Within room × hour permutation null (50 perms, bge): ΔLL(L − line) 2.5/50/97.5% -12.4, 0.2, 16.3; f̂(1) -0.0126, 0.0003, 0.0103.
- **gte** (6,360 rows, 164 with n_u ≥ 4, 5 days; power vs W-L3 0.64; scored: no).
  - O1 step curve: f̂(1) -0.0023 [-0.0128, 0.0088], f̂(2) -0.0150 [-0.0358, 0.0042], f̂(3) -0.0127 [-0.0404, 0.0159], f̂(4–5) 0.0232 [-0.0100, 0.0673], f̂(6+) -0.0580 [-0.1006, -0.0177].
  - O2 Δ_curv undefined (a bin ≤ 0). f̂(6+)/f̂(3) 4.567 [-25.568, 31.957].
  - O3 out of fold (A1 form): ΔLL(L − line) -0.0 [-3.0, 3.9] nats; ΔLL(L − power) 93.3 [-6.4, 288.8]; ΔLL(power − line) -93.3 [-285.9, 4.4]. Card's pooled-amplitude form: ΔLL(L − line) -2.3 [-6.1, 0.5].
  - Fits: ĉ 0.141 [0.020, 30.000], n̂_sat 21.34 [0.100, 150.000] (grid-edge share 0.43); power p̂ 1.50 [0.050, 1.500].
  - Nuisance pulls: newest item 0.0230 [0.0096, 0.0395]; named count 0.0205 [0.0050, 0.0476] per aligned named item.
  - O4: ĝ(1) 0.005 [-0.028, 0.030], ĝ(1)/f̂(1) undefined (f̂(1) CI includes 0), read − in-flight at n = 1 -0.007 [-0.032, 0.029]. O5: largest n with ≥ 50 rows 4.
  - Rules: P1 fail, P2 fail, P3 fail, P4 fail; kill (linear curve) True, kill (line as good) True (not applied: unscored); verdict by the card's rule: **descriptive**.

## Scorecard (period-specific axes)
Descriptive (not scored: H113 identification, the 200-row count or power < 0.8). C, D, F, H: 0.
