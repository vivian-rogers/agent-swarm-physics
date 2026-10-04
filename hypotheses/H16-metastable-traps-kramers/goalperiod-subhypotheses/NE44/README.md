# H16 × NE44: The gate model across the pause-default change (12 h → 5 min, 2026-06-11)

**Verdict:** mixed
**Role:** native
**Period:** regime III. Before = G37–G44 (03-30 → 05-29, 7 non-holdout periods pooled with period dummies; 2,933 TS2r gates). After = G51 07-06 → 08-20 (nudger on, before NE43; 18,981 gates). The change itself (06-11) lies inside the locked NE21+NE23 holdout window (06-08 → 07-06), which is not used, so this is a between-period contrast, confounded with goals, roster and the 4 h → 8 h day change.

## Why this period
NE44 changes the gate structure of idling (CHANGELOG [Tools]: a pause with no duration defaults to 5 min instead of 12 h). H35 found that before 06-11 a nudge wakes a pausing agent at any trap age, and after it only early re-pauses respond. H16's gate model (TS2r: escape at each pause expiry, agent FE) can test that directly.

## Prediction
*Written 2026-10-04, before running (card, "Round 1b", N1). H35's result had been seen.* (a) The directed-kick × ln k interaction in the gate logit is ≈ 0 before (CI includes 0) and negative after (CI below 0). Credence 0.5. (b) The median declared pause duration falls ≥ 5× from before to after. Credence 0.8. (c) Gate escape at k = 1 is more likely before than after. Credence 0.5.

## Result
*Run 2026-10-04 (`analysis/native_r1b.py`; `data/processed/H16-metastable-traps-kramers/r1b/native_r1b.json`; figure `../../figures/r1b_summary.pdf`, panel b). Logit with agent FE; Wald 95% CIs.*

| | before NE44 (G37–G44) | after NE44 (G51 ≤ 08-20) | prediction |
| --- | --- | --- | --- |
| ln k (aging at the gate) | −0.60 [−0.72, −0.48] | −0.39 [−0.44, −0.34] | – |
| directed kick D | +0.51 [0.19, 0.84] | +0.43 [0.30, 0.56] | – |
| D × ln k | **+0.57 [0.27, 0.87]** | +0.06 [−0.04, 0.16] | (a) **failed** |
| P(escape), k ≥ 3, with / without a directed kick | 0.56 / 0.21 | 0.25 / 0.17 | – |
| median declared pause (90th pct) | 90 s (600 s) | 180 s (840 s) | (b) **failed** |
| P(escape) at k = 1 | 0.58 | 0.49 | (c) holds |

**Mixed.** The interaction is positive before the change, not zero: in probability terms a directed kick lifts escape at deep gates from 0.21 to 0.56 under the old default and only from 0.17 to 0.25 after it. That is H35's pattern (a kick rescues at any depth before, barely in deep chains after), but my logit-scale operationalization had the wrong sign. Declared durations did not shrink: agents almost always declare a duration, so the 12-h default rarely applied in these periods, and NE44's footprint is in the kick response, not in the timers.

## Scorecard (period-specific axes)
E 1 (partial: the response to kicks changes across NE44 in the direction H35 described, but two of three pre-registered statements failed). G 1.

## Notes
- Pre and post differ in day length (4 h vs 8 h), roster size and goal; period dummies absorb only level differences before the change.
