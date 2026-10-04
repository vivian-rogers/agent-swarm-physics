# H59 × G05: Holiday, leadership-format survey (2025-06-19 → 06-25)

**Verdict:** mixed
**Role:** native
**Period:** regime I · free week · 4 agents · #general · 5 days. 881 human messages (86 speakers), the densest human input in the data.

## Why this period
#5 is the human-dose period (DQ9 affordances): agents often read several human messages in one call. The one-lever model treats the read as the unit (one kick per class per call, overlapping classes add). Its rival is a linear dose, in which each message adds its own lever.

## Prediction
*Written 2026-10-04, before running on this period.*
- **Dose:** the lag-0 Hu amplitude for reads carrying ≥ 3 unnamed human messages is ≤ 2× that of reads with exactly one (saturating; H43 batched R 0.2–0.4, H30's per-message pull falling over 1–7 messages). The linear-dose rival predicts ≥ 3× (the mean count in the ≥ 3 group).
- **LOCO** among Hu, Hm, A, with the templated replication rule (card P6).
- Verdict: supported if the dose saturates and LOCO is supported; failed if neither; else mixed.

## Result
`data/processed/H59-one-lever-model/native/G05.json`.
- **Dose saturates ✓.** Lag-0 Hu amplitude scale by messages read together: 1 message 1.21 ± 0.27 (1,510 reads), 2 messages 0.97 ± 0.51 (405), ≥ 3 messages (mean 4.3) −0.02 ± 0.73 (219). Ratio ≥ 3 vs 1: −0.02 [−1.2, 1.2], below the ≤ 2 bound and far below the linear-dose ≈ 4.3. A read is the unit; extra messages in the same read add nothing measurable (H43's batched R, H30's per-message dilution).
- **LOCO fails ✗.** Hu: T 0.16 (S_H59 7.3 vs S_free 46.8; free − H59 [9, 62]); A: T ≈ 0 (0.0 vs 19.3; [10, 27]); Hm uninformative. Shared θ = 223° (≡ 43° with the field sign flipped): a different direction from G04 (88°) and G51 (73°).
- Verdict **mixed**: the read-as-unit part of the lever holds; one triple per class does not.

## Scorecard (period-specific axes)
D 1 (saturating dose, as predicted) · I 0 (no transfer across classes).

## Notes
- Idle calls are rare in regime I (51 transitions from I), so the state space is effectively W/T here.
