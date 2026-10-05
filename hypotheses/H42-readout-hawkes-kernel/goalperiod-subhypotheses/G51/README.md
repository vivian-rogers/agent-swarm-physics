# H42 × G51: Private roles (2026-07-06 → 2026-09-04, non-holdout part): is n_cross consistent as the swarm grows?

**Verdict:** failed (n_cross collapses to 0 in late #51 in both kernels; read-out gain positive in only 4 of 9 segments)
**Role:** native (exploratory, non-holdout); its 11 non-holdout segments (51a–51l) also enter the replication table
**Round 2 verdict:** supported (Round 2 below; the line above is round 1's)
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

## Round 2 (2026-10-05)

*Prediction (templated from the card's round-2 pre-registration, 2026-10-05 04:05 UTC, written before any round-2 statistic):* in regime III a named read raises talk at the read-out call (≈ 0.08 per read, H67), cold-named messages carry at least half the thread-named jump, the named Hawkes kernel survives a fitted Cox field, and reads move call timing only through the reading call's own decision. In regimes I–II no class switch beyond the call-skeleton null. Round-2 verdict rule: *supported* if the Cox-field named model beats field-only S0 held out (summed over the period's CV units) with n_named > 0 **and** the pooled cold-named talk J has its CI above 0; *failed* if neither; *mixed* otherwise; *descriptive* without a CV unit.

**Round 2 verdict:** supported. Period pools (random effects over units, 95% CI): talk J named 0.079 [0.070, 0.087], cold 0.052 [0.040, 0.064], thread 0.094 [0.080, 0.108], unnamed 0.0024 [0.0012, 0.0036].
Call timing (excess over the call-skeleton null): pause J named -0.0063 [-0.0094, -0.0033]; log gap J named -0.0274 [-0.0459, -0.0089] (fragile, Amendment R2-A).
R3 (Cox field; event-weighted): exponential n_x 0.024 → 0.004; read-out n_x 0.016 → 0.008; named per message 0.159 → 0.154; summed held-out gain of the named model over field-only S0 2490.5 nats.

| unit | calls | talk J named | cold | thread | unnamed | pause J named (excess) | log gap J named (excess) | chat next J unnamed (excess) | R3 n_x(A) r1 → Cox | R3 n_x(B) r1 → Cox | R3 named per msg r1 → Cox | R3 Δcv(Bmu − S0), Cox (mnats/event) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 45020 | 0.063 [0.045, 0.082] | 0.044 [0.017, 0.070] | 0.070 [0.048, 0.093] | 0.001 [-0.002, 0.005] | -0.0085 ± 0.0061 | -0.0469 ± 0.0267 | – | 0.042 → 0.003 | 0.033 → 0.022 | 0.084 → 0.080 | 24.28 |
| 51b | – | – | – | – | – | – | – | – | 0.088 → 0.051 | 0.050 → 0.041 | 0.213 → 0.204 | – |
| 51c | 106569 | 0.090 [0.068, 0.114] | 0.058 [0.024, 0.095] | 0.105 [0.080, 0.132] | 0.003 [0.001, 0.005] | -0.0007 ± 0.0076 | 0.0050 ± 0.0366 | – | 0.030 → 0.000 | 0.023 → 0.006 | 0.192 → 0.184 | 86.02 |
| 51d | 59689 | 0.062 [0.047, 0.079] | 0.055 [0.031, 0.081] | 0.065 [0.046, 0.085] | 0.000 [-0.003, 0.003] | -0.0077 ± 0.0074 | -0.0303 ± 0.0314 | – | 0.038 → 0.000 | 0.013 → 0.006 | 0.158 → 0.153 | 76.17 |
| 51e | 51081 | 0.083 [0.061, 0.104] | 0.085 [0.055, 0.133] | 0.082 [0.051, 0.114] | 0.001 [-0.002, 0.004] | 0.0005 ± 0.0107 | -0.0184 ± 0.0412 | – | 0.059 → 0.043 | 0.051 → 0.039 | 0.214 → 0.211 | 121.17 |
| 51f | 71479 | 0.073 [0.060, 0.089] | 0.038 [-0.001, 0.066] | 0.084 [0.069, 0.104] | 0.000 [-0.003, 0.004] | -0.0081 ± 0.0093 | -0.0237 ± 0.0338 | – | 0.000 → 0.000 | 0.004 → 0.001 | 0.136 → 0.127 | 60.13 |
| 51g | 218887 | 0.086 [0.073, 0.102] | 0.056 [0.027, 0.083] | 0.095 [0.081, 0.113] | 0.004 [0.002, 0.006] | -0.0085 ± 0.0088 | -0.0411 ± 0.0305 | – | 0.022 → 0.000 | 0.013 → 0.004 | 0.172 → 0.171 | 63.18 |
| 51h | 49419 | 0.117 [0.079, 0.153] | 0.017 [-0.040, 0.073] | 0.148 [0.102, 0.198] | 0.006 [0.002, 0.010] | -0.0100 ± 0.0122 | 0.0180 ± 0.0525 | – | 0.001 → 0.000 | 0.000 → 0.000 | 0.189 → 0.170 | 54.02 |
| 51i | 19148 | 0.087 [0.041, 0.126] | 0.083 [0.013, 0.149] | 0.089 [0.037, 0.146] | 0.002 [-0.003, 0.007] | -0.0014 ± 0.0229 | -0.1247 ± 0.1000 | – | 0.000 → 0.000 | 0.000 → 0.000 | 0.222 → 0.217 | 76.96 |
| 51j | 16807 | 0.094 [0.065, 0.113] | 0.063 [-0.020, 0.110] | 0.124 [0.065, 0.182] | 0.004 [0.001, 0.008] | -0.0025 ± 0.0204 | 0.0494 ± 0.0904 | – | 0.000 → 0.000 | 0.000 → 0.000 | 0.088 → 0.087 | 34.28 |
| 51k | 8108 | 0.062 [0.010, 0.085] | -0.032 [-0.152, 0.104] | 0.101 [0.039, 0.170] | -0.001 [-0.010, 0.004] | -0.0084 ± 0.0437 | -0.0860 ± 0.1063 | – | 0.000 → 0.000 | 0.002 → 0.000 | 0.090 → 0.089 | – |
| 51l | 8571 | 0.099 [0.059, 0.157] | -0.046 [-0.151, 0.168] | 0.147 [0.085, 0.180] | 0.002 [-0.008, 0.021] | -0.0345 ± 0.0369 | -0.0925 ± 0.1001 | – | 0.008 → 0.000 | 0.000 → 0.000 | 0.185 → 0.184 | – |

J = β(read) − β(in flight) per read message (OLS within agent × day × call-class cells; 1-h block bootstrap). Excess = J minus the call-skeleton null mean (8 synthetic message streams on the real call skeleton). R3: 'r1' = round 1's shared 30-min baseline refitted; 'Cox' = free log-rate per day × 10 min (per day × room × 10 min in multi-room units). Data: `data/processed/H42-readout-hawkes-kernel/round2/`.
