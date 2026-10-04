# H32 confirm re-freeze (round 1b), 2026-10-04

`confirm_r1b.py` replaces `confirm.py` (untouched) for any holdout run. Written before any look at #14, #22 or #28. Not run on the holdout.

## What changed
- **Exposure.** DQ1 ledger call starts (`H32_DATA=r1b`). A message counts as seen if it was posted before `t_call` of the producing call. Same-room messages posted during that call count as unread.
- **Content.** bge (primary) and gte (whitened per regime, with gte goal fields).
- **Confirm path:** builds gte vectors and fields with a base-aware copy of `scheme/build_r1b.py`, and reads held-out ledger calls through a copy of `ledger_calls` without its `~holdout` filter.
- **Dedupe** (DQ5 `statement_flags`): reported for #28, not scored. Activity bins, outages, work and failures are not inputs.
- **Predictions.**
  - **C1-r1b:** #28 transfer significant under both models.
  - **C7-r1b:** top source Opus 4.5 or GPT-5.2 under both models. Credence lowered from 0.5 to 0.3.
  - **C9-r1b (new):** at τ = 60 s, T_read > T_unread for #28 (H57 placebo).
  - C2–C6 and C8 are unchanged (bge).

## Why
- Ledger item 15 / RE-D1: re-freeze on ledger visibility.
- DQ5: the top source agrees across models in only 17/32 periods.
- STANDARDS §1: the in-flight placebo is required. Round 1b: read beats unread in 17/17 transfer periods, while unread carries about a third of the effect.

## Holdout reuse (ledger L197–L199)
- No prior run on #14, #22 or #28. Planned same-family users: #28 H12, H33, H36; #22 H06, H10, H33, H36; #14 H24, H36.
- H34 and H20 plan the same modality.
- Known issue 101: windows that cross day edges can pull held-out call rows. The dry run uses the original filter; the confirm path includes them on purpose.

## Dry run (#30→#28, #16→#22, #17→#14; built from scratch into a scratch directory)
- Executes end to end.

| Stand-in | T (bge, p) | T (gte, p) |
| --- | --- | --- |
| #30 | 0.093%, 0.024 | 0.086%, 0.024 |
| #16 | −0.001%, 0.42 | 0.031%, 0.024 |
| #17 | −0.001%, 0.39 | −0.004%, 0.54 |

- **Pass:** C1-r1b, C2, C3, C5, C6, C8, C9-r1b (T_read 0.23% vs T_unread 0.07%). **Fail:** C4 (split-half −0.45), as in the original.
- **Fail:** C7-r1b. The top source of #30 is Opus 4.5 under bge and Opus 4.6 under gte. This is the expected model dependence.
- bge T and the top source reproduce the original dry run (0.091%, Opus 4.5).

## Recommendation
**Adopt.** C7-r1b is likely to fail; it is a secondary.
