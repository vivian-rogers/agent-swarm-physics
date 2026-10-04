# H42 × G51: Private roles (2026-07-06 → 2026-09-04, non-holdout part): is n_cross consistent as the swarm grows?

**Verdict:** failed (n_cross collapses to 0 in late #51 in both kernels; read-out gain positive in only 4 of 9 segments)
**Role:** native (exploratory, non-holdout); its 11 non-holdout segments (51a–51l) also enter the replication table
**Period:** regime III · mode I/K (private roles) · N 21 → 32 · one room except 51g (#general + #focus) · 45 non-holdout days in 12 units split at roster joins, NE32, NE38, room-set changes, NE33. The #51 tail (from 09-07) is locked holdout.

## Why this period
The longest, largest and densest stretch of the data: about 41k agent messages and 930k calls in non-holdout segments that differ mainly in headcount. H03 found #51's n̂ falling as N grows and its fast cross term falling toward 0 by late August (room-blind at-risk set). If cross-excitation is a read-out step whose per-pair weight is attention-limited (H18, H03), the per-message cross-branching should stay roughly constant across segments while the per-pair weight falls like 1/N, and a read-out kernel should show this more cleanly than an exponential one.

## Prediction
*Written 2026-10-04 07:45 UTC, before running the #51 segments through the pipeline. Disclosed: #51c was fitted once in a timing test (world B: B n_cross 0.023, A_g 0.035, C 0.034; world pr: B 0.092, A 0).*
- **N3a:** the across-segment CV of log n_cross is smaller for world B's B than for world A's A (consistency).
- **N3b:** world B's per-pair weight (n_cross / recipients per message) falls with N: log-log slope in [−1.5, −0.5]; n_cross per message is roughly flat (|slope of log n_cross on log N| < 0.5).
- **N3c:** world B's B beats S0 on held-out likelihood in ≥ 6 of the 8 segments with ≥ 2 days.
- **Counts against:** N3a reversed; per-pair slope ≥ 0; B ≤ S0 held-out in ≥ 5 of 8.

## Result
*Replication row (layer 1):* amended reading **mixed** (world-B read-out gain +36.4 nats vs world-A exponential gain +72.3 nats over the 9 multi-day segments; event-weighted n_x 0.016 vs 0.024; world-B B above both nulls in most segments but below the 0.05 field floor); the pre-registered rule gives "supported", which is invalidated by the synthetic validation (card A3).

Replication rows for the 12 non-holdout segments (world B = call-clock world; world A = H03 world): see `data/processed/H42-readout-hawkes-kernel/G51/replication_block.md`. In brief, world-B n_x(B) is 0.033, 0.049, 0.023, 0.013, 0.051, 0.004, 0.013, 0, 0, 0, 0.001, 0 (51a → 51l, N 21 → 32), and world-A n_x(A) is 0.041, 0.088, 0.030, 0.038, 0.059, 0, 0.022, 0.001, 0, 0, 0, 0.008. The median read-out lag grows from 19 s (51a) to 78–87 s (51f–51h); q90 from 5 to 20 min.

| prediction | observed | verdict |
| --- | --- | --- |
| N3a CV of log n_x smaller for B than A | SD of log n_x 1.61 (B) vs 1.78 (A); 5/12 (B) and 4/12 (A) segments at the floor | met only formally: both collapse to the floor |
| N3b per-pair weight ∝ N^(−0.5…−1.5), n_x flat in N | Spearman ρ(n_x(B), N) = −0.78, ρ(n_x(A), N) = −0.71; per-pair ρ = −0.82; nonzero-unit slope of log per-pair weight on log N = −5.1 | **failed** (n_x is not flat; it falls with N and with time) |
| N3c world-B B beats S0 held out in ≥ 6 of 8 multi-day segments | 4 of 9 | **failed** |
| (extra) world-B B above both nulls | 6 of 12 segments (all in 51a–51g) | — |

- **Reading:** in #51, message-driven talk excitation is small (≤ 0.05 per message) under both kernels while the swarm is young. It is gone from 51h (08-24) on, after the room merge and NE43, as read-out lags grow. This matches H03's finding that fast cross-triggering in #51 falls toward 0 by late August.
- **The read-out kernel does not make n_cross more consistent across #51; it vanishes along with the exponential one.** N and time (NE43, the room-set changes, longer pause chains) are confounded across segments.
