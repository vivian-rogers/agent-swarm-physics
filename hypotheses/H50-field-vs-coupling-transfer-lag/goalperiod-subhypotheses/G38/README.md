# H50 × G38: Rooms with different instructions; the pause gates (#38a–e) (2026-04-02 → 2026-04-24 (units 38a–38e, 17 days))

**Verdict:** supported (replication supported; native: resume and pause are scaffold fields with zero relative lag; agents stop without reading the pause message)
**Role:** native
**Period:** regime III · units 38a (8 d, N=12), 38b (3 d, N=12), 38c (1 d, N=13), 38d (2 d, N=13), 38e (3 d, N=14).

## Why this period
17 daily bookends at fixed clock times (resume 16:59:30 UTC, pause ≈ 21:00:02) in two rooms: a square-wave input. The resume arrives ≈ 1.5 min before the scaffold starts agents and the pause ≈ 1–6 min before it stops them, so it separates a scaffold field (start/stop by the platform) from a read-out response to the message and from a peer cascade. Also the replication estimator on its 5 units.

## Prediction
*Written 2026-10-04 07:00 UTC, before running this test.*
- (i) Resume: ≥ 80% of agents make their first call of the day before the first peer message of the day reaches their room (onsets cannot be peer-driven; zero relative lag).
- (ii) Pause: agents read the pause message at hop 1; the number of calls after its read-out is small and set by the scaffold's stop time: Spearman ρ between peer messages read after the pause read-out and calls made after it is ≤ 0.2 (no goodbye cascade keeps agents going), and last-call times are tightly clustered (IQR across agents ≤ 2 min).
- (iii) Talk at the pause read-out call is elevated over placebo (J₁ at the pause message > 0; low power, 17 events).
- Replication rule (card) on the pooled units: expected *supported*.

## Result
### Replication layer (common estimator)
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G38/` (one JSON per unit). Figure: [`figures/G38_gate_fir.pdf`](figures/G38_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.009 [0.001, 0.017]; activity field excess (full window, day-weighted) = 0.66; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | 8 | 12 | 11,898 | 13.0 | 15 | 0.050 [0.033, 0.069] | 1 | -0.010 [-0.041, 0.008] | -0.045 [-0.066, -0.027] | -0.005 [-0.012, 0.003] | 1.06 |
| 38b | 3 | 12 | 4,186 | 13.4 | 18 | 0.017 [-0.023, 0.048] | 3 | -0.007 [-0.038, 0.023] | -0.025 [-0.047, 0.006] | 0.008 [-0.001, 0.016] | 1.20 |
| 38c | 1 | 13 | 1,619 | 11.9 | 24 | 0.021 [-0.026, 0.072] | – | -0.041 [-0.113, 0.031] | -0.035 [-0.101, 0.042] | 0.014 [-0.025, 0.049] | 0.90 |
| 38d | 2 | 13 | 2,215 | 12.5 | 21 | -0.014 [-0.050, 0.025] | – | 0.017 [-0.016, 0.046] | 0.043 [-0.024, 0.110] | -0.029 [-0.068, 0.019] | 2.26 |
| 38e | 3 | 14 | 3,998 | 12.6 | 19 | -0.002 [-0.013, 0.006] | 4 | -0.017 [-0.042, 0.002] | 0.015 [0.002, 0.027] | -0.013 [-0.019, -0.006] | -0.09 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | 2.08 | 0.77 (0.80 / 0.16) | 0.19 | 0.19 | 0.22 | 1.33 [0.94, 1.72] | 0.06 |
| 38b | 3.73 | 0.54 (0.16 / 0.46) | 0.76 | 0.10 | 0.12 | 0.86 [0.00, 2.16] | -0.04 |
| 38c | 1.53 | 0.40 (0.76 / 0.26) | – | 0.14 | 0.65 | 0.66 [0.00, 1.81] | 0.03 |
| 38d | 1.42 | 0.63 (0.84 / 0.14) | – | 0.03 | -0.08 | 0.00 [0.00, 3.03] | -0.20 |
| 38e | 1.83 | 0.60 (0.76 / 0.19) | 6.23 | 0.11 | 0.56 | 0.00 [0.00, 0.22] | 0.06 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | edge_on | 8 | 5.23 [4.38, 8.15] | 7 | 28 | 0.38 |  | – |
| 38a | pause | 8 | -10.65 [-11.46, -8.70] | 2 | 13 | -0.91 |  | – |
| 38a | human | 13 | -0.28 [-0.49, 0.55] | 0 | 2 | 0.15 | human_other: -0.104 [-0.264, 0.250] | – |
| 38a | nudge | 41 | 0.53 [-0.31, 1.72] | 19 | 5 | 0.16 | nudge_target: 0.092 [-0.161, 0.400] | – |
| 38a | platform | 462 | 0.38 [0.30, 0.67] | 1 | 3 | 0.08 |  | – |
| 38b | edge_on | 3 | 4.95 [2.80, 5.34] | 5 | 36 | 0.86 |  | – |
| 38b | pause | 3 | -3.36 [-3.81, -1.05] | 2 | 10 | -0.35 |  | – |
| 38b | human | 4 | 1.78 [1.17, 3.44] | 2 | 11 | 0.23 |  | – |
| 38b | nudge | 16 | -0.35 [-3.44, 1.51] | 12 | 13 | -0.05 |  | – |
| 38b | platform | 137 | 1.30 [0.61, 2.03] | 2 | – | 0.17 |  | – |
| 38d | edge_on | 2 | 6.62 [–, –] | 4 | 6 | 1.22 |  | – |
| 38d | pause | 2 | -11.09 [–, –] | 2 | 18 | -1.72 |  | – |
| 38d | human | 1 | 1.30 [–, –] | 7 | 2 | -0.42 |  | – |
| 38d | nudge | 20 | 1.30 [–, –] | 1 | 6 | 0.12 | nudge_target: 0.044 [-0.460, 0.454] | – |
| 38d | platform | 93 | 0.88 [–, –] | 1 | 3 | 0.03 |  | – |
| 38e | edge_on | 3 | 4.57 [0.82, 10.07] | 6 | 28 | 0.48 |  | – |
| 38e | pause | 3 | -7.37 [-7.37, -4.75] | 2 | 11 | -0.36 |  | – |
| 38e | human | 9 | 0.48 [-0.70, 3.63] | 10 | 6 | 0.24 | human_other: 0.231 [-0.006, 0.343] | 3 |
| 38e | nudge | 22 | -0.72 [-2.82, 0.42] | 1 | 4 | -0.08 | nudge_target: – [1.144, 1.154] | 1 |
| 38e | platform | 175 | 0.71 [0.59, 1.69] | 1 | 12 | 0.05 |  | – |


### Native test
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G38/native.json`, `pause_stops.parquet`. Figure: [`figures/G38_pause_stops.pdf`](figures/G38_pause_stops.pdf). 17 days, 211 agent-days.

| prediction | observed | verdict |
| --- | --- | --- |
| (i) ≥ 80% of agents start before the first peer message reaches them | 82%; first-call onsets have IQR 9 s across agents (≈ 0.7 call cycles) | yes |
| (ii) stop set by the scaffold, not by reading goodbyes: few calls after read-out, ρ ≤ 0.2, last-call IQR ≤ 2 min | only 6% of agents make any call after the pause message (median 1); last-call end relative to the message: quantiles 10/25/50/75/90% = -217, -92, 1, 10, 23 s; per-day IQR 73 s; ρ not computable (too few readers) | yes for the stop; the predicted mechanism (read at hop 1, then stop) is wrong: agents are halted without reading it |
| (iii) talk at the pause read-out elevated | not testable (no read-out calls near the boundary) | n/a |

**Reading.** Both gates are scaffold fields with zero relative lag. At the resume, agents start within seconds of each other (IQR ≈ 9 s, under one call cycle), and most start before any peer message exists, so there is no start-up cascade. At the pause, in-flight calls finish (90% of last calls end within 23 s after the message) and no new call starts. The message is posted as agents are halted, so it is an announcement, not an input they respond to. This is the mechanism behind H38's regime-III edge co-activation.

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 1/5 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 1/5 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 (bge, all) | 0.064 [-0.013, 0.141] | CI includes 0 (1 unit(s)) |
| R1 J^c_1 named / unnamed | -0.060 [-0.174, 0.054] / 0.096 [0.009, 0.183] | address split |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | 0.048 [0.016, 0.081] / 0.159 [0.031, 0.286] | post hoc; valid in regime III only |


## Notes
