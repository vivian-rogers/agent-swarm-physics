# H66 × G51: private roles; measured server time and the room split (2026-07-06 → 2026-09-04, units 51a–51l)

**Verdict:** failed
**Role:** native (also the replication estimator on its 12 units)
**Period:** regime III · #51 · 21–32 agents (9 labs) · #general, plus #focus in 51g (08-05 → 08-21) · 33 non-holdout days in 12 units.

## Why this period
- **Measured server time.** Three Gemini agents (Gemini 2.5 Pro, 3.1 Pro, 3.5 Flash; more after 09-03) log the API's own server time (`dur_api_s`), the only direct platform-latency measurement in regime III. It validates the turnaround proxy and separates a provider field from a village-wide one.
- **Room split (51g).** A platform field ignores rooms; a reading coupling does not. Cross-room pairs are the control.
- **The largest regime-III residual** after H38's trim (z 8.5), with nine providers.

## Prediction
*Written 2026-10-04 20:30 UTC, after the synthetic study (Amendment 1) and before any real-data statistic.*
- **Proxy validation:** across Gemini calls, corr(log turnaround, log server time) ≥ 0.5 [0.7].
- **Provider vs platform:** the Google server-time spin correlates between Google agents beyond the block-shift null [0.6]; the Google server-time field correlates with the non-Google turnaround field at |ρ| < 0.02 [0.65].
- **Room split (51g):** cross-room / same-room ρ̄_lat in [0.8, 1.25] [0.7]; residual activity E larger for same-room than cross-room pairs [0.55]; Δf < 0.10 [0.65].
- **Replication (12 units):** E significant in ≥ 8/12 units [0.7]; median Δf < 0.10 [0.6].
- *Against my reading:* Google server time co-moving with other providers' turnaround (a village-wide field), or Δf ≥ 0.35.

## Result
*Run 2026-10-04 ~21:00 UTC. Data: `data/processed/H66-platform-latency-field/replication/<unit>.json`, `unit_table.parquet`.*

| unit | N | days | all-present min | E [95% CI] (block-shift p) | Δf [95% CI] | ρ̄_lat (p) | ρ̄_lat same-lab / cross-lab | corr(L, K) (post hoc) | rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 21 | 2 | 916 | -0.0017 [-0.0058, 0.0032] (p 0.73) | -0.16 [-2.02, 1.40] | 0.017 (p 0.02) | 0.040 / 0.010 | 0.04 | descriptive |
| 51c | 25 | 5 | 1687 | 0.0029 [-0.0007, 0.0068] (p 0.06) | 0.28 [-0.49, 2.46] | 0.006 (p 0.08) | 0.013 / 0.004 | 0.15 | descriptive |
| 51d | 26 | 5 | 1628 | -0.0007 [-0.0019, 0.0013] (p 0.63) | -0.68 [-10.20, 3.44] | 0.003 (p 0.42) | -0.013 / 0.006 | 0.11 | descriptive |
| 51e | 27 | 3 | 846 | -0.0004 [-0.0018, 0.0015] (p 0.55) | -4.03 [-4.03, 17.06] | 0.027 (p 0.02) | 0.041 / 0.024 | 0.12 | descriptive |
| 51f | 27 | 4 | 1416 | 0.0069 [-0.0014, 0.0175] (p 0.01) | 0.36 [0.25, 0.61] | 0.046 (p 0.02) | 0.037 / 0.048 | 0.19 | supported |
| 51g | 27 | 13 | 4884 | 0.0031 [0.0007, 0.0066] (p 0.01) | 0.17 [-0.05, 0.62] | 0.023 (p 0.02) | 0.022 / 0.023 | 0.06 | mixed |
| 51h | 27 | 3 | 1137 | 0.0036 [0.0001, 0.0092] (p 0.07) | 0.19 [0.09, 0.61] | 0.066 (p 0.02) | 0.080 / 0.062 | 0.13 | descriptive |
| 51i | 28 | 2 | 368 | 0.0049 [-0.0019, 0.0115] (p 0.12) | 0.04 [-0.74, 0.55] | 0.107 (p 0.02) | 0.089 / 0.110 | -0.00 | descriptive |
| 51j | 29 | 1 | 423 | 0.0038 [-0.0031, 0.0105] (p 0.15) | 0.10 [-1.67, 1.15] | 0.091 (p 0.02) | 0.084 / 0.093 | 0.07 | descriptive |
| 51k | 30 | 1 | 218 | 0.0054 [-0.0035, 0.0139] (p 0.11) | 0.95 [-2.86, 7.32] | 0.224 (p 0.02) | 0.290 / 0.213 | 0.34 | descriptive |
| 51l | 30 | 1 | 192 | 0.0101 [-0.0003, 0.0218] (p 0.03) | 0.42 [-0.29, 3.31] | 0.179 (p 0.02) | 0.199 / 0.175 | 0.10 | mixed |

Ineligible (all-present window with a defined field < 10 minutes per day): 51b.

**Pre-registered rule:** supported. **Verdict after Amendment 2 (post hoc, 2026-10-04 ~21:20 UTC):** failed. In every unit the latency field rises with the number of active agents (corr(L, K) > 0), while a latency field that silences agents gives corr(L, K) < 0 (synthetic W2: −0.34 to −0.66). A congestion world with no latency action (W6) returns Δf ≈ 1.1–1.6, so a positive Δf here measures load, not drive. Where E is not significant, there is no residual to explain (descriptive).

### Native tests (predictions above)
| Prediction | Observed | Verdict |
| --- | --- | --- |
| corr(log turnaround, log server time) ≥ 0.5 within agent-day | r = 0.49 over 199,181 Gemini calls (per agent 0.30–0.52); server time is 0.44 of the median turnaround | held (marginal) |
| Google server-time spin co-moves between Google agents | ρ̄ -0.019 to 0.058; p ≥ 0.06 in all 11 units | failed |
| Google server-time field vs non-Google turnaround: \|ρ\| < 0.02 | 51a 0.09, 51c 0.03, 51d 0.02, 51e -0.02, 51f 0.05, 51g 0.00, 51h -0.03, 51i -0.04, 51j 0.04, 51k 0.18, 51l 0.08 (p < 0.05 in 51f, 51k) | mostly held (small, mostly n.s.) |
| (descriptive) Google *turnaround* vs non-Google turnaround | 51a 0.04, 51c 0.07, 51d 0.01, 51e 0.13, 51f 0.13, 51g 0.10, 51h 0.34, 51i 0.36, 51j 0.45, 51k 0.69, 51l 0.66 | the shared field is the non-API part of a call |
| 51g room split: cross-/same-room ρ̄_lat in [0.8, 1.25] | same-room 0.021 / cross-room 0.036 (ratio ≈ 1.7) | failed as bounded; the field is not room-gated (cross-room pairs co-move more) |
| 51g: same-room E > cross-room E | 0.0036 vs 0.0003 | held (both small) |
| 51g: Δf < 0.10 | 0.17 [-0.05, 0.62] | failed (and it measures load) |
| E significant in ≥ 8/12 units | 3/11 eligible units (51b ineligible) | failed |

**Reading.** The API server time does not co-move across agents, within Google or with other providers. The turnaround does co-move across providers, and the co-movement grows late in #51 (ρ̄_lat 0.09–0.22 at N = 28–30). The shared component is the harness and execution part of a call. It rises when more agents are active: a congestion meter of the village platform, not a field that drives co-activation.

## Scorecard (period-specific axes)
- C (adequacy): E against the trimmed block-shift null, per unit above.
- H (comparative): the field-vs-load sign test (post hoc) decides against the H66 field reading in every unit with a significant E.

## Notes
- Written by `analysis/summarize.py` (replication rows templated; native rows written from `native/results.json`).
