# H142 × G51: private roles and timer wakes (#51 main body, units 51a–51l)

**Verdict:** failed
**Role:** exploratory (replication + native N1)
**Period:** regime III · mode I/K (private roles) · up to 21 agents · #general (and #focus from 08-05) · non-reserved days 2026-07-06 → 2026-09-04. The tail (2026-09-07 → 09-21) is reserved and not used.

## Why this period
The largest batches (k ≥ 17 is common: H113's top bin) and the only period with timer wakes, where the batch is set by others while the reader sleeps (H18's design D2: dilution 0.50 [0.45, 0.56]; H113: a_U 0.31 [0.25, 0.37]). Named pulls are measured here (H29: 0.03–0.09 vs 0.009–0.021 of the gap per message).

## Prediction
*Written 2026-10-07 ~12:30 UTC, before running on this period. Seen: H113's, H18's and H29's #51 numbers; no aligned count or directional step.*
- **P1 (talk calls):** ΔLL(Langevin − linear) > 0 with CI above 0. Credence 0.35.
- **N1 (timer wakes):** ΔLL(Langevin − linear) > 0 with CI, and n̂_sat(wakes) within ×1.5 of n̂_sat(talk). Credence 0.3.
- **P2:** Δ_curv > 0 with CI above 0. Credence 0.25.
- Counts against: the kill (linear curve or line as good out of fold), with power ≥ 0.8.

## Result
*Round 1, 2026-10-07 (exploratory). Amendments A1–A4 in the card apply. Figure: `figures/step_curve.pdf`.*
- **bge** (318,856 rows, 30,758 with n_u ≥ 4, 45 days; power vs W-L3 1.0; scored: yes).
  - O1 step curve: f̂(1) -0.0000 [-0.0022, 0.0023], f̂(2) -0.0029 [-0.0064, 0.0005], f̂(3) -0.0071 [-0.0113, -0.0026], f̂(4–5) -0.0066 [-0.0112, -0.0020], f̂(6+) -0.0104 [-0.0161, -0.0047].
  - O2 Δ_curv undefined (a bin ≤ 0). f̂(6+)/f̂(3) 1.472 [0.761, 2.952].
  - O3 out of fold (A1 form): ΔLL(L − line) -0.7 [-2.0, 0.5] nats; ΔLL(L − power) 1.2 [-1.1, 3.6]; ΔLL(power − line) -1.9 [-4.4, 0.5]. Card's pooled-amplitude form: ΔLL(L − line) 2.5 [-7.0, 11.2].
  - Fits: ĉ 0.020 [0.020, 30.000], n̂_sat 150.00 [0.100, 150.000] (grid-edge share 0.71); power p̂ 0.75 [0.050, 1.500].
  - Nuisance pulls: newest item 0.0103 [0.0074, 0.0137]; named count 0.0026 [-0.0007, 0.0060] per aligned named item.
  - O4: ĝ(1) 0.003 [-0.002, 0.008], ĝ(1)/f̂(1) undefined (f̂(1) CI includes 0), read − in-flight at n = 1 -0.003 [-0.009, 0.003]. O5: largest n with ≥ 50 rows 36.
  - Rules: P1 fail, P2 fail, P3 fail, P4 fail; kill (linear curve) True, kill (line as good) True; verdict by the card's rule: **failed**.
  - Sensitivity (K = 12): ΔLL(L − line) -4.1 [-9.9, 0.1], Δ_curv — [—, —], n̂_sat 150.00.
  - Sensitivity (copies and templates removed): ΔLL(L − line) -0.7 [-2.0, 0.5], Δ_curv — [—, —], n̂_sat 150.00.
  - Within room × hour permutation null (25 perms, bge): ΔLL(L − line) 2.5/50/97.5% -14.9, -0.7, 4.8; f̂(1) -0.0009, 0.0002, 0.0016.
- **gte** (318,856 rows, 28,953 with n_u ≥ 4, 45 days; power vs W-L3 1.0; scored: yes).
  - O1 step curve: f̂(1) 0.0002 [-0.0022, 0.0023], f̂(2) -0.0012 [-0.0047, 0.0016], f̂(3) 0.0018 [-0.0035, 0.0069], f̂(4–5) -0.0031 [-0.0084, 0.0013], f̂(6+) -0.0112 [-0.0160, -0.0057].
  - O2 Δ_curv undefined (a bin ≤ 0). f̂(6+)/f̂(3) -6.189 [-59.849, 93.041].
  - O3 out of fold (A1 form): ΔLL(L − line) 5.7 [-1.8, 11.7] nats; ΔLL(L − power) 3.6 [-1.6, 8.0]; ΔLL(power − line) 2.1 [-3.1, 7.0]. Card's pooled-amplitude form: ΔLL(L − line) 6.0 [-1.0, 12.5].
  - Fits: ĉ 0.159 [0.020, 0.508], n̂_sat 18.89 [5.927, 150.000] (grid-edge share 0.07); power p̂ 0.60 [0.200, 1.476].
  - Nuisance pulls: newest item 0.0127 [0.0096, 0.0158]; named count 0.0107 [0.0077, 0.0140] per aligned named item.
  - O4: ĝ(1) 0.002 [-0.003, 0.007], ĝ(1)/f̂(1) undefined (f̂(1) CI includes 0), read − in-flight at n = 1 -0.002 [-0.008, 0.003]. O5: largest n with ≥ 50 rows 35.
  - Rules: P1 fail, P2 fail, P3 fail, P4 fail; kill (linear curve) True, kill (line as good) True; verdict by the card's rule: **failed**.
- **N1 timer wakes (bge)**:
    - O1 step curve: f̂(1) 0.0047 [-0.0006, 0.0103], f̂(2) 0.0043 [-0.0049, 0.0148], f̂(3) 0.0106 [-0.0037, 0.0232], f̂(4–5) 0.0027 [-0.0096, 0.0158], f̂(6+) 0.0171 [-0.0023, 0.0341].
    - O2 Δ_curv -0.58 [-3.792, 2.666]. f̂(6+)/f̂(3) 1.617 [-16.585, 13.590].
    - O3 out of fold (A1 form): ΔLL(L − line) -5.3 [-13.3, 1.0] nats; ΔLL(L − power) -2.6 [-6.5, 1.7]; ΔLL(power − line) -2.7 [-9.0, 2.5]. Card's pooled-amplitude form: ΔLL(L − line) -3.5 [-7.8, -0.2].
    - Fits: ĉ 2.320 [0.020, 30.000], n̂_sat 1.29 [0.100, 150.000] (grid-edge share 0.35); power p̂ 0.60 [0.050, 1.500].
    - Nuisance pulls: newest item 0.0094 [0.0019, 0.0174]; named count 0.0044 [-0.0027, 0.0122] per aligned named item.
    - O4: ĝ(1) -0.001 [-0.010, 0.007], ĝ(1)/f̂(1) undefined (f̂(1) CI includes 0), read − in-flight at n = 1 0.006 [-0.005, 0.016]. O5: largest n with ≥ 50 rows 11.
  - N1: ΔLL CI > 0: False; n̂_sat(wakes)/n̂_sat(talk) 0.01 (ln ratio CI [-7.31, 4.64]); within ×1.5: False; **N1 fail**.
- **N1 timer wakes (gte)**:
    - O1 step curve: f̂(1) 0.0029 [-0.0021, 0.0085], f̂(2) 0.0033 [-0.0056, 0.0111], f̂(3) 0.0075 [-0.0051, 0.0208], f̂(4–5) -0.0025 [-0.0175, 0.0113], f̂(6+) 0.0233 [0.0043, 0.0409].
    - O2 Δ_curv -1.02 [-4.334, 2.076]. f̂(6+)/f̂(3) 3.094 [-33.756, 24.670].
    - O3 out of fold (A1 form): ΔLL(L − line) -7.4 [-18.7, 0.1] nats; ΔLL(L − power) 2.5 [-6.1, 13.5]; ΔLL(power − line) -9.9 [-23.0, 0.1]. Card's pooled-amplitude form: ΔLL(L − line) 0.0 [-0.6, 0.7].
    - Fits: ĉ 0.026 [0.020, 30.000], n̂_sat 117.55 [0.100, 150.000] (grid-edge share 0.53); power p̂ 1.50 [0.050, 1.500].
    - Nuisance pulls: newest item 0.0106 [0.0022, 0.0188]; named count 0.0129 [0.0058, 0.0201] per aligned named item.
    - O4: ĝ(1) 0.011 [0.003, 0.018], ĝ(1)/f̂(1) undefined (f̂(1) CI includes 0), read − in-flight at n = 1 -0.008 [-0.018, 0.002]. O5: largest n with ≥ 50 rows 11.
  - N1: ΔLL CI > 0: False; n̂_sat(wakes)/n̂_sat(talk) 6.22 (ln ratio CI [-6.65, 2.87]); within ×1.5: False; **N1 fail**.
- *Post hoc* (bge, raw): f̂(1) -0.0014 [-0.0039, 0.0011], newest 0.0082, ΔLL(L − line) -1.7 [-5.2, 0.6].
- *Post hoc* (bge, day): f̂(1) 0.0023 [0.0000, 0.0044], newest 0.0111, ΔLL(L − line) -2.3 [-5.9, 0.3].
- *Post hoc* (bge, raw+day): f̂(1) 0.0062 [0.0038, 0.0088], newest 0.0112, ΔLL(L − line) -0.8 [-2.3, 0.4].
- *Post hoc* (gte, raw): f̂(1) -0.0035 [-0.0059, -0.0010], newest 0.0137, ΔLL(L − line) 2.8 [-7.2, 11.8].
- *Post hoc* (gte, day): f̂(1) 0.0022 [-0.0000, 0.0046], newest 0.0134, ΔLL(L − line) 4.6 [-1.1, 10.2].
- *Post hoc* (gte, raw+day): f̂(1) 0.0037 [0.0014, 0.0064], newest 0.0158, ΔLL(L − line) 4.7 [-2.8, 11.8].

## Scorecard (period-specific axes)
C 0 (the Langevin form does not beat the line out of fold); D 0 (no unfitted signature: Δ_curv undefined); F 2 (power vs W-L3 ≥ 0.8 on this skeleton; W-lin size ≤ 0.12); H 0 (does not beat the line or the power law).

## Notes
- The named count n^name_{c,u} is in the model; H29's 3–6× named pull would otherwise mimic a curve if named items cluster at low n.
