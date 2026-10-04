# H15 × NE30: same-family succession, Gemini 3 Pro → Gemini 3.1 Pro (2026-03-09) — confirmatory

**Verdict:** pending (confirmatory; **not run**)
**Role:** confirmatory (locked holdout: NE30 window 2026-03-05 → 03-16, goal #34; plus the NE33 tail, #43, #45–#50 and the #51 tail for C2–C4)

## Why this NE
The successor starts with an empty memory but shares its predecessor's model family (pretraining prior). In Kolchinsky–Wolpert terms it is a full erasure of stored information (δ = 1) with the family "field" kept. If memory carried day-scale load-bearing information, the successor should show a deficit; if the family prior substituted for memory, a same-family successor should show a smaller deficit than other newcomers. Exploration (round 1) found **no** newcomer deficit at the day scale (P4 failed: V* meta +0.15 [−0.18, +0.47]; V_eng +0.32, z +2.3, i.e. newcomers are *more* active early), so there is nothing for the family prior to substitute; the confirmatory question becomes whether the null replicates, together with the one strong round-1 finding (the context-erasure dip).

## Confirmatory criteria
*Written 2026-10-03, after exploratory round 1 and before any holdout use. Script: `../analysis/confirm_ne30.py` (refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`; `--dry-run` runs on non-holdout stand-ins).*

| | Test | Pass | Stand-in used in the dry run |
| --- | --- | --- | --- |
| C1 | NE30 successor deficit (tenure days 1–3 vs 6–12, vs incumbent pseudo-join null in #34), V_rel (V* for regime II) and V_eng | z > −2 on both (refutation-only) | GPT-5.4 joining in #35 |
| C2 | NE33 batch join (Muse Spark 1.3, Gemini 3.8 Flash, GPT-6 Astra), V_eng | z > −2 (refutation-only) | GPT-5.6 Sol/Terra/Luna in #51 |
| C3 | forced-consolidation write dip, turns +1…+10 vs −20…−11, holdout regime III periods with ≥ 200 forced consolidations | DL meta ≤ −0.25 with CI below 0, and per-period CI below 0 in ≥ 2/3 of periods | non-holdout #36b–#51 |
| C4 | ML (same rule) on V*, holdout days only | NOT (meta ≤ −0.3 SD with z ≤ −2); inconclusive if < 2 periods | non-holdout ML events |
| C5 (check) | dip_CF − dip_CV vs agent-day base (task-phase confound) | > 0, CI above 0 | non-holdout |

**Overall:** CONFIRMED if C3 and C4 pass and C1/C2 don't refute; REFUTED if C3 fails, C4's opposite holds, or C1/C2 show a significant deficit; otherwise INCONCLUSIVE.

**Amendment before any holdout use (2026-10-03):** C1/C2 first also required an effect size (> −0.3 / ≥ −0.1 SD). The dry run showed that with 1–3 events these thresholds are noise-dominated (stand-in values −0.93 and −0.20 SD), so C1/C2 were made refutation-only. What I had seen: only the non-holdout stand-in values listed here.

## Dry run (non-holdout stand-ins, 2026-10-03)
C1 V_rel −0.93 (z −1.45), V_eng +0.29 (z +0.54); C2 −0.20 (z −0.58); C3 meta −0.44 [−0.49, −0.39] over 9 periods; C4 −0.55 (z −0.87, k = 2); C5 +0.0097 [+0.0056, +0.0137]. All criteria pass on the stand-ins (as they must: they are the exploratory data). Output: `data/processed/H15-semantic-information-scrambles/confirm_dryrun.json`.

## Power and caveats
- C1 has one event: it can only refute. C2 has three.
- C3 is well powered (thousands of forced consolidations per long period).
- In confirm mode the script rebuilds all H15 tables on the full calendar into `data/processed/H15-semantic-information-scrambles/confirm/`; #51 contributes only its held-out tail days (≥ 09-07) to C3/C4.
- Not covered by Vivian's approval for H02/H04/H05; needs her sign-off.
