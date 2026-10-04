# H47 × G51: Each agent: Maximize your assigned goal!

**Verdict:** failed
**Role:** native
**Period:** regime III · mode I/K · up to 32 agents · rooms [0, 15] · 45 active days (non-holdout). Units (shared `period_units`): 51a (goal_start); 51b (ne:NE32; roster_join:GPT-5.6 Luna; roster_join:GPT-5.6 Sol; roster_join:GPT-5.6 Terra); 51c (roster_join:Grok 4.5); 51d (roster_join:Kimi K3); 51e (roster_join:Claude Opus 5); 51f (ne:NE38); 51g (rooms:{#general, #focus}); 51h (rooms:{#general}); 51i (roster_join:GLM-5.3 Flash); 51j (roster_join:Claude Fable 5.1); 51k (ne:NE33; roster_join:Gemini 3.8 Flash; roster_join:Muse Spark 1.3); 51l (ne:NE33; roster_join:GPT-6 Astra).

## Why this period
The private-role era: one room (#general, 21–32 agents) except the **#focus weeks** (51g, 08-05 → 08-21), when an agent-made side room held about two core members plus short visitors (DQ6: everyone is assigned to #general; #focus is a presence deviation). Two leverages: (1) an A-B-A on a self-made room (51f → 51g → 51h); (2) one big room with many agents, where coherence could be limited by who talks to whom (conversational distance) instead of the room. Also two room events for the detector (#focus opens 08-05; #focus empties by 08-24). The #51 tail (from 09-07) is held out.

## Prediction
*Written 2026-10-04 ~06:10 UTC, before running H47 on this period.*
- **P8a (primary):** r_F = ρ_FG/ρ_GG (focus members vs general members, over general–general pairs) drops in 51g: r_F(51g) < min(r_F(51f), r_F(51h)) − 0.2 (focus-label permutation for the DiD).
- **P8b:** in the single-room units, correlation is flat across conversational tiers: median G ≥ 0.6.
- **51g as a two-room unit (replication rule):** reported, but #focus has 1–3 members per window, so C_B is near unpowered.
- **Detector (card P3, Amendment 1):** at the #focus opening (08-05), R1_swarm z < 3; R1_loc ≥ 2 within ±1 day [low credence: about two core members; synthetic #focus-like AUC 0.63]; R1_room (persistent rooms only) misses it, since #focus has no history.
- **Against:** r_F unchanged in 51g (a two-agent side room doesn't cut coherence) or G ≪ 1 (coherence in a big room is conversation-limited).

## Result
| Native prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P8a (primary): r_F(51g) < min(r_F(51f), r_F(51h)) − 0.2 | 51f 0.08 · 51g 0.27 · 51h 1.33; DiD -0.44 (ρ_FG 0.004 / 0.018 / 0.044) | focus-label permutation p (DiD low) 0.275 | **not met**: the two focus members were already decoupled before #focus existed |
| P8b: median G ≥ 0.6 in the single-room units | median G 0.18 (51a 0.32, 51b 0.24, 51c 0.17, 51d 0.15, 51e 0.50, 51f 0.08, 51h 0.10, 51i 0.18, 51j 0.18, 51k 0.41, 51l 0.14) | tier permutation | **not met**: in one room of 21–32 agents, correlation lives in pairs that address each other |
| 51g as a two-room unit (replication rule) | C_B 0.23, p 0.007; G 0.47 | 2 #focus members | supported by the replication rule, near-unpowered |
| Detector, #focus opens (08-05; clean) | R1_swarm -0.97, R1_room -1.04, R1_loc 0.05 (#focus cohort of 2) | – | no detector fires |
| Detector, #focus empties (08-24; clean) | R1_swarm 0.95, R1_room 0.95, R1_loc 0.68 | – | no detector fires |

Focus members (modal room #focus on ≥ 2 days of 51g): agents [6, 29] (13 days each).

**Reading.** The self-made side room did not visibly cut coherence: its two core members were already about 0.1× as correlated with #general as #general pairs were with each other *before* #focus opened. The side room formalized a split that had already happened (selection), and the pair statistic with 2 members is very noisy. The informative result is P8b: in the big single room, content correlation is concentrated in pairs that talk to each other (median G 0.18). Coherence inside a large room is shorter than the room.

Data: `results/g51.json`, `results/detector.json`.

## Scorecard (period-specific axes)
- **C:** 51g C_B beats the room-relabel null (p 0.007), but with two members.
- **G:** DQ6 confirms #focus is a presence deviation (everyone assigned to #general).
- **H:** R-conversation (coherence set by who talks to whom) wins inside the big room.

## Notes
- 2026-10-04 ~06:10 UTC: folder and prediction written before the real-data run.
- 2026-10-04: results filled from `analysis/explore.py` (round 1, exploratory, non-holdout only).
