# H142 × G38: the long shared week (#38, 2026-04-02 → 2026-04-27)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime III · mode C · 12 agents · two rooms (#best / #rest, room-specific kickoffs) · 17 days. Units from `period_units`.

## Why this period
Field-identified by H113 in both embedding models, with large batches in regime III and 17 days of talk calls, so rows with n_u ≥ 4 are likely. H113's information per call here rises and then falls with k (1.07 → 1.70 → 1.13 bits), a hint of saturation that a per-direction curve can test at fixed k.

## Prediction
*Written 2026-10-07 ~12:30 UTC, before running on this period. Seen: H113's #38 numbers; no aligned count or directional step.*
- **P1:** ΔLL(Langevin − linear) > 0 with CI above 0. Credence 0.35.
- **P2:** Δ_curv > 0 with CI above 0. Credence 0.25.
- **P3:** n̂_sat ∈ [1.5, 6]. Credence 0.3.
- **P4:** ĝ(1)/f̂(1) ≤ 0.5 and read − in-flight contrast at n = 1 > 0. Credence 0.6.
- Counts against: the card's kill on this period, if the synthetic power against W-L3 is ≥ 0.8 here.

## Result
*Round 1, 2026-10-07 (exploratory). Amendments A1–A4 in the card apply. Figure: `figures/step_curve.pdf`.*
- **bge** (34,944 rows, 552 with n_u ≥ 4, 17 days; power vs W-L3 0.99; scored: yes).
  - O1 step curve: f̂(1) 0.0036 [-0.0050, 0.0121], f̂(2) 0.0082 [-0.0062, 0.0237], f̂(3) 0.0004 [-0.0260, 0.0239], f̂(4–5) 0.0053 [-0.0212, 0.0324], f̂(6+) 0.0207 [-0.0103, 0.0509].
  - O2 Δ_curv -3.04 [—, —]. f̂(6+)/f̂(3) 47.345 [-12.237, 17.236].
  - O3 out of fold (A1 form): ΔLL(L − line) -5.1 [-12.1, 0.9] nats; ΔLL(L − power) -4.0 [-6.1, -2.0]; ΔLL(power − line) -1.1 [-7.2, 4.2]. Card's pooled-amplitude form: ΔLL(L − line) -1.9 [-4.4, -0.4].
  - Fits: ĉ 0.229 [0.020, 30.000], n̂_sat 13.10 [0.100, 150.000] (grid-edge share 0.42); power p̂ 0.55 [0.050, 1.500].
  - Nuisance pulls: newest item 0.0194 [0.0081, 0.0309]; named count 0.0039 [-0.0050, 0.0137] per aligned named item.
  - O4: ĝ(1) 0.017 [-0.004, 0.040], ĝ(1)/f̂(1) undefined (f̂(1) CI includes 0), read − in-flight at n = 1 -0.014 [-0.039, 0.009]. O5: largest n with ≥ 50 rows 6.
  - Rules: P1 fail, P2 fail, P3 fail, P4 fail; kill (linear curve) True, kill (line as good) True; verdict by the card's rule: **failed**.
  - Sensitivity (K = 12): ΔLL(L − line) -0.8 [-2.4, 0.0], Δ_curv — [—, —], n̂_sat 150.00.
  - Sensitivity (copies and templates removed): ΔLL(L − line) -1.8 [-5.5, 1.2], Δ_curv -1.180 [—, —], n̂_sat 14.80.
  - Within room × hour permutation null (50 perms, bge): ΔLL(L − line) 2.5/50/97.5% -6.4, -0.8, 4.2; f̂(1) -0.0092, 0.0005, 0.0087.
- **gte** (34,944 rows, 578 with n_u ≥ 4, 17 days; power vs W-L3 0.93; scored: yes).
  - O1 step curve: f̂(1) -0.0005 [-0.0088, 0.0076], f̂(2) -0.0040 [-0.0173, 0.0102], f̂(3) 0.0195 [-0.0025, 0.0409], f̂(4–5) -0.0148 [-0.0408, 0.0090], f̂(6+) -0.0345 [-0.0666, 0.0008].
  - O2 Δ_curv undefined (a bin ≤ 0). f̂(6+)/f̂(3) -1.770 [-19.609, 4.137].
  - O3 out of fold (A1 form): ΔLL(L − line) -6.8 [-10.9, -2.9] nats; ΔLL(L − power) -0.3 [-2.0, 1.4]; ΔLL(power − line) -6.5 [-10.4, -2.7]. Card's pooled-amplitude form: ΔLL(L − line) -0.6 [-1.6, 0.1].
  - Fits: ĉ 0.110 [0.020, 30.000], n̂_sat 27.23 [0.100, 150.000] (grid-edge share 0.56); power p̂ 0.85 [0.050, 1.500].
  - Nuisance pulls: newest item 0.0196 [0.0063, 0.0316]; named count 0.0093 [-0.0003, 0.0184] per aligned named item.
  - O4: ĝ(1) 0.029 [0.003, 0.054], ĝ(1)/f̂(1) undefined (f̂(1) CI includes 0), read − in-flight at n = 1 -0.029 [-0.058, -0.002]. O5: largest n with ≥ 50 rows 6.
  - Rules: P1 fail, P2 fail, P3 fail, P4 fail; kill (linear curve) True, kill (line as good) True; verdict by the card's rule: **failed**.
- *Post hoc* (bge, raw): f̂(1) 0.0055 [-0.0013, 0.0146], newest 0.0163, ΔLL(L − line) -3.8 [-8.0, -0.0].
- *Post hoc* (bge, day): f̂(1) 0.0038 [-0.0029, 0.0120], newest 0.0210, ΔLL(L − line) -4.2 [-11.3, 1.1].
- *Post hoc* (bge, raw+day): f̂(1) 0.0096 [0.0026, 0.0186], newest 0.0204, ΔLL(L − line) 8.4 [0.2, 18.2].

## Scorecard (period-specific axes)
C 0 (the Langevin form does not beat the line out of fold); D 0 (no unfitted signature: Δ_curv undefined); F 2 (power vs W-L3 ≥ 0.8 on this skeleton; W-lin size ≤ 0.12); H 0 (does not beat the line or the power law).

## Notes
- Direction × room × hour effects use the reader's room; room-kickoff directions are projected out per room.
