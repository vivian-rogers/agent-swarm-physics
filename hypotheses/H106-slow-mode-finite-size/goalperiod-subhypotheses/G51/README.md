# H106 × G51: #51 common mode and the batch joins NE32 + NE33 (2026-07-06 → 09-04, non-holdout)

**Verdict:** n/a
**Role:** exploratory
**Period:** regime III · private goals (one goal period, one scaffold) · active population ≈ 22 → 30 over nine weeks · NE32 (07-09, three newcomers in isolated rooms, merged 07-10) and NE33 (09-03/04, three newcomers). The #51 tail from 09-07 is held out.

## Why this period
H81 found a #51 cross-agent common mode with τ ≈ 3 active days. #51 has one goal and one scaffold, and N jumps twice. If that mode has magnet inertia, its daily decorrelation slows after each join.

## Prediction
*Written 2026-10-04 21:39 UTC, before running on this period.*
- Day residuals as H81's #51 native (own #51 mean removed, own agent goal and #51 directions projected). Cross-agent lagged alignment L(k) (i ≠ j pairs; expectation free of N). Per window φ_W = L_W(1)/L_W(0⁺), k_W = −ln φ_W.
- **NE32:** pre 07-06 → 07-08 vs post 07-10 → 07-17. **NE33:** pre 08-27 → 09-02 vs post 09-03 → 09-04. Magnet: Δln k = −ln(N_post/N_pre) ≈ −0.1 to −0.2. Drift: 0.
- **Pass (N2):** Δln k < 0 at both joins, placebo percentile ≤ 0.10 for at least one (placebo = every other #51 day boundary with the same window lengths). **Against:** both ≥ 0.5 percentile. Expected unpowered (N rises ×1.1–1.2); if the planted-mode power is < 0.8 the verdict is **inconclusive** whatever the sign. Prior 0.1.
- Within-#51 weekly slope of k_w on ln N_w: descriptive.
- Also reported: the regime-III block-level ρ_G for #51 weeks (descriptive).

## Result
| Model | event | Δφ (post − pre) | placebo percentile | N pre → post | planted power (share 0.05 / 0.2) |
| --- | --- | --- | --- | --- | --- |
| bge_small | NE32 | -0.095 | 0.37 (n 35) | 21.0 → 25.2 | 0.15 / 0.18 |
| bge_small | NE33 | +0.442 | 0.86 (n 37) | 28.2 → 31.5 | 0.12 / 0.12 |
| gte_modernbert | NE32 | -0.381 | 0.03 (n 35) | 21.0 → 25.2 | 0.21 / 0.18 |
| gte_modernbert | NE33 | -0.067 | 0.27 (n 37) | 28.2 → 31.5 | 0.12 / 0.12 |

Weekly φ_w vs ln N_w slope (bge_small): -0.081; whole-period φ = 0.544.

Weekly φ_w vs ln N_w slope (gte_modernbert): -0.902; whole-period φ = 0.540.

Reading: **inconclusive** (unpowered: the best planted power is 0.18 < 0.8); verdict n/a by the card's power rule.

## Scorecard (period-specific axes)
E (two joins), F (planted-mode power on the #51 panel).

## Notes
- 2026-10-04 21:41 UTC, Amendment A2 (before the run): the statistic is Δφ = φ_post − φ_pre (φ outside (0, 1) makes ln k undefined in 2–6-day windows); the magnet predicts Δφ > 0, so a pass needs placebo percentile ≥ 0.90. Verdict n/a = inconclusive by the power rule.
- Data: `data/processed/H106-slow-mode-finite-size/natives/natives.json`.
