# H59 × G04: public-chat era, regime I (2025-05-15 → 06-18)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 4–6 agents · #general (public, up to 124 human speakers) · 25 days. No nudges.

## Why this period
The densest human input with enough days: 4,627 broadcast-human reads, 324 named-human reads and 2,752 mention reads. Here the human classes are read in every state, so LOCO tests the shared direction (A1).

## Prediction
*Templated from the card (P6, written 2026-10-04 before any outcome fit).* Hu, Hm, A: T ≥ 0.8 and S_H59 CI > 0.

## Result
`data/processed/H59-one-lever-model/G04/results.json`, `loco_split.json`.

| Class (reads) | κ | h | d | S_delay / S_H59 / S_dir / S_free | T | Cell |
| --- | --- | --- | --- | --- | --- | --- |
| Hu (4,627) | 0.18 [0.08, 0.26] | 1.81 [1.37, 2.46] | 12 s | 159 / 218 / 215 / 293 | 0.75; free − H59 [49, 101] | mixed |
| Hm (324) | 0.42 [0.28, 0.58] | 1.85 [1.13, 3.15] | 11 s | 24 / 26 / 27 / 44 | 0.59 | mixed |
| A (2,752) | −0.07 [−0.21, 0.08] | 0.51 [0.18, 0.79] | 11 s | −76 / 3 / 3 / 57 | 0.06; free − H59 [35, 76] | **fail** |

- θ = 88.5° [72, 119] (toward talk); K = 1, −0.05, −0.32, −0.17, −0.06, −0.05: a rebound after the read-out.
- **Human classes transfer at the read-out** (post hoc early rows: Hu 0.84, Hm 1.0 of the free fit) but not in the tail.
- **Mentions fail everywhere:** a regime-I mention mostly speeds up the work ↔ wait edge (free fit, lag 0: W→I +1.85, I→W +0.72). That is an edge-specific catalyst; neither a uniform κ nor a talk-directed field can represent it (R_dir does not help: 3.4).
- R_delay is rejected for Hu and A (H59 − delay [34, 86], [55, 103]).

## Scorecard (period-specific axes)
C 1 · D 1 (humans at the read-out) · H 1 (beats R_delay; loses to R_free) · I 0.

## Notes
- Regime I has few idle calls (646 transitions from I); "idle" here is a wait call.
