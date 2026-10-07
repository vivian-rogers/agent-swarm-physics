# H142 × G16: free week with operator rules (2025-10-06 → 2025-10-10)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime I · one room · 7 agents · 5 days. Units from `period_units`.

## Why this period
Field-identified by H113 in gte only (b̂ 0.79 gte). Short and small: likely few rows with n_u ≥ 4.

## Prediction
*Written 2026-10-07 ~13:20 UTC by the round-1 agent, before running on this period (copied from the card's replication layer, as the card's "Results by goal period" note asks). Seen: H113's numbers for this period; no aligned count, cluster assignment or directional step.*
- **P1:** ΔLL(Langevin − linear) > 0 with CI above 0. Credence 0.35.
- **P2:** Δ_curv > 0 with CI above 0. Credence 0.25.
- **P3:** n̂_sat ∈ [1.5, 6]. Credence 0.3.
- **P4:** ĝ(1)/f̂(1) ≤ 0.5 and read − in-flight contrast at n = 1 > 0. Credence 0.6.
- Counts against: the card's kill on this period, if the synthetic power against W-L3 is ≥ 0.8 here. Below 200 rows with n_u ≥ 4 or power < 0.8, the period reports a descriptive shape only.

## Result
*Round 1, 2026-10-07 (exploratory). Amendments A1–A4 in the card apply. Figure: `figures/step_curve.pdf`.*
- **bge** (15,112 rows, 383 with n_u ≥ 4, 5 days; power vs W-L3 0.91; scored: no).
  - O1 step curve: f̂(1) -0.0009 [-0.0106, 0.0082], f̂(2) 0.0180 [-0.0045, 0.0389], f̂(3) 0.0193 [-0.0106, 0.0467], f̂(4–5) -0.0038 [-0.0297, 0.0227], f̂(6+) 0.0078 [-0.0292, 0.0406].
  - O2 Δ_curv undefined (a bin ≤ 0). f̂(6+)/f̂(3) 0.405 [-3.980, 6.260].
  - O3 out of fold (A1 form): ΔLL(L − line) -1.1 [-5.7, 3.3] nats; ΔLL(L − power) 1.2 [-5.1, 10.0]; ΔLL(power − line) -2.4 [-6.7, 2.2]. Card's pooled-amplitude form: ΔLL(L − line) 1.8 [-5.1, 9.1].
  - Fits: ĉ 0.292 [0.020, 30.000], n̂_sat 10.27 [0.100, 150.000] (grid-edge share 0.21); power p̂ 1.50 [0.050, 1.500].
  - Nuisance pulls: newest item 0.0229 [0.0061, 0.0427]; named count -0.0012 [-0.0039, 0.0055] per aligned named item.
  - O4: ĝ(1) 0.021 [0.004, 0.038], ĝ(1)/f̂(1) undefined (f̂(1) CI includes 0), read − in-flight at n = 1 -0.022 [-0.045, 0.000]. O5: largest n with ≥ 50 rows 5.
  - Rules: P1 fail, P2 fail, P3 fail, P4 fail; kill (linear curve) True, kill (line as good) True (not applied: unscored); verdict by the card's rule: **descriptive**.
- **gte** (15,112 rows, 380 with n_u ≥ 4, 5 days; power vs W-L3 0.87; scored: yes).
  - O1 step curve: f̂(1) 0.0047 [-0.0040, 0.0129], f̂(2) -0.0006 [-0.0156, 0.0120], f̂(3) 0.0147 [-0.0149, 0.0411], f̂(4–5) 0.0198 [-0.0014, 0.0395], f̂(6+) -0.0111 [-0.0467, 0.0214].
  - O2 Δ_curv undefined (a bin ≤ 0). f̂(6+)/f̂(3) -0.753 [-10.759, 8.499].
  - O3 out of fold (A1 form): ΔLL(L − line) 8.4 [3.9, 14.3] nats; ΔLL(L − power) 0.9 [-0.7, 2.6]; ΔLL(power − line) 7.6 [4.6, 11.7]. Card's pooled-amplitude form: ΔLL(L − line) -0.7 [-5.1, 2.3].
  - Fits: ĉ 1.425 [0.098, 1.425], n̂_sat 2.11 [2.106, 30.757] (grid-edge share 0.01); power p̂ 0.30 [0.250, 1.500].
  - Nuisance pulls: newest item 0.0268 [0.0138, 0.0388]; named count 0.0011 [-0.0019, 0.0052] per aligned named item.
  - O4: ĝ(1) 0.000 [-0.017, 0.016], ĝ(1)/f̂(1) undefined (f̂(1) CI includes 0), read − in-flight at n = 1 0.005 [-0.014, 0.026]. O5: largest n with ≥ 50 rows 5.
  - Rules: P1 pass, P2 fail, P3 pass, P4 fail; kill (linear curve) True, kill (line as good) False; verdict by the card's rule: **failed**.

## Scorecard (period-specific axes)
C 0 (the Langevin form does not beat the line out of fold); D 0 (no unfitted signature: Δ_curv undefined); F 2 (power vs W-L3 ≥ 0.8 on this skeleton; W-lin size ≤ 0.12); H 0 (does not beat the line or the power law).
