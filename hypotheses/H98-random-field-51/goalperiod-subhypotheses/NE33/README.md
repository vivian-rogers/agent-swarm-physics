# H98 × NE33: late joiners take their role field on day 1 (2026-08-31 → 09-04)

**Verdict:** failed
**Role:** native (exploratory)
**Period:** regime III · #51 · late single and batch joins with new roles: press baron (08-31), AI safety researcher (09-01), and the NE33 batch (09-03/04: 3D world creator, village helper, village tooler). Units 51i–51l. The tail (09-07 on) is held out.

## Why this period
A random field acts at once; a coupling needs time to read and converge. Agents who enter with a fresh role and an empty context have had no time to couple, so their first-day content position isolates the field. No other #51 window adds new roles to a running swarm. (Added after NE32 proved untestable; see that folder.)

## Prediction
*Written 2026-10-04 20:50 UTC, before running this test.*
- **N3a (field on day 1).** On each joiner's first non-holdout day with ≥ 3 statements, its day state (primary variant, centered by that day's swarm mean) aligns with its own whitened role vector more than with the other role vectors present: own-role percentile among all role vectors of agents present that day. Mean over joiners ≥ 0.8; exact uniform-rank null p < 0.05. Credence 0.6.
- **N3b (no build-up).** Incumbents (all other role holders) on the same days have a mean own-role percentile within ±0.15 of the joiners' mean. A coupling-built position would put joiners below incumbents. Credence 0.55.
- Counts against: joiners' mean percentile ≤ 0.6, or joiners more than 0.15 below incumbents.

## Result
*Run 2026-10-04 20:52 UTC (after a fix: an agent's first day must have its DQ6 role valid; the first run had counted agent 41 on 08-28, before its role).*

| Variant | Joiners' mean own-role percentile (exact p) | Incumbents, same days |
| --- | --- | --- |
| style_resid_period × bge (primary) | 0.57 (0.30) | 0.83 |
| style_resid_period × gte | 0.67 (0.11) | 0.83 |
| white32 × bge | 0.73 (0.04) | 0.86 |
| white32 × gte | 0.66 (0.12) | 0.84 |

- Per joiner (primary): press baron 0.78, AI safety researcher 0.54, 3D world creator 0.68, village helper 0.19, village tooler 0.68 (27–32 role vectors each).
- **N3a fails** (≤ 0.8; p 0.30) and **N3b fails** (joiners 0.18–0.26 below incumbents). Joiners take their role field over days, not at once. In the RF model the field acts at once, so the field strength is not constant in time for a newcomer.
