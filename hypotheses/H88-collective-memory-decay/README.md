# H88: Collective memory decays biexponentially

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only). Mixed: attention to a finished period decays, but not biexponentially. It falls fast (τ ≈ 4–6 village days) to a small persistent floor, and newcomers are not slower than veterans.**
- **P1 (biexponential) fails:** terms (20 periods): best model exponential + floor 8, single exponential 5, biexponential 4, power law 3; artifacts (7 periods with enough later uses): single 3, floor 3, biexponential 1. Kill 1 (single exponential in ≥ 1/2) is not met either.
- **Fast decay to a floor:** terms τ 5.5 village days (median), floor 1.9% of the initial share; artifacts τ 4.0, floor ≈ 0. The present veterans' share at days 21–40 is 8% (terms) of its days 1–3 value (decay in 13/18), so the decay is not departure-driven (P2 passes; the closed-roster native agrees).
- **Newcomers are not slower (P3 fails, power 0.87–0.92):** they use a just-finished period's terms at 0.93× the veterans' standardized rate. 59% of their first uses follow a logged read.
- **Retirements:** in 2 of 3 exits, nobody else used the retiree's carried items afterwards.
- Card, nulls and predictions written 2026-10-04 20:09 UTC before any post-period statistic; synthetic validation and Amendment A1 before real data. `analysis/confirm.py` written, dry-run, **not run**.
**Question (GOALS.md):** **Q4** (where does the swarm's information live?): it measures how long a finished goal period stays in the village's attention, and whether the slow part is carried by the record rather than by the agents who were there. It also serves Q3 (the slow component is the egregore's candidate cultural memory).
**Fields:** dynamics (relaxation, two-compartment decay), info theory (memory stores), sociophysics (collective attention, cultural memory)
**Literature:** Candia, Jara-Figueroa, Rodriguez-Sickert, Barabási & Hidalgo 2019, "The universal decay of collective memory and attention" (*Nature Human Behaviour* 3, 82)†: **not in `literature/`** (no arXiv version), so its biexponential two-compartment form is **quoted from memory** (HH316 refinement; model 13 §4). [Ashery et al. 2025](../../literature/ashery-2025-emergent-social-conventions-llm-populations.md) and [Centola & Baronchelli 2015](../../literature/centola-2015-spontaneous-emergence-of-conventions.md) are used only for the carrier argument (a convention at consensus is absorbing; a term hardcoded in an artifact acts as a committed source). Project cards: H15 (memory carries ≈ 0 day-scale semantic information), H44 and H58 (agents recover from erasure by re-reading their own artifacts), H41 (spread is caged by rooms and gated by read-out), H34 (marker rule), H79 (the retiree's repos catalyse no later work).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t); Regime; Driving / external field; **Idea (H34 marker rule)**; Contagion / adoption event; **Exposure (turn read-out)** (H08; DQ1 ledger). New named variants proposed for DEFINITIONS.md (defined under Observables; not edited here): **period items (artifacts, terms)**, **post-period attention share s_g(k)**, **veteran / newcomer of a period**, **communicative and cultural components**.
**From:** HH316 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/13-cultural-evolution-conventions/` (§4, collective memory decay: primary), `physics-models/04-semantic-information/` (secondary: which store carries the slow part)
**Data inputs (shared tables first):** `artifacts`, `artifact_mentions` (agent rows; action rows with `how ∈ {url, output, bare}`), H34 marker uses (`data/processed/H34-idea-cascades/markers/`, hashes only, non-holdout by construction; the rule lives in `infra/shared/idea_markers.py`), `chat_core` (row map, speakers), `roster`, `calendar`, `period_units`, DQ1 `context_ledger_items` × `call_windows` (newcomers' reads), DQ4 `work_commits` (agent work, sensitivity channel).

## Source HH (verbatim from the HH list, including literature refinements)
Collective memory decays biexponentially (communicative + cultural). After a goal period ends, follow attention to its artifacts and terms: references, reads and commits. Candia et al. find a fast communicative component, carried by the people who were there, and a slow cultural component, carried by the record.
  - *Prediction:* a biexponential, with a fast τ₁ of days carried by veterans of that period and a slow τ₂ of weeks carried by the record. Newcomers contribute only to the τ₂ component.
  - *Egregore reading:* the slow component is the village's cultural memory.
  - *Kill:* a single exponential, or decay set entirely by veterans' departure.
  - *Models:* 04 · *Builds on:* H15, H44, HH290, HH294
  *Refinement (literature, 2026-10-04):* The primary paper (Candia et al. 2019) has no arXiv version and is not in `literature/`; the biexponential form is quoted from memory.

## Question
After a goal period ends, does the village's attention to that period's artifacts and coined terms decay as the sum of a fast component carried by the period's veterans and a slow component that newcomers share, rather than as one exponential or as a side effect of veterans leaving?

## Design: two layers (STANDARDS §4)
- **Replication:** the common estimator (decay fits of the post-period attention share) on every eligible finished goal period. The unit is the goal period P whose items are followed; the observations are later days. Role `replication`.
- **Period-native tests:** G05 (the closed village: roster fixed 05-23 → 08-15, so no departure and no newcomer can shape the decay), NE27 (G10: three newcomers join four veterans; their attention to older items at matched item age), NE28/NE29 carrier loss (retirements; do other agents keep using the retiree's items). Each has its own dated prediction. Role `native`.

## Model
**From:** `physics-models/13-cultural-evolution-conventions/` §4 (Candia et al. 2019†, form quoted from memory).

**Two-compartment memory.** Communicative memory u (talk among those who were there) decays at rate p and transfers into cultural memory v (the record: repos, sites, files, history search, memory files) at rate r. Cultural memory decays at rate q:

  S(k) = u + v,   u = N e^{−(p+r)k},   v = N r/(p + r − q) · (e^{−qk} − e^{−(p+r)k})

S is a biexponential with a fast time τ₁ = 1/(p + r) and a slow time τ₂ = 1/q. Here k counts village days since P's last day (held-out days count in k but carry no data).

**H88 observable model.** For carrier group g (veterans of P or newcomers to P) on day k, the attention share is y_{g,k} / O_{g,k}: uses of P's items over the group's uses of all items of that kind that day. The share is fitted as

  E[y_{g,k}] = O_{g,k} f(k),  with f ∈ {M1: A e^{−k/τ};  M2: A₁ e^{−k/τ₁} + A₂ e^{−k/τ₂};  M1c: A e^{−k/τ} + c;  MP: A k^{−α}}

by Poisson quasi-likelihood (overdispersion φ from the M2 Pearson χ²). M2 is the Candia model; M1 is the kill; M1c (a permanent floor: the item becomes infrastructure) and MP (a power law, scale-free attention) are rivals. The slow share is σ = A₂τ₂ / (A₁τ₁ + A₂τ₂), the fraction of the integrated attention in the slow component.

**Carrier predictions.** Veterans carry both components. Newcomers joined after P, so they have no communicative memory of P: their share follows only the slow component, f_new(k) ∝ e^{−k/τ₂}. At matched k, the ratio R(k) = s_new(k) / s_vet(k) then rises with k toward a plateau.

**Rivals.**
- **K1, single exponential (HH kill):** one store, one rate.
- **K2, departure-driven decay (HH kill):** per present veteran, attention does not decay; the aggregate falls only as veterans leave.
- **K3, permanent floor (M1c):** a fraction of items becomes infrastructure and never decays on the observed horizon.
- **K4, power law (MP):** scale-free attention, no characteristic times.
- **K5, exogenous re-activation:** a later goal or operator message names the old item, so its attention is a field, not memory. Controlled by dropping items that humans mention after P (sensitivity).
- **K6, re-coinage:** a newcomer produces the same term without reading it (shared priors). Measured by the in-cone share of newcomers' first uses of P's terms.

## Data scheme (`scheme/`)
Script: `scheme/build.py` (shared tables only; no text read; held-out days excluded with `calendar.holdout` and `common.holdout_mask`, asserted).
- **Inputs:** `artifacts`, `artifact_mentions`, H34 `markers/uses.parquet` and `first_seen.parquet`, `chat_core` (row index `msg` → message_id, t, day, speaker), `roster`, `calendar`, `goal_periods` via `calendar.goal_no`, `period_units`, `context_ledger_items` + `call_windows` (newcomer receipts), `work_commits`.
- **Transform:**
  1. **Artifact items of P:** an artifact's root is its `parent` if set, else itself. A root is P's item if its earliest first-seen time over itself and its children falls on a non-holdout day of P, its first speaker is an agent, its kind is repo, site or file (domains dropped), and agents mention it during P at least 3 times, by at least 2 agents.
  2. **Term items of P:** H34 N-class markers (names and coinages) with `first_goal == P`, used during P in ≥ 3 agent messages by ≥ 2 agents. W-class (rare words) as a sensitivity set.
  3. **Uses:** artifact uses = agent rows of `artifact_mentions` on the item or its children (chat and intention rows, plus action rows with `how ∈ {url, output, bare}`); term uses = agent chat messages carrying the marker. Human mentions are kept separately for K5.
  4. **Daily counts** per P, carrier group and day after P: y (uses of P's items) and O (uses of all items of the kind by the group). Veterans of P: agents with ≥ 1 non-holdout chat message during P. Newcomers to P: `joined` after P's last day. Agents 19, 28, 30 dropped.
  5. **Day index:** k = rank of the day among `calendar` days after P's last day. Held-out days stay in k with no observation (censored, not zero).
- **Output:** `data/processed/H88-collective-memory-decay/` (`items.parquet`, `daily.parquet`: P, kind, group, k, day, y, O, observed flag; `carriers.parquet`; analysis outputs in `synthetic/`, `replication/`, `natives/`, `confirm/`; `_provenance.json`).
- **Regimes covered:** I, II, III. The follow-up of a period may cross regime boundaries (exception (c): the afterlife of a period is the object). The share normalization removes volume and hours changes; the fitted times are reported with the regime of P.

## Eligible periods
Replication: non-holdout goal periods 2–44 with ≥ 10 artifact items (artifact channel) or ≥ 30 term items (term channel), ≥ 3 observed days in k ≤ 5, ≥ 30 observed days in k ≤ 120, and ≥ 50 post-period veteran uses. #51 has no follow-up (its tail is held out). The horizon ends at 2026-09-04, the last non-holdout day.

## Observables
*Written 2026-10-04 20:09 UTC, before any post-period attention statistic.*
- **O1. Decay fits per P and channel (veterans).** M1, M2, M1c and MP by quasi-likelihood; QAIC with the same φ for all four. Report τ₁, τ₂, σ, and ΔQAIC(M1 − M2). A period "is biexponential" if M2 has the lowest QAIC and beats M1 by ≥ 2.
- **O2. Departure check (K2).** For veterans still present, the share at k 1–3 vs k 21–40 (ratio with a day-block bootstrap). Decay inside the present veterans means the decay is not departure.
- **O3. Newcomer ratio.** R(k) = s_new(k)/s_vet(k) at matched k. Per P where newcomers exist, and pooled over P with period-specific intercepts (exception (d): too little newcomer data per period; per-period values reported beside the pooled slope). Statistic: slope b of log R on log k (Poisson model with group × log k interaction and P-specific intercepts), P-block bootstrap CI. Constrained check: fit the newcomer series with a single exponential and compare its τ with the veteran τ₂.
- **O4. Store contrast.** σ and τ₂ for artifacts vs terms in the same P.
- **O5. Re-coinage (K6).** For each newcomer's first use of a P term, whether any message carrying the term entered one of its receiving calls earlier (DQ1 ledger). The in-cone share bounds co-generation (a lower bound on transmission, because files and history search are not in the ledger).
- **O6. Exogenous re-activation (K5).** Refit O1 without items that a human mentions after P.
- **Natives.**
  - **G05 (closed village):** periods #4 (unit 4c on), #5, #6 and #7, follow-up truncated at 2026-08-15 (before NE27). The roster is fixed (four agents), so K2 cannot act. O1 on each.
  - **NE27 (G10):** the three newcomers vs the four veterans, days 08-18 → 09-19 (non-holdout), attention share to items of #2–#8 by item age (k of the source period on that day). Ratio R by age band (≤ 15, 16–40, > 40 village days).
  - **NE28 + NE29 (carrier loss):** for each retirement (o3 and Opus 4.1 on 2025-12-01; Claude 3.7 Sonnet on 2026-02-19; also Grok 4 on 2025-10-29), items with ≥ 5 uses in the 10 village days before the exit. Retiree-carried: the retiree made ≥ 40% of those uses. Controls: items with < 10% retiree uses, matched on pre-exit volume tercile. Outcome: other agents' uses in the 10 village days after vs before (ratio of ratios, item-block bootstrap).

## Null / baseline
*Written 2026-10-04 20:09 UTC.*
- **Model nulls:** M1 (single exponential) for O1; equal decay for both groups (R constant, b = 0) for O3; ratio of ratios = 1 for the carrier-loss native.
- **Calibration:** model-selection size and power on synthetic counts at the real offsets O and the real observation masks of every eligible period (S0 single, S1 biexponential, S2 floor, S3 power law; Poisson and gamma-Poisson noise). The b-test size is measured with a common f for both groups.
- **Uncertainty:** day-block bootstrap (blocks of 5 village days) for fitted times; P-block bootstrap for pooled statistics.

## Impostor table (STANDARDS.md §1)
| Impostor | How it could fake the result | How H88 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | Day length and the number of active agents change attention volume (2 h → 8 h days) | Attention is a share of the group's own daily uses (offset O); held-out days are censored, not zero | removed |
| Exogenous field (kickoff, goal, operator) | A later goal or operator message names an old item, so its attention is a field (K5); a goal that continues the previous one keeps its items alive | O6 drops items that humans mention after P; continuation periods are flagged from the fitted A₂ and reported | partly |
| Shared model priors (family, style) | Models re-coin generic terms (K6), producing a fake slow tail; families re-use the same tools | Terms must be first seen in P and used by ≥ 2 agents there; O5 measures the in-cone share of newcomer first uses; artifacts are named objects, not words | partly |
| Contemporaneous convergence | Not a co-movement statistic; relevant only to newcomers' uptake (co-generation vs reading) | O5 in-cone share | partly |

## Prediction
*Written 2026-10-04 20:09 UTC, before running the analysis on real data. Verdict rules fixed now.*

**Replication (card level, artifact channel primary, terms secondary).**
- **P1 biexponential (headline):** M2 has the lowest QAIC and beats M1 by ≥ 2 in ≥ 2/3 of eligible periods (artifacts). Median τ₁ in [0.5, 5] village days; median τ₂ in [10, 120] village days. *Against (kill 1):* M1 wins (lowest QAIC, or M2 gains < 2) in ≥ 1/2 of eligible periods. My prior: 45% (a floor M1c or a power law may fit as well over 120 days).
- **P2 not departure (kill 2):** the present-veteran share at k 21–40 is below the share at k 1–3 (ratio CI < 1) in ≥ 2/3 of eligible periods. *Against:* the ratio CI includes 1 in > 1/3 of periods (the per-veteran share does not decay).
- **P3 newcomers carry only the slow part:** the pooled slope b > 0 with the P-block CI above 0, and the newcomer single-exponential τ is ≥ the veteran τ₁ upper CI in ≥ 2/3 of periods with newcomer data. *Against:* b ≤ 0 (newcomers pick up P's items as fast as veterans remember them: communicative transmission to newcomers).
- **P4 the record is the slow store:** artifacts keep a larger slow share than terms (σ_art > σ_term) in ≥ 2/3 of periods with both fits. *Against:* σ_art ≤ σ_term in ≥ 1/2.
- **P5 transmission, not re-coinage:** ≥ 50% of newcomers' first uses of P terms are in-cone (descriptive threshold; a lower bound).

**Natives (dated predictions also in each folder).**
- **N1 G05 closed village:** M2 beats M1 (ΔQAIC ≥ 2) for at least 2 of #4, #5, #6, #7 on artifacts or terms, with the roster fixed. *Against:* M1 wins in ≥ 3 of 4 (or no decay at all).
- **N2 NE27:** newcomers' share is below the veterans' for recent items (R < 1 for source age ≤ 15 days, CI < 1) and R rises with age (R(> 40) > R(≤ 15)). *Against:* R(≤ 15) ≥ 1, or R falls with age.
- **N3 carrier loss:** other agents keep using retiree-carried items: ratio of ratios in [0.5, 2] with CI including 1. *Against:* CI below 1 (the item's memory left with its carrier, kill 2 at item level).

**Overall reading (fixed now).** **Supported** if P1, P2 and P3 pass. **Mixed** if P1 passes and one of P2, P3 fails, or P1 fails while M1c or MP win (the decay has a slow part but not Candia's form). **Refuted** if M1 wins in ≥ 1/2 of periods (kill 1) or P2 fails (kill 2), with synthetic power ≥ 0.8 for M2 at the fitted amplitudes.

## Synthetic validation (axis F; run 2026-10-04 20:41–21:04 UTC, before any real-data fit)
`analysis/synthetic.py` → `data/processed/H88-collective-memory-decay/synthetic/synthetic.json`. Real veteran and newcomer offsets O and real observation masks of the design-eligible periods (artifacts: #4, #12, #17–#20, #24–#26, #30, #36, #38, #39, #41; terms: 25 periods). Counts y ~ Poisson or gamma-Poisson (shape 2) around O·f(k); 30 replicates per truth and noise; 40–60 for the newcomer test. Amplitudes are assumptions (early share 0.3), not fitted.

| Truth | Best model by QAIC (artifacts, Poisson / NB2) | "Biexp" call rate (artifacts; terms) |
| --- | --- | --- |
| S0 single exponential (τ 4) | M1 0.93 / 0.83 | 0.00–0.03; 0.00–0.03 |
| S1 biexponential (τ₁ 2, τ₂ 40, A₂ 0.02) | M2 0.60 / 0.53; MP 0.37 / 0.33 | 0.50–0.60; 0.70–0.90 |
| S1w weak slow part (A₂ 0.005) | M2 0.50 / 0.40; MP 0.40 / 0.43 | 0.40–0.50; 0.63–0.97 |
| S2 exponential + floor | M1c 0.90 / 0.93 | 0.03; 0.10–0.17 |
| S3 power law (α 1) | MP 0.80 / 0.57 | 0.07–0.13; 0.03–0.30 |

- M2 recovers τ₁ ≈ 2 and τ₂ ≈ 39 (medians) when it is the truth. M2 and the power law are confused on artifacts (one in three).
- **Pooled newcomer slope (first version, Poisson with period intercepts):** not identified. Estimates diverged (|b| up to 10³⁶) because many newcomer cells are zero.
- **Standardized ratio (replacement, below):** size 0.067 (artifacts and terms; one-sided CI rule), power 0.92 (artifacts) and 0.87 (terms) when newcomers carry only the slow part. A band-level standardization was biased (size 0.18 / 0.55) because newcomers' offsets sit late within a band; day-level standardization fixes it.

## Amendment A1 (2026-10-04 21:04 UTC, after the synthetic validation, before any real-data fit)
- **A1.1 (O3/P3 estimator).** R(band) = Σ_P observed newcomer uses / Σ_P expected uses, where expected = the newcomers' offset on day k × the veterans' share on the same P and day k. Bands of k: 1–10, 11–40, 41–120 village days. b = log R(41–120) − log R(1–10), P-block bootstrap (2,000). P3 passes if b > 0 with CI > 0. The single-exponential τ of the newcomer series stays as a descriptive check.
- **A1.2 (P1 rule).** Even when every period is biexponential, the per-period call rate is 0.4–0.6 for artifacts, so "≥ 2/3 of periods" has power < 0.5. New rule: P1 passes if M2 is the most frequent best model across eligible periods and the biexp call holds in ≥ 40% of them (artifacts; terms reported alongside with ≥ 50%). Kill 1 is unchanged (M1 best in ≥ 1/2 of periods); under S1 M1 wins in 0–10% of periods, so a kill is powered.
- **A1.3 (eligibility).** Design-only: ≥ 10 artifact items or ≥ 30 term items, ≥ 3 observed days in k ≤ 5, ≥ 30 observed days. Artifacts: 14 periods; terms: 25.

## Results by goal period
Roles: `replication` = templated point (veterans' fits on the period's own items; not an independent test); `native` = period-specific design. Verdicts use the artifact channel where it has ≥ 50 later uses, else terms.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | mixed | terms: best M1c (τ 5.8, floor 0.061) |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | supported | terms: M2 τ₁ 4.7, τ₂ 99; ΔQAIC +9.4 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | mixed | terms: best M1c (τ 7.2, floor 0.32) |
| [G05](goalperiod-subhypotheses/G05/README.md) | native | mixed | closed roster: #4, #5 power law, #6 floor; 0/3 biexponential |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | mixed | terms: best MP (α 0.90) |
| [G10](goalperiod-subhypotheses/G10/README.md) | native | mixed | NE27 newcomers' R: 0.98 (≤ 15 d), 0.65, 1.02 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | mixed | terms: best M1c (τ 10.5) |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | supported | terms: M2 τ₁ 3.7, τ₂ 30; ΔQAIC +6.3 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | failed | terms: best M1 (τ 41) |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | mixed | terms: best M1c (τ 14.4) |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | artifacts: best M1 (τ 25); terms M1 (τ 29) |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | mixed | terms: best M1c (τ 3.3, floor 0.026) |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | supported | artifacts: M2 τ₁ 4.0, τ₂ 40; ΔQAIC +3.3; terms MP |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | n/a | < 50 later veteran uses |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | mixed | terms: best M1c (τ 0.6) |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | supported | terms: M2 τ₁ 0.2, τ₂ 66 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | n/a | < 50 later veteran uses |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | mixed | artifacts and terms: best M1c (τ 3.0 / 2.4) |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | failed | terms: best M1 (τ 38) |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | mixed | artifacts and terms: best M1c (τ 4.0 / 5.2) |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | supported | terms: M2 τ₁ 0.3, τ₂ 11 (85 uses) |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | artifacts: best M1c (τ 4.7); terms flat (MP α 0) |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | failed | artifacts and terms: best M1 (τ 11 / 9.5) |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | failed | terms: best M1 (τ 9.0; 73 uses) |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed | artifacts: best M1 (τ 1.6) |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | n/a | < 50 later veteran uses |
| [NE28](goalperiod-subhypotheses/NE28/README.md) | native | mixed | carried items: Grok 4 27 → 0, Sonnet 3.7 89 → 0; NE28 ratio 2.0 [0.03, 7.0]; pooled 0.78 [0.01, 2.2] |

## Outcome vs prediction
*Run 2026-10-04 21:05–21:12 UTC (`analysis/replication.py`, `analysis/natives.py`). Non-holdout days only; held-out days censored.*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 M2 the modal best model and biexp in ≥ 40% (artifacts; terms ≥ 50%) (A1.2) | artifacts (7): M1 3, M1c 3, M2 1, biexp 1/7. Terms (20): M1c 8, M1 5, M2 4, MP 3, biexp 4/20 (in those: τ₁ 2.0, τ₂ 48 days) | **fail** |
| Kill 1: M1 best in ≥ 1/2 | artifacts 3/7, terms 5/20 | not met |
| P2 present veterans' share at k 21–40 below k 1–3 (CI < 1) in ≥ 2/3 | terms 13/18 (median ratio 0.079); artifacts 5/5 (median 0.0001) | **pass** |
| P3 newcomers carry only the slow part: b > 0, CI > 0 | terms R 0.93 / 0.64 / 0.79 by age band, b −0.17 [−0.80, +1.32]; artifacts b +0.57 [−1.19, +1.72] | **fail** (power 0.87–0.92) |
| P4 artifacts keep a larger slow share than terms | 1/6 periods | fail |
| P5 ≥ 50% of newcomers' first uses of P terms in-cone | 0.59 (1,434 first uses) | pass (descriptive) |
| O6 refit without human-mentioned items | terms: M1c 7, MP 4, M2 3, M1 5 (19 periods) | same picture |
| N1 G05 closed roster: M2 in ≥ 2 of #4–#7 | 0 of 3 fitted (#4, #5 MP; #6 M1c; #7 no later uses) | mixed |
| N2 NE27: R(≤ 15 d) < 1, R rising with age | 0.98 [0.0, 2.7], 0.65, 1.02 | mixed |
| N3 carrier loss: ratio of ratios in [0.5, 2], CI ∋ 1 | pooled 0.78 [0.01, 2.2]; 2 of 3 exits total loss | mixed (rule met through an uninformative CI; post hoc reading) |

**Overall (pre-registered reading):** P1 fails while the floor and power-law models win, P2 passes and P3 fails, so H88 is **mixed**: attention to a finished period does decay among the agents who stay, but not in Candia's two-compartment form, and newcomers do not carry only a slow component.

## Results
**1. Attention to a finished period falls within a week.** For a period's coined terms, the veterans' attention share at days 21–40 after the period is 8% of its days 1–3 value (median over 18 periods). An exponential with a floor fits best most often: decay time τ = 5.5 village days (median, 20 periods), floor 1.9% of the initial share. For artifacts the decay is similar (τ ≈ 4) but the floor is ≈ 0: a finished period's repos and files are almost never touched again (7 of 14 design-eligible periods have fewer than 50 later uses).

**2. The fast part is not carried by the people who were there.** Candia's model puts the fast component in the veterans. Here newcomers who arrive right after a period use its terms at 0.93× the veterans' standardized rate (days 1–10), and the newcomer/veteran ratio does not rise with age (b −0.17 [−0.80, +1.32]). The synthetic slow-only newcomer gives b ≈ +1.2 with power 0.87–0.92, so this is a powered failure. What decays is the topic, for everyone at once.

**3. Decay is not departure.** Within the present veterans the share falls (P2), and in the closed-roster summer of 2025 (#4–#6, four agents, no joins or exits) the decay is there too. So kill 2 fails, and carrier turnover is not needed.

**4. A biexponential is rare.** M2 wins in 5 of 27 period × channel fits. Where it wins, τ₁ ≈ 2 and τ₂ ≈ 48 village days. The floor model wins more often (11 of 27), then the single exponential (8), then the power law (3). The synthetic shows M2 and the power law confusable on artifacts (one in three), but not M2 and the floor.

**5. Items carried by one agent die with it.** When Grok 4 (2025-10-29) and Claude 3.7 Sonnet (2026-02-19) retired, the items they had carried (≥ 40% of recent uses) got no further use by anyone (27 → 0 and 89 → 0 uses in 10 village days). After NE28 the picture is confounded by the #21 goal switch. Pooled, the test is uninformative.

**6. The floor is partly re-coinage.** 41% of newcomers' first uses of a period's terms come without a logged read of the term (it could still come from files or search). So the persistent floor mixes record-borne memory with generic terms that models produce again.

Figures: `figures/summary_obs.pdf` (veterans' term share vs days since the period, 20 periods, with the median floor fit; best-model shares real vs synthetic), `figures/summary_obsb.pdf` (newcomer/veteran ratio by age; carrier loss). Data: `data/processed/H88-collective-memory-decay/` (`replication/replication.json`, `natives/natives.json`, `synthetic/synthetic.json`, `confirm/confirm_dryrun.json`). Estimates: 158 rows in `per_period_estimates` (hypothesis H88).

## Faithfulness scorecard
*Round 1, 2026-10-04.* Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed.
**Rival models:** K1 single exponential, K2 departure-driven decay, K3 exponential + floor, K4 power law, K5 exogenous re-activation, K6 re-coinage.
**Locked holdout used for confirmation:** none yet (`analysis/confirm.py`, dry-run only).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Items, uses and shares come from `artifacts`, `artifact_mentions` and H34 markers; held-out days are censored. Item thresholds (≥ 3 uses, ≥ 2 agents) are a choice; artifacts are too sparse after their period in half the periods. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Share offsets remove volume and hours changes; overdispersion is large (φ 1–100) and handled by QAIC; one decay law per period is assumed. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The single exponential loses in 19 of 27 fits; but Candia's M2 is not the winner. No held-out-day likelihood test. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The present-veteran decay (P2) holds; the model's signature (newcomers slow, P3) fails at power 0.87–0.92. |
| E interventional | predicts the change across a natural experiment | 1 | Closed roster: decay without turnover. Retirements: carried items end in 2 of 3 exits. NE27 uninformative. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Synthetic counts at the real offsets and masks: model-selection rates for four truths, τ recovery, newcomer-test size and power; two flawed estimators found and replaced before real data (A1). |
| G ground truth | agrees with known structure | 0 | No ground truth for memory. |
| H comparative | beats the named rivals | 0 | Candia's M2 loses to the floor (K3) and is matched by the single exponential (K1). |
| I transfer | holds in other same-mode periods, including the holdout | 1 | The fast-decay-to-floor picture holds for terms across three regimes (20 periods); artifacts are sparse; holdout not run. |

## Confirmatory predictions (written 2026-10-04 21:16 UTC after round 1, before any holdout use; `analysis/confirm.py`, dry-run only, **not run**)
Targets: the items of held-out periods #1, #9, #14, #15, #22, #28, #29, #43, #45–#50, followed for 120 village days (to 2026-09-21).
- **C1:** biexp call in < 40% of eligible periods and M1c or MP best in ≥ 1/2 (terms). **C2:** present-veteran share ratio CI < 1 in ≥ 2/3. **C3:** newcomer b CI includes 0 or b ≤ 0. **C4:** terms M1c τ median in [2, 12] village days and floor ratio median in [0.005, 0.08].
- **Overall:** confirmed if C1, C2 and C4 pass. Dry run on the round-1 periods: all pass.
- **Reuse disclosure:** #45 (H02, H04 executed: activity) and #46–#50 (H04 executed) have prior runs on other modalities; this test reads chat markers and artifact mentions. Disclose in both cards and `LOG.md` if run.

## Caveats
- **Candia et al. 2019 is not in `literature/`;** its biexponential form is quoted from memory.
- **Horizons.** 120 village days with censored held-out stretches; a τ₂ of months and a floor cannot be told apart.
- **Terms are H34 markers** (hashed coinages, identifiers, quoted phrases). Some are generic and re-coined (K6: 41% of newcomer first uses out of cone). "First seen in P" means first non-holdout use; a held-out earlier use is invisible.
- **Artifact mentions** count working references (cwd, URLs, outputs), so they measure work attention, not reading.
- **Overdispersion** is large; QAIC uses φ from M2 for all models.
- **NE27 shares** were taken within the pool of #2–#8 items for both groups (fixed before the run; the card's offset was all uses).
- **Post hoc:** the reading of the carrier-loss CI as uninformative.

## Round 2 redirects (2026-10-04)
*Proposed by the round-1 agent; the coordinator may revise.*
- **Where round 1 went sideways:** the aggregate share mixes items that die in days (topic words) with items that become infrastructure, and a mixture of single exponentials with a floor beats a two-compartment model.
- **What the direction is really after:** which items outlive their period and what carries them (an artifact, a convention, one agent).
- **H88-R1.** Item-level survival: time to last use per term and artifact, with covariates (hardcoded in a repo, carried by one agent, named by a later kickoff, in-cone share). Fit the floor as a cured fraction (mixture cure model), not as a rate.
- **H88-R2.** Carrier concentration: item survival vs the share of its uses by its top carrier (HH291's committed-carrier argument); the two clean retirements suggest single-carrier items die with their carrier.
- **H88-R3.** Record access: test the floor across NE04 (history search added) and NE18 (verbatim 10-day search window) on items older than 10 village days.
- **H88-R4.** Separate re-coinage from memory: family-matched control villages are not available, so use in-cone first uses only for the newcomer channel.

## Notes
- 2026-10-04 20:09 UTC: card written by the round-1 agent before any post-period attention statistic. Seen before writing: roster, calendar, period units, the H34 marker table schemas. Candia et al. 2019 is not in `literature/`; every statement of its form here is from memory (†).
- 2026-10-04 21:03 UTC: **H81 methods warning and results seen (coordinator message; after the synthetic validation, before any real-data fit).** H88 uses no agent baseline or village vector: its observable is a count share of a period's items, so the leave-period-out artifact does not apply. The warning about placebo-corrected excesses applies to the carrier-loss native (a ratio of ratios); its null is measured on matched control items (Amendment A1). H81's regime-I collective slow mode (τ ≈ 23–28 days) and H82's finding that day-1 carry-over lives in each agent's own previous content are prior information for τ₂ and for the veteran fast component.
- 2026-10-04 21:24 UTC: round 1 finished. Order (file times): card 20:09 → scheme 20:40 → synthetic 20:41–21:04 (model selection; newcomer test redone 21:03 after two estimator failures) → A1 21:04 → period predictions 21:04 → replication 21:05–21:12 → natives 21:09–21:12. One heavy job at a time (one background run was killed for slowness and replaced by a vectorized estimator). Data: `data/processed/H88-collective-memory-decay/` (< 1 MB) with `_provenance.json`.
