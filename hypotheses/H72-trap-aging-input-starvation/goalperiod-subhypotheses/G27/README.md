# H72 × G27: blocked spells (Jev v3.1 `p_blocked`), with G51 as the powered companion (2026-01-12 → 01-23)

**Verdict:** failed
**Role:** native
**Prediction outcome (dated, written against H72):** held. The verdict line scores H72's claim (blocked-spell aging is starvation).
**Period:** regime I · #27 (10 days of long debugging traps); G51 non-holdout days as the second, powered arm. Unit: 5-min Jev windows inside blocked spells (`p_blocked` ≥ 0.5 runs; H16 TS5).

## Why this period
HH260 names Jev blocked spells as the check. #27 is the long-debugging period where blocked spells aged most (H16 round 1b β −1.24). A blocked agent is busy, so the test asks whether directed input, not idleness, sets its escape.

## Prediction
*Written 2026-10-04, before running (card, N2).*
Blocked-spell aging survives the directed-starvation control (ρ < 0.3) in both periods, and β_s's CI includes 0 [0.65].

## Result
`analysis/native.py`; numbers in `data/processed/H72-trap-aging-input-starvation/native/native.json` (logit, agent FE, B = 200).

| Period | spells / windows / leaves | β_age0 | β_age (s controlled) | β_s (s_dir) | ρ | prediction |
| --- | --- | --- | --- | --- | --- | --- |
| G51 | 2948 / 4910 / 2678 | -0.54 [-0.63, -0.36] | -0.54 [-0.63, -0.36] | +0.01 [-0.03, +0.05] | -0.00 | pass |
| G27 | 285 / 493 / 257 | -0.70 [-0.89, -0.28] | -0.71 [-0.89, -0.28] | +0.04 [-0.04, +0.10] | -0.01 | pass |

