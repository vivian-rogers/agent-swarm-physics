# H142 × G13: human-subjects experiment (2025-09-08 → 2025-09-19)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime I · one room · 6 agents · 10 days. Units from `period_units`.

## Why this period
Field-identified by H113 in both models (b̂ 0.67 [0.60, 0.75] bge). Regime I batches are small, so few rows with n_u ≥ 4 are expected.

## Prediction
*Written 2026-10-07 ~13:20 UTC by the round-1 agent, before running on this period (copied from the card's replication layer, as the card's "Results by goal period" note asks). Seen: H113's numbers for this period; no aligned count, cluster assignment or directional step.*
- **P1:** ΔLL(Langevin − linear) > 0 with CI above 0. Credence 0.35.
- **P2:** Δ_curv > 0 with CI above 0. Credence 0.25.
- **P3:** n̂_sat ∈ [1.5, 6]. Credence 0.3.
- **P4:** ĝ(1)/f̂(1) ≤ 0.5 and read − in-flight contrast at n = 1 > 0. Credence 0.6.
- Counts against: the card's kill on this period, if the synthetic power against W-L3 is ≥ 0.8 here. Below 200 rows with n_u ≥ 4 or power < 0.8, the period reports a descriptive shape only.

## Result
*Round 1, 2026-10-07 (exploratory). Amendments A1–A4 in the card apply. Figure: `figures/step_curve.pdf`.*
- **bge** (36,056 rows, 909 with n_u ≥ 4, 10 days; power vs W-L3 1.0; scored: yes).
  - O1 step curve: f̂(1) 0.0056 [-0.0019, 0.0136], f̂(2) -0.0048 [-0.0146, 0.0050], f̂(3) -0.0145 [-0.0303, -0.0011], f̂(4–5) -0.0089 [-0.0267, 0.0102], f̂(6+) -0.0175 [-0.0429, 0.0084].
  - O2 Δ_curv undefined (a bin ≤ 0). f̂(6+)/f̂(3) 1.200 [-0.798, 5.974].
  - O3 out of fold (A1 form): ΔLL(L − line) -3.2 [-8.1, 0.3] nats; ΔLL(L − power) 0.4 [-4.9, 4.8]; ΔLL(power − line) -3.6 [-5.4, -1.8]. Card's pooled-amplitude form: ΔLL(L − line) -0.0 [-0.1, 0.0].
  - Fits: ĉ 0.159 [0.020, 30.000], n̂_sat 18.89 [0.100, 150.000] (grid-edge share 0.19); power p̂ 1.05 [0.050, 1.500].
  - Nuisance pulls: newest item 0.0106 [0.0002, 0.0203]; named count 0.0017 [-0.0069, 0.0083] per aligned named item.
  - O4: ĝ(1) 0.003 [-0.006, 0.014], ĝ(1)/f̂(1) undefined (f̂(1) CI includes 0), read − in-flight at n = 1 0.002 [-0.012, 0.014]. O5: largest n with ≥ 50 rows 9.
  - Rules: P1 fail, P2 fail, P3 fail, P4 fail; kill (linear curve) True, kill (line as good) True; verdict by the card's rule: **failed**.
  - Sensitivity (K = 12): ΔLL(L − line) -1.5 [-3.9, 0.1], Δ_curv — [—, —], n̂_sat 24.10.
  - Sensitivity (copies and templates removed): ΔLL(L − line) -2.2 [-5.2, 0.1], Δ_curv — [—, —], n̂_sat 21.34.
  - Within room × hour permutation null (50 perms, bge): ΔLL(L − line) 2.5/50/97.5% -7.2, -1.3, 10.0; f̂(1) -0.0068, 0.0008, 0.0056.
- **gte** (36,056 rows, 1,051 with n_u ≥ 4, 10 days; power vs W-L3 1.0; scored: yes).
  - O1 step curve: f̂(1) 0.0011 [-0.0064, 0.0106], f̂(2) -0.0055 [-0.0165, 0.0048], f̂(3) -0.0143 [-0.0329, 0.0004], f̂(4–5) -0.0167 [-0.0355, -0.0039], f̂(6+) -0.0175 [-0.0395, 0.0043].
  - O2 Δ_curv undefined (a bin ≤ 0). f̂(6+)/f̂(3) 1.226 [-0.953, 8.614].
  - O3 out of fold (A1 form): ΔLL(L − line) -1.3 [-3.1, 0.0] nats; ΔLL(L − power) -0.0 [-1.7, 1.4]; ΔLL(power − line) -1.3 [-2.0, -0.6]. Card's pooled-amplitude form: ΔLL(L − line) -3.1 [-6.8, -0.4].
  - Fits: ĉ 0.020 [0.020, 2.320], n̂_sat 150.00 [1.293, 150.000] (grid-edge share 0.49); power p̂ 0.85 [0.274, 1.500].
  - Nuisance pulls: newest item 0.0078 [-0.0023, 0.0163]; named count 0.0031 [-0.0026, 0.0100] per aligned named item.
  - O4: ĝ(1) -0.009 [-0.017, -0.001], ĝ(1)/f̂(1) undefined (f̂(1) CI includes 0), read − in-flight at n = 1 0.010 [-0.003, 0.024]. O5: largest n with ≥ 50 rows 8.
  - Rules: P1 fail, P2 fail, P3 fail, P4 fail; kill (linear curve) True, kill (line as good) True; verdict by the card's rule: **failed**.
- *Post hoc* (bge, raw): f̂(1) -0.0012 [-0.0100, 0.0078], newest 0.0088, ΔLL(L − line) -4.1 [-9.6, -0.3].
- *Post hoc* (bge, day): f̂(1) 0.0067 [-0.0008, 0.0157], newest 0.0113, ΔLL(L − line) -3.8 [-9.4, 0.3].
- *Post hoc* (bge, raw+day): f̂(1) 0.0026 [-0.0061, 0.0119], newest 0.0101, ΔLL(L − line) -4.8 [-9.9, -0.2].

## Scorecard (period-specific axes)
C 0 (the Langevin form does not beat the line out of fold); D 0 (no unfitted signature: Δ_curv undefined); F 2 (power vs W-L3 ≥ 0.8 on this skeleton; W-lin size ≤ 0.12); H 0 (does not beat the line or the power law).
