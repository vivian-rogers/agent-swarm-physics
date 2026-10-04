# H59 × G38: regime-III two-room period (2026-04-02 → 04-24)

**Verdict:** failed
**Role:** replication
**Period:** regime III · 14 agents · two rooms · 17 days. Nudger on.

## Why this period
The second-largest nudge sample (109 receiving calls) and 2,437 mention reads, in a different goal and room setup from #51.

## Prediction
*Templated from the card (P6, written 2026-10-04 before any outcome fit).* Powered classes N, Hu, A: T ≥ 0.8 and S_H59 CI > 0 each; failed if any has T < 0.5 with S_free − S_H59 CI > 0.

## Result
`data/processed/H59-one-lever-model/G38/results.json`, `loco_split.json`.

| Class (reads) | κ | h | d | S_delay / S_H59 / S_dir / S_free | T | Cell |
| --- | --- | --- | --- | --- | --- | --- |
| N (109) | −0.77 [−1.54, 0.54] | 3.95 [1.97, 7.91] | 64 s | 2.5 / 2.0 / 17.7 / 16.8 | 0.12; free − H59 [0.1, 26.8] | **fail** |
| Hu (85) | 0.36 [−0.88, 1.63] | 4.41 [1.65, 5.27] | 58 s | 6.9 / 4.4 / 4.6 / 5.7 | 0.77 | uninformative |
| A (2,437) | −0.05 [−0.39, 0.64] | 3.56 [1.99, 4.78] | 15 s | −94 / 19 / 43 / 46 | 0.41 | uninformative (S_free CI includes 0) |

- θ = 59° [42, 69]; K = 1, 0.65, 0.30, 0.08, 0.03, 0.03 (K₁ = 0.65 > 0.5: a lag-1 response, against P3).
- **The nudge needs its own direction:** R_dir (θ_N free) recovers all of R_free's skill (17.7 vs 16.8) at the read-out. A mention borrowing its shape from N + Hu loses half (early rows: 21 vs 55; R_dir 44). So in G38 the classes differ in *direction*, which a single θ cannot carry.
- Mention reads lose half their effect when stale (0.52 [0.28, 0.75]), unlike G51.

## Scorecard (period-specific axes)
C 1 · D 0 · H 0 (R_dir wins) · I 0.

## Notes
- The synthetic showed that G38 scale is marginal: in the one-lever world, A reached T ≥ 0.8 in 1 of 2 replicates.
