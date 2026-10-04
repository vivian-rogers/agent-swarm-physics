# H11 × G26: Elect a village leader. They choose this week's goal! (2026-01-05 → 2026-01-12)

**Verdict:** P1 supported; P2 supported; HH22: jump supported, mechanism inconclusive
**Role:** exploratory (candidate)
**Period:** regime I · mode C · N = 10 at start · one room (#general) · 5 active days. Class for H11: **FM-consensus**.

## Why this period
HH22 (folded into H11 on 2026-10-03 by Vivian) and HH84: approval voting over six candidates, a three-way tie, then a runoff. Two state variants: project labels (the shared ballot documents) for P1/P2, and **chat-declared votes** for the HH22 tests.

## Prediction
*Written 2026-10-03, before running on this period.*
- **Class prediction:** ferromagnetic (consensus on a shared choice): βJ_CW > 0 (P1), βJ_PL z_N2 ≥ +2 (P2), and a first-order jump in the dominant share (P3). Per-period verdict on P1: **supported** if the sign is right and |t| > t_(D−1, 0.975) (leave-one-day-out jackknife); **weak** if the sign is right but not significant; **failed** if the sign is wrong.
- **P3 (consensus jump):** the share x₁ of the final-day dominant project shows an O4 'jump' (Δ ≥ 0.3, τ ≤ 2 windows, persistence ≤ 0.15), and βJ_CW ≥ βJ_s(q_eff) (first-order region). A jump with βJ_CW < βJ_s is scored as a field-driven step; a gradual rise counts against P3.
- **P4 (control):** the action-class βJ_CW is positive or ≈ 0 whatever the class.
- **P7 (prior):** |βJ_CW| < 2, below βJ_s(q), so no spontaneous first-order transition.
- **Minimum data:** ≥ 15 room blocks with N_b ≥ 3 at W = 30; otherwise n/a.
- **What would count against it:** the opposite sign of βJ_CW (P1), or, for an FM class, a positive βJ_CW that disappears under the within-agent permutation null N1 (spread carried entirely by agent fields, R1).

**HH22 vote tests (G26 only; chat-declared votes, structural labels, no text).**
- *States.* A vote declaration is an agent chat message in #26 containing a vote word that names ≥ 1 roster agent (`chat_mentions_clean.mentions_roster`).
  - The primary set is first-person declarations ("I vote / my vote / I approve …"); any vote-word message is the robustness variant.
  - A single named candidate is a categorical state. Several named candidates form an approval set, weighted 1/k per candidate.
  - Each voter's latest declaration is carried forward.
  - Candidates are the agents named in ≥ 1 first-person declaration; HH22 expects q = 6.
  - Runoff onset is the first 30-min window with ≥ 2 agent messages containing "runoff", a structural keyword timing.
- **P-G26a (symmetric point).** At runoff onset, the latest declarations put the top three candidates level: a multinomial equality test on their approval weight gives p > 0.05, and the perplexity of the declared distribution over the candidates is q_eff ≥ 3. Fails if one candidate already leads significantly.
- **P-G26b (first-order jump).** The eventual winner's declared share shows an O4 "jump" at or after runoff onset: Δ ≥ 0.3, τ ≤ 2 windows, rising from ≈ 1/3 to ≥ 0.75, with persistence ≤ 0.15. Fails if the rise is gradual (R3) or absent.
- **P-G26c (Potts mechanism, mean field).** Take the runoff snapshot (each voter's last single-candidate declaration after onset) under symmetric fields (HH22's symmetric point). The profile-likelihood βJ_snap of the Curie–Weiss Potts with q = q_runoff is ≥ βJ_s(q_runoff), i.e. the first-order region (βJ_s(3) = 2.75). If the runoff count vector is concentrated but βJ_snap < βJ_s, or symmetric fields are rejected, the step is field-driven (institutional), not a Potts transition.
- My credences: P-G26a 0.5; P-G26b 0.5; P-G26c 0.15. The runoff is a protocol change that narrows q from 6 to the tied set; that is a field, not spontaneous ordering.

## Result
| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P1 βJ_CW (primary) | > 0 | +6.13 (jackknife SE 0.87, t = +7.03, t_crit 2.78) | βJ = 0; N1 (within-agent permutation) mean -1.09, z_N1 = +4.0 | **supported** |
| P2 βJ_PL (agent fields) | z ≥ +2 | +7.49; z_N2 = +6.44, z_N1d = +5.29, z_N1 = +4.99 | N2 (circular shift) mean +4.14 | **supported** |
| O3 agreement ratio R | – | 9.35 | 1 = interchangeable agents | descriptive |
| P3 consensus jump (project labels) | jump, Δ ≥ 0.3, τ ≤ 2, persistence ≤ 0.15; βJ_CW ≥ βJ_s(q_eff) | gradual (Δ = +0.18, τ = 0.03 win, persistence +0.50); q_eff = 4.7, βJ_s = 3.56, first-order region: yes | constant / linear fits | **failed** |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | +1.27 (t = +2.81); action βJ_PL z_N2 = +3.97 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 5/5 day folds improve | fields only | consistent |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = +38.9 | N1 (9 draws) | agrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW +6.13; drift-corrected excess βJ_PL − N2 mean = +3.36 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels +5.54, q ≤ 4 +6.78, W = 15 min +5.93, W = 60 min +6.24, computer-use actions only (post hoc) +5.68, day fields +3.77.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: +3.43. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 0.17.
- Persistence P(same project next window): 0.61.

**HH22 vote tests (chat-declared votes; candidate codes only, no text):**
| Test | Prediction | Observed | Verdict |
| --- | --- | --- | --- |
| P-G26a symmetric point at runoff onset | top-3 level (p > 0.05), q_eff ≥ 3 | onset rule fired at window 2 (day 1). Top-3 approvals [8.0, 3.0, 2.0], χ² p = 0.09, q_eff = 3.66, 9 voters | passes the test as written (p > 0.05, q_eff ≥ 3) but is uninformative: the onset rule fired on a day-1 mention of a runoff, the test has little power, and the proxy does not reproduce the reported three-way tie |
| P-G26b runoff is a first-order jump | jump, Δ ≥ 0.3, τ ≤ 2, ≈ 1/3 → ≥ 0.75, persistence ≤ 0.15 | jump at window 27.2 of 36: 0.18 → 0.80 (Δ = 0.62, τ = 0.15 win, ΔBIC step vs linear 40), persistence 0.00 | **supported** (the pre-jump level is 0.18, below ≈ 1/3; any-vote-word variant: Δ = 0.48, end level 0.69) |
| P-G26c Potts mechanism (runoff snapshot, symmetric fields) | βJ_snap ≥ βJ_s(q) | counts [8, 1, 1] (q = 3); βJ_snap = 2.80 [0.65, 4.65] vs βJ_s = 2.75; P(max ≥ 8 under independent symmetric voters) = 0.010 | **at threshold, inconclusive** |

Winner (most single-candidate declarations, from structural codes) = agent 17, DeepSeek-V3.2, matching the dataset's goal summary. The declared-vote universe is 10 named agents, not 6: vote messages also name non-candidates, e.g. ballot organizers.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | z_N2 = +6.4; held-out gain 5/5 folds |
| D unfitted predictions | 1 | sign by goal mode: supported (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode); vote jump predicted and observed |
| G ground truth | 1 | vote winner and runoff jump match the dataset's goal summary |

## Notes
- 2026-10-03 (round 1): the project labels (mostly ballot Google Docs) are not the consensus variable. The declared votes are. The pre-registered runoff-onset rule (≥ 2 'runoff' messages in a window) fired on day 1, long before the decisive vote at window ≈ 27, so P-G26a measured an early state.
