# H40 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-27)

**Verdict:** failed
**Role:** native (exploratory; NE14 inside the period, exception (c): the transition is the object). Replication numbers reported too.
**Period:** regime II on 36a (03-23), regime III from 03-24 (36b, 36c; NE14 perma-computer-use, NE41 forced consolidation); #35 (regime II) added as extra pre-days · 12 agents · rooms 2 and 3 · 8,611 read-out items in #36.

## Why this period
A within-agent cadence change at a dated scaffold step: the regime II → III switch. If per-call coupling is invariant, an agent's change in per-hour coupling should track its change in call rate.

## Prediction
*Written 2026-10-04 ~06:10 UTC (card N4), before any H40 statistic on G35/G36.* For the median agent the change in per-call coupling is smaller in magnitude than the change in log call rate. Weak test (one regime-II day in #36; the switch changes context structure too).

## Result
| Test | Observed | Prediction | Verdict |
| --- | --- | --- | --- |
| **N4** share of agents with \|Δ log per-call β(10)\| < \|Δ log rate\| (11 agents) | 0.09 (1/11) | ≥ 0.5 | **failed** |
| median Δ log call rate / Δ log per-call / Δ log per-hour | −0.21 / +0.18 / +0.10 | | |
| median \|Δ log per-call\| vs \|Δ log rate\| | 0.60 vs 0.21 | | per-call coupling moved 3× more than cadence |
| corr(Δ log per-hour, Δ log rate) | +0.34 (n = 11) | | weak |
| Replication η (#36) | +0.08 ± 0.15 | CI < 0.5 | supported |
| Replication held-out Δ log-lik | +0.0104 | > 0 | supported |

**Reading.** Across the scaffold switch, call rates fell about 19% while per-call reply coupling changed by a factor of ~1.8 in either direction, agent by agent (e.g. one agent's replies collapsed from 89 to 5 in the 10-call window). A regime switch changes what a call *is*, so per-call coupling is not invariant across it; cadence is not the only thing the switch moved. Within #36 the call clock holds (η ≈ 0.08).

Data: `native/N4_G36.json`, `results/G36.json`.

## Scorecard (period-specific axes)
- **E:** failed (per-call coupling not invariant across NE14). Small n (11 agents; post side 2–4 days).
