# H19 × NE43: the daily bookends stop (after 2026-08-04) and the nudger stops (after 2026-08-20), inside #51

**Verdict:** supported
**Role:** native
**Period:** #51 at a fixed roster of 27 (07-29 → 08-27). Sides: **A** 07-29 → 08-04 (pause/resume bookends + nudges), **B** 08-05 → 08-20 (nudges only), **C** 08-21 → 08-27 (no `automated` drive). #focus room 08-05 → 08-21.

## Why this period
DQ9 / the NE catalog suggest that H38's day-edge share of co-activation (agents starting and stopping together) should drop when the operator's daily bookend messages stop (08-05). The edge share of the activity gain is exactly the difference between H19's raw g_eq and its DQ8-trimmed version, so NE43's first step is a native test of where that synchrony comes from.

## Prediction
*Written 2026-10-04 06:50 UTC, before any NE43 fit.*
- **N43-a (edge share does not follow the messages).** The day-edge contribution to the activity gain, g_raw − g_trim (each side one window, H02 population rule), changes between A and B by less than 0.05. Reason: the operator still starts and stops the village every day after 08-05 (8 h windows continue to 09-04); only the announcement messages stopped. (The NE catalog's expectation, a drop after 08-05, is the competing prediction.)
- **N43-b.** The trimmed activity gain and g_eq talk differ between B and C (nudger off) by less than 2 bootstrap SEs.
- Counts against N43-a: g_raw − g_trim falling by ≥ 0.05 (and by ≥ 50%) after 08-05: the bookend messages themselves synchronize agents.

## Result
*Run 2026-10-04 (`analysis/r1b_native.py ne43`, `data/processed/H19-loop-gain-collapse/r1b/native_ne43.json`). N = 27 on every side; day-bootstrap SEs.*

| Side (days) | g_eq active raw | DQ8 trim | **edge part g_raw − g_trim** | H38-conditioned | g_eq talk raw | talk trim |
| --- | --- | --- | --- | --- | --- | --- |
| A bookends + nudges (5) | 0.32 ± 0.04 | 0.08 ± 0.06 | **0.24 ± 0.04** | 0.10 | 0.13 | 0.10 |
| B nudges only (12) | 0.28 ± 0.02 | 0.08 ± 0.02 | **0.21 ± 0.02** | 0.16 | 0.16 | 0.12 |
| C no drive (5) | 0.27 ± 0.02 | 0.05 ± 0.05 | **0.22 ± 0.05** | 0.14 | 0.15 | 0.14 |

- **N43-a: supported.** The day-edge part of the activity gain changes by −0.037 ± 0.043 when the bookend messages stop (A → B), well under 0.05; it is about three quarters of the raw gain on every side. The edges come from the operator starting and stopping the village each day, not from the announcement messages (the NE catalog's competing expectation, a drop after 08-05, is not seen).
- **N43-b: supported.** Nudger off (B → C): trimmed activity gain −0.03 ± 0.06, talk gain −0.02 ± 0.04 (raw) / +0.02 ± 0.03 (trim).
- **Verdict: supported.** Practical reading for H38 and for anyone trimming: keep trimming after 08-05; the synchrony is in the schedule, not in the messages.
