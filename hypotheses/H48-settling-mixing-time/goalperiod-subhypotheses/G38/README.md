# H48 × G38: Charity fundraiser, year 2 (2026-04-02 → 04-24)

**Verdict:** failed
**Role:** native
**Period:** regime III · shared objective, two rooms with room kickoffs (#best 4, #rest 8 at the kickoff) · N 12 → 14 · 17 active days (68.6 active h). Steps inside: NE36 (misinformation removed at the kickoff), NE17 (04-14), NE18 (04-20), two joins (38c, 38e). Not held out.

## Why this period
The longest regime-III two-room period, and the one where H20 found its strongest kickoff relaxation (lag-1 correlation 0.66 → 0.87 over four active days). Agents differ a lot in how fast they read their room-mates (direct coverage T90 for the period is ~11 active h, against ≤ 1 h in most periods, because a few agents post rarely), so H48 can be tested *within* one period: agents who finish reading their room-mates later should settle later. The room contrast (#best 4 agents vs #rest 8) adds a second, within-period comparison with the same goal.

## Prediction
*Written 2026-10-04 ~07:10 UTC, before running settling on this period.*
- **N2a (primary, per agent):** Spearman over agents (day-1 roster, detected per-agent S1 settling, 2-active-hour bins) between τ_i and agent i's own coverage time T_i (the time i has read ≥ 1 post-kickoff message from 90% of its room-mates) is > 0 with permutation p < 0.05 (bge; gte reported).
- **N2b (room contrast):** sign(log τ_S1,#rest − log τ_S1,#best) = sign(log T90_#rest − log T90_#best).
- **N2c (H20 timescale):** per-room H20 τ_q (days) ordered as N2b.
- **Field rival:** τ_i unrelated to T_i (ρ ≈ 0); the two rooms settle alike.
- **Credence:** N2a 0.25 (per-agent settling fits are noisy); N2b 0.5 (a coin flip in expectation).

## Result
| Native prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| N2a (primary, per agent): Spearman(τ_i, T_i) > 0 | per-agent S1 settling detected in 0/12 agents (bge) and 1/12 (gte); per-agent coverage times take only two values (#best ≈ 0.01–0.02 h; every #rest agent ≈ 10.8 h, because one rarely posting #rest agent was not read for 10.8 active h) | permutation | **n/a (unpowered; the observable has no within-room variance)** |
| N2b: sign(Δ log τ_S1) = sign(Δ log T90), #rest vs #best | T90: #rest 10.8 h vs #best 0.02 h; τ_S1 bge 17.3 vs 1.5 h (both *not detected*); gte 0.25 (detected) vs 156 h (not detected) | – | n/a (room-level S1 not detected in bge; opposite signs across models) |
| N2c: per-room H20 τ_q ordered as N2b | the slower-covering #rest settles **faster** on H20's day clock: bge 1.7 d (detected) vs 20.2 d (not detected); gte 1.6 d vs 12.3 d (both detected) | – | **failed** (against in gte, with both detected) |

**Reading.** #38 is where H20 found its strongest kickoff relaxation, and the read-out graph has a striking structure (one silent agent makes the 8-agent room take 11 active hours to be fully covered, while the 4-agent room is covered in about a minute). If settling waited for coverage, #rest should settle later. On the only estimator that is detected in both rooms (H20's two-time τ_q, gte), it settles about 8× *faster*. The hour-resolution S1 is not detectable per room in bge. Figure: [`figures/g38_rooms.pdf`](figures/g38_rooms.pdf). Data: `data/processed/H48-settling-mixing-time/G38/` (`agents.parquet`, `natives.json`, `s1_room*_*.parquet`).

## Scorecard (period-specific axes)
- **D:** failed (N2c). **C:** per-agent fits unpowered. **G:** the read-out ledger reproduces the room split exactly (no cross-room reads).

## Notes
- Room kickoffs: the shared `goal_fields` `kickoff_room` vectors (the H01 swap bug is not in the shared table) are used for the per-room robustness variant; the village kickoff is primary.
