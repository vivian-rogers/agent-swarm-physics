# H107: Does the room split grow from zero (an instability) or appear at once (a hidden field)?

**Status:** exploratory round 1 done (2026-10-04, non-holdout only): **mixed.** Neither pure symmetry breaking nor a hidden field. In two identical-kickoff periods (#37, #39) the room split starts near zero on day 1 (r₁ 0.09, −0.09; gte 0.15, 0.43) and grows over the week. In #41 and #42 it is already at 70–90% of its final size on day 1, but the day-1 direction is only half aligned with the final one (c₁ 0.50–0.59). The members' pre-period repos set the day-1 direction only in #42 (f_repo 0.34, p 0.002; gte 0.39), which fails that period by the HH kill. The positive control is half met: #44's kickoff field gives a step along the final direction (π₁ 0.73), #38's gives a full-size step whose direction is only half kept (π₁ 0.53), so the onset clauses are inconclusive at card level. Card and predictions written 2026-10-04 21:24–21:28 UTC, before any H107 statistic on real data; Amendment 1 (21:37 UTC) after the synthetic, before real data. `analysis/confirm.py` frozen and dry-run, not run. Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH337.
**Question (GOALS.md):** **Q2** (what is field and what is coupling: is H100's "spontaneous" room split a hidden field, the work each room inherits from its members) with **Q3** (collective order beyond fields: is there a room instability that starts from zero).
**Fields:** stat mech (spontaneous vs explicit symmetry breaking; onset of order after a quench: nucleation and coarsening vs a field step), sociophysics (group divergence from inherited work), econometrics analogue (a field covariate in an event-time profile)
**Literature:** `physics-models/11-vector-spins/README.md` (soft-spin O(n); Goldstone and transverse response), `physics-models/10-potts/README.md` (rooms as Potts domains; a field on project states). Project cards: H100 (spontaneous share f_spont 0.58–0.91; no remanence; movers adopt within a day), H102 (two domains where rooms do different work; sharp wall), H47 (#41 rooms separated from day 0), H48 (content settles within hours of a kickoff, τ ≈ 2–4.5 h), H93 (an unmodelled assignment field fakes bistability), H58/H70 (agent + own artifact), H91 (content modes drift ~1 SD a day).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field; Interaction (broadcast); Agent state, vector variant; H100/H102 named variants **room of a statement**, **room of an agent-day**, **day-centred agent vector** (here centred per time bin), **room separation S**, **relabel excess Q**, **agent constant â_i (leave-period-out)**, **field share f_field**. New named variants proposed here (defined under Observables; DEFINITIONS.md not edited): **bin-excess separation E(b)**, **excess cross-product C(b, b′)**, **onset ratio r₁**, **disattenuated onset cosine c₁**, **onset projection π₁**, **inherited repo field u_repo**, **carried-content field u_prev**, **work persistence κ_w**.
**From:** HH337 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/` (primary), `physics-models/10-potts/` (secondary: the inherited repo field is a Potts field on project states)
**Data inputs (shared tables first):** `embeddings/statements.parquet` + `statements_style_resid32_{bge_small,gte_modernbert}.npy` (primary) and `statements_white32_*` (variant); `rooms_timeline` (null `t_end` → +inf); `chat_core`; `embeddings/chat_index`, `intentions_index`; DQ4 `work_commits`; `artifacts`, `artifact_mentions` (strict `how ∈ {url, output, bare}`); `embeddings/goals.parquet` + `goal_vectors*` (`kickoff_room`); `period_units`; `roster`; `hypotheses/holdout.json` via `holdout_mask`. No text is read.

## Source HH (verbatim from the HH list, including refinements)
- **HH337 · Does the room split grow from zero (an instability) or appear at once (a hidden field)?** H100 found that two rooms with identical kickoffs still diverge (Q_spont up to 4.2 in #41), but the spontaneous share is a residual. True spontaneous symmetry breaking starts at zero separation. The separation then grows, and its direction is chosen by early fluctuations (nucleation, then coarsening). A hidden field, such as the work each room inherits, gives full separation on day 1, along a direction that the members' previous repos predict.
  - *Prediction (SSB):* in H100's identical-kickoff periods, the day-1 separation is ≤ 0.3 of the period's final separation and grows monotonically. The day-1 direction aligns with the final direction at |cos| < 0.5. The members' previous-period repo labels (DQ4) do not predict the direction.
  - *Check:* H100's cross-fitted separation S(d) and relabel excess per active day (or half-day). Correlate the direction Δ(d) with Δ(final). Predict Δ from a Potts field built from each room's pre-period repos (H100-R3 machinery).
  - *Kill (SSB):* S(1) ≥ 0.8 S_final with day-1 direction cos ≥ 0.7, or the pre-period repos predict the direction. The "spontaneous" share is then a hidden field.
  - *Impostors:* exogenous: identical kickoffs plus the repo field as an explicit covariate. Priors: agent constants removed (H100). Scheduler: n/a. Convergence: growth alone cannot separate coupling from a self-made room drive; HH339 does that.
  - *Models:* 11, 10 · *Builds on:* H100, H102, H93

## Question
When two rooms get identical instructions, does their content difference start at zero on the first day and grow (an instability whose direction early fluctuations choose), or is it already at full size on day 1, along a direction that the work the members bring from the previous period predicts (a hidden field)?

## Design: two layers (STANDARDS §4)
- **Eligible periods.** Non-holdout #best/#rest periods with ≥ 3 one-room agents per room: G35–G39, G41, G42, G44 (H100's set). #40 (one merged room) and 51g (#focus has 2 agents) are not eligible. #43 is held out, so G44's pre-period is #42.
- **Replication** (role `replication`): the onset estimator (O1–O4) on the identical-kickoff periods with a regime-consistent day 1: **G37, G39, G41, G42**. **G36** runs as descriptive only: its kickoff day (03-23) is regime II and its other days regime III, so day 1 and the final days live in different whitening bases.
- **Natives** (role `native`), each with its own dated prediction:
  - **G38 + G44** (room-specific kickoffs): the positive control. A known field should give a step: full separation on day 1 along the final direction. If the estimator cannot see this step, the identical-period verdicts are inconclusive.
  - **G35** (the RPG fork week, NE15: each room works on its own fork from day 1): a known *work* field. Regime II, so no agent constants (composition stays in).
  - **G39** (the 04-27 reshuffle): half of #38's #best moved to #rest, carrying 17 days of room-specific #38 work. The inherited repo field is strongest here.
  - **G41** (the NE42 re-split, 05-11): rooms re-form with #39's partition after a merged week. Does day 1 recall #39's direction (room memory) or #40's work?
- **Exceptions (CLAUDE.md).** (b) agent constants â_i come from other periods (invariance checked by H100: r 0.49 vs null 0.14). (c) G39 and G41 compare across a boundary (the transition is the object).

## Model
**From:** `physics-models/11-vector-spins/` (linear soft-spin O(n), n = 32), with `physics-models/10-potts/` for the inherited field.

Content of agent i in time bin b of period P (room r): x_{i,b} ∈ ℝ³², bin-centred (minus the mean over all agents present in b) and minus the agent constant â_i:

  x_{i,b} = b_{r}(t_b) + η_{i,b},   Δ(t) = b_best(t) − b_rest(t)

- **Hidden field (explicit or inherited).** Δ(t) = χ h + δ(t) with h fixed from t = 0: the room kickoff difference (#38, #44), the fork (#35), or the inherited work field h = h_best − h_rest. The Potts form: room r's members carry pre-period repo shares p_r(σ) over repos σ, and h_r = Σ_σ p_r(σ) v_σ with v_σ the repo's content vector. **Signature:** |Δ(1)|² ≈ |Δ_final|², Δ(1) ∥ Δ_final, and Δ ∥ u_repo.
- **Spontaneous symmetry breaking after a quench.** With within-room coupling J above threshold and no field, |Δ(t)| grows from the finite-N fluctuation level, |Δ(t)|² ≈ |Δ_F|² (1 − e^{−t/τ_g})² for t ≳ a nucleation time, and the direction is set by early fluctuations. Before saturation the direction still diffuses (D ∝ 1/(N|Δ|²); H108), so coarsening can rotate it. **Signature:** E(1) ≪ E_F, growth over days, cos(Δ(1), Δ_F) < 1, no alignment with u_repo.
- **Fast instability.** The same as SSB with τ_g ≈ hours (H48: content settles in τ ≈ 2–4.5 h). At day resolution it looks like a step. Only the half-day and hour bins of day 1 can separate it from a field present at t = 0.

**Rivals.**
- **R-field (hidden field):** HH337's kill. Step onset along the inherited work direction.
- **R-SSB (slow instability):** growth over days, direction chosen early.
- **R-fast (fast instability):** step at day resolution, growth inside day 1, direction not along u_repo.
- **R-comp (composition):** a step along the members' constants. Removed by â_i (H100: f_comp 0.03–0.18 where rooms separate).

## Data scheme (`scheme/`)
`scheme/build.py` → `data/processed/H107-room-split-onset/` (≤ 20 MB, `_provenance.json`). Non-holdout rows only, asserted with `holdout_mask`. No vectors are copied: the scheme stores row indices into the shared statement arrays.
- **Statements** (`statements.parquet`): every non-holdout agent statement (chat and intentions) of goals #33–#51, Claude Code agent excluded, with `srow` (row in the shared `statements_*` arrays), agent, t, PT day, goal, unit, regime, `win30`, **room at the statement** (chat: message room; intentions: as-of `rooms_timeline`, null `t_end` → +inf; the H100/H102 rule, copied), the agent's **room of the day** (majority room) and `half` (0: `win30` 0–3, the first 2 h of the day; 1: later), and a statement parity within the agent-day (odd/even, for split halves).
- **Repo mentions** (`repo_mentions.parquet`): strict agent `artifact_mentions` (chat or intention source) mapped to statement rows, with files and sites mapped to their parent repo; artifact id, repo name, t, `srow`.
- **Agent work** (`agent_repo_period.parquet`): DQ4 work commits with `author_kind == agent`, not automated, not imported, per (goal, agent, repo): distinct commit hashes. The canonical filter is not applied (fork commits whose hash first appeared in the parent repo count; infra Known issues).
- **Fields** (`fields.parquet` + `fields_<model>.npy`): whitened room kickoff vectors and per-room operator-message means (H100's rule, copied).
- **Regimes covered:** II (#35, #36a) and III (#36b onward). #51 rows serve only the agent constants.

## Observables
*Written 2026-10-04 ~21:27 UTC, before any H107 statistic on real data.* Primary instrument: bge style_resid; gte reported alongside. Agent vectors per bin are means of unit statement vectors (≥ 2 statements), bin-centred, minus â_i. â_i = leave-period-out agent constant (H100's rule) with **both P and its pre-period P⁻ left out** (so the carried work is not removed). Agents in two rooms within the period are dropped (H100's rule).
- **Time bins.** Days d = 1…n of the period; half-days (d, h) with h = 0 the first two active hours. Final block F = the last ⌈n/3⌉ days (#37: day 3; #38: last 6 days).
- **O1 Bin-excess separation E(b) and excess cross-product C(b, b′).** Δ(b) = mean of #best agents present in b − mean of #rest agents present in b. **C(b, b′) = Δ(b)·Δ(b′) − ⟨Δ_π(b)·Δ_π(b′)⟩_π**, where π runs over 2,000 **joint** relabels of the period's agents (room sizes kept; the same π in every bin; infra Known issue: two-period relabels must be joint). **E(b) = C(b, b).** E is unbiased for |Δ_room|² to O(1/N): agent-day noise and leftover constants enter the null mean too. Relabel p for E(b) > 0.
- **O2 Onset ratio r₁ = E(1)/E_F** (HH's S(1)/S_final), with E_F computed on the agents' means over block F. **Growth:** E(d)/E_F for every day; Spearman ρ(d, E(d)); monotone = ρ ≥ 0.5 and E(n) > E(1).
- **O3 Onset direction.** **c₁ = C(1, F)/√(E(1) E_F)** (disattenuated cosine; reported only when E(1) has relabel p < 0.2; else "undefined: no day-1 split"). **π₁ = C(1, F)/E_F** (the day-1 separation along the final direction as a share of the final separation; linear in day-1 data, so stable when E(1) ≈ 0). A field step gives π₁ ≈ 1; growth or rotation gives π₁ ≪ 1.
- **O4 Half-day profile.** E(1,0)/E_F and π₁ at half-day (1, 0): the first two hours. R-fast predicts a small first half-day and a large day 1; R-field predicts both large.
- **O5 Inherited repo field u_repo** (the HH's Potts field). Repo vector v_σ = mean of the non-holdout statement vectors that name repo σ, from statements dated before P's first day only. Room field h_r = mean over room r's members of Σ_σ w_{iσ} v_σ, with w_{iσ} member i's share of its pre-period work commits (P⁻ = previous non-holdout goal period). u_repo = unit(h_best − h_rest). **f_repo(X) = (Δ_X⁽¹⁾·u)(Δ_X⁽²⁾·u)/S_X** for X = day 1 (statement-parity halves) and X = the period (alternating-day halves, H100's S), with H100's direction null (random directions from the within-room-centred between-agent covariance, 2,000 draws). Defined only where ≥ 2 members per room have pre-period work.
- **O6 Carried-content field u_prev** (secondary covariate). The members' P⁻ period means (minus the same â_i) grouped by their P rooms; f_prev(X) as in O5.
- **O7 Work persistence κ_w** (model 10 check, descriptive): share of room r's P work commits in repos its own members worked in during P⁻, minus the share in repos only the other room's members worked in; mean over the two rooms. κ_w > 0 means the inherited work field exists in the work channel.
- **Robustness:** both embedding models; style_resid vs white32; â_i removed vs not removed.

## Null / baseline
- **N1 Joint relabel** (O1–O4): 2,000 random partitions with room sizes kept, the same in every bin.
- **N2 Direction null** (O5, O6): random unit directions from the empirical within-room-centred between-agent covariance (H20: isotropic nulls are too narrow).
- **N3 Agent bootstrap** (CIs): agents resampled within rooms (500), with the relabel null recomputed per replicate (200 relabels).
- **N4 Synthetic worlds (axis F; run first):** on the real agent × bin × statement-count skeletons of G35–G44: null; hidden-field step (ρ 0.3, 1); hidden field along a planted u_repo; slow SSB (τ_g 1, 2 days; direction diffusing ∝ 1/|Δ|²); fast instability (τ_g 1 h); composition-sorted.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | no | Content directions, not timing. Bin centring removes any common shift within a bin. | n/a |
| Exogenous field (kickoff/goal/operator) | yes: it is the question | Identical kickoffs in the replication periods; bin centring removes the global goal and kickoff field. The room fields are measured: kickoffs (#38, #44), the forks (#35), and the inherited repo field u_repo as an explicit covariate (O5), plus the carried-content field u_prev (O6). Unrecorded room drives other than repos (sites, documents) stay in the residual. | partly |
| Shared model priors (family, style) | yes | DQ5 style_resid vectors; leave-period-out agent constants â_i (P and P⁻ left out); both embedding models. | removed (regime III); open in G35 |
| Contemporaneous convergence | partly | Onset shape cannot separate within-room coupling from a self-made room drive (HH337; HH339 does that). The claim here is about the field, not about coupling. | open |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-field, R-SSB, R-fast, R-comp (above).
**Locked holdout used for confirmation:** none run. `analysis/confirm.py` (frozen 2026-10-04, guarded by `--confirm`, `H107_CONFIRM=1`, a SHA-256 freeze and the holdout ledger) targets the held-out two-room periods #45–#48 (onset shape and the repo clause). Dry-run on non-holdout stand-ins only.

| Axis | Test (plan) | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | bins, rooms, constants, repo field defined from dataset fields; both models | 1 | Statement-level DQ5 vectors (style_resid, both models), H100's room-of-statement rule (null t_end fixed), agent constants with P and P⁻ left out, repo field from DQ4 commits × strict repo mentions dated before the period. Repo vectors use same-regime statements only, so #37's field rests on 4 days of #36. |
| B assumptions | within-period stationarity of the final block; regime-consistent day 1 | 1 | Day 1 must share the whitening basis with the final block (G36 excluded). The final block is assumed stationary; #38's 17 days show a stable magnitude (E(d)/E_F 0.76–1.33). No Markov audit. |
| C adequacy | relabel null for E and π₁; direction null for f_repo | 1 | Joint-relabel E_F size 0.02 (synthetic); the final split is significant in 7/8 periods in bge (not G36), 6/8 in gte. Agent-bootstrap CIs are wide at 3–4 #best agents (r₁ CI widths 1.0–1.9 in #37, #39, #42). |
| D unfitted predictions | onset shape and direction (r₁, c₁, π₁) are not fitted | 1 | The SSB onset clause holds in 2/4 identical periods, the onset kill in 0/4, the repo clause in 1/4 (#42 day 1). The half-day profile shows growth inside the week in #37 and #39 (E/E_F −0.03 → 1.01) and a full split within two hours in #41 and #42. |
| E interventional | positive controls (#38/#44 kickoffs, #35 forks); G39 reshuffle; NE42 re-split | 1 | Kickoff fields give full-size day-1 splits (r₁ 0.76–1.36) but only #44 keeps its direction (π₁ 0.73); the forks give a large split with a half-kept direction (π₁ 0.43; gte 0.62). The 04-27 reshuffle carries no #38 repo field into #39 day 1 (f 0.00, p 0.76); the carried content field splits by model. The NE42 re-split does not recall #39's direction; day 1 anti-aligns (excess z −4.5; post hoc reading). |
| F identifiability | real-skeleton synthetic: step vs slow vs fast worlds; repo-field power | 2 | Amendment 1: step worlds give the kill in 75% and π₁ ≥ 0.6 in 100% at ρ 1; slow SSB gives r₁ ≤ 0.3 in 76% and the kill in ≤ 1%; repo rule size 0.03–0.05, power 1.0. A fast (≈ 1 h) instability is not separable from a step at day resolution, and only partly at half-day. |
| G ground truth | the known fields (kickoffs, forks) must show steps | 1 | All three known-field periods split fully on day 1 (r₁ 0.76–1.39), as a field predicts; the direction is kept only in #44. |
| H comparative | R-field vs R-SSB vs R-fast | 1 | R-SSB fits #37 and #39 (slow growth from zero, no repo alignment); R-field fits #42's day 1 (repo-aligned) but not its later days; #41 is R-fast or a field present at t = 0 (full split in 2 h, no repo or memory alignment). No single rival covers the four periods. |
| I transfer | holdout (#45–#48) | 0 | not run |

## Prediction
*Written 2026-10-04 ~21:27 UTC, before the synthetic validation and before any H107 statistic on real data.*

**What I had seen when writing this (so these are not blind):** the H100 card and results (period Q, Q_spont, f_comp, remanence, movers; Gemini 3.1 Pro's day-1 φ 0.88), the H102 card (D per period), the H47 note that #41's rooms separated from day 0, H48's settling times (τ ≈ 2–4.5 h), H91's daily drift, and the per-period counts of non-holdout days, agents per room and agent work commits per goal (no repo-by-room breakdown). No H107 statistic had been computed.

- **P0, synthetic (axis F; run first).** On the real skeletons: (a) the joint-relabel test of E has size ≤ 0.07 [0.7]; (b) in hidden-field worlds at ρ = 1 the HH kill (r₁ ≥ 0.8 and c₁ ≥ 0.7) fires in ≥ 50% of period runs, and π₁ ≥ 0.6 in ≥ 70% [0.5]; (c) in slow-SSB worlds (τ_g ≥ 1 day) r₁ ≤ 0.3 in ≥ 50% of runs and the kill fires in ≤ 10% [0.5]; (d) the f_repo rule (≥ 0.15, direction-null p < 0.05) has size ≤ 0.07 and power ≥ 0.7 when the planted field lies along u_repo at ρ = 1 [0.5]. Where (b) or (c) fails at a period's counts, that period's onset verdict is "inconclusive".
- **P1, onset in identical-kickoff periods (replication; G37, G39, G41, G42).** I expect the split to be mostly present on day 1 (H48's hours-scale settling; H47's #41 day 0). Credences: the HH's SSB clause (r₁ ≤ 0.3 and growth) holds in ≥ 3/4 [0.2]; the HH kill's onset clause (r₁ ≥ 0.8 and c₁ ≥ 0.7) holds in ≥ 2/4 [0.35]; median π₁ over the four ≥ 0.5 [0.6].
- **P2, half-day timing.** In the first two hours, E(1,0)/E_F ≤ 0.3 in ≥ 3/4 identical periods (growth inside day 1: R-fast) [0.35].
- **P3, inherited repos.** f_repo (period level) ≥ 0.15 with direction-null p < 0.05 in ≥ 2/4 identical periods with a defined field [0.2]; the same at day 1 [0.2]. κ_w > 0 in ≥ 3/4 (the work field exists in work) [0.6].
- **P4, positive control (G38, G44).** π₁ ≥ 0.6 in both [0.6]; r₁ ≥ 0.8 and c₁ ≥ 0.7 in both [0.4].
- **P5, G35 forks.** π₁ ≥ 0.6 (no constants removed) [0.5].
- **P6, G39 reshuffle.** f_repo(day 1) along the #38-repo field ≥ 0.15 with p < 0.05 [0.3]; f_prev(day 1) ≥ 0.15 with p < 0.05 [0.3].
- **P7, G41 re-split.** C(day 1 of #41, #39 period) within the joint relabel null (|z| < 2) [0.65]; f_repo along the #40-repo field n.s. [0.7].

**Verdict rules.**
- *Identical period (G37, G39, G41, G42):* **supported** (SSB) if E_F has relabel p < 0.05, r₁ ≤ 0.3 (point estimate), and the repo clause is not met; **failed** (hidden field) if r₁ ≥ 0.8 and c₁ ≥ 0.7, or f_repo ≥ 0.15 with p < 0.05 (period or day 1); **mixed** otherwise; **descriptive** if E_F has p ≥ 0.05 (no final split to grow toward). "Inconclusive" (P0) is written as mixed with the reason.
- *Natives:* G38/G44 supported if π₁ ≥ 0.6 (the known field shows a step); G35 likewise; G39 supported (no inherited field) if neither f_repo nor f_prev at day 1 reaches p < 0.05 with ≥ 0.15, failed if either does; G41 supported if P7 holds.
- *Hypothesis level (HH337):* **supported (SSB)** if ≥ 3/4 identical periods are supported and P4 passes; **failed (hidden field)** if ≥ 2/4 identical periods fail by the HH kill (onset clause or repo clause); **mixed** otherwise. If P4 fails (the known fields show no step), the onset clauses are inconclusive and only the repo clause is scored.
- *Two models:* the verdict uses bge; a period verdict that gte reverses (supported ↔ failed) is downgraded to mixed.
- *Multiplicity:* about 8 periods × 2 models × 3 variants; only these rules count.

### Amendment 1 (after the synthetic validation, before any H107 statistic on real data)
*2026-10-04 21:37 UTC.* `analysis/synthetic.py`, 40 worlds per setting, 300 joint relabels, on the real statement skeletons of G35, G37–G39, G41, G42, G44 (280 period runs per world). Calibration (instrument, not an outcome): statement noise s_ε² = 0.0195 and agent-day deviation s_η² = 0.0026 per coordinate (regime III, #36–#44); leftover agent constants at the full H100 variance τ² = 0.0014 (no constants removed in the synthetic, so it is conservative). Room-effect size ρ as in H100.

| World | E_F rejects | kill (r₁ ≥ 0.8, c₁ ≥ 0.7) | SSB (r₁ ≤ 0.3) | π₁ ≥ 0.6 | median r₁ / π₁ | first half-day E/E_F ≤ 0.3 | repo rule (planted / random u) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| null | 0.02 | 0.00 | 0.01 | (0.20; E_F n.s.) | – | – | 0.05 / 0.05 |
| step ρ 0.3 | 0.75 | 0.38 | 0.11 | 0.86 | 1.00 / 1.01 | 0.18 | 1.00 / 0.05 |
| step ρ 1 | 0.99 | 0.75 | 0.00 | 1.00 | 1.04 / 1.03 | 0.01 | 1.00 / 0.03 |
| slow SSB τ_g 1 d | 0.99 | 0.01 | 0.76 | 0.07 | 0.17 / 0.33 | 0.84 | – |
| slow SSB τ_g 2 d | 0.95 | 0.00 | 0.76 | 0.05 | 0.09 / 0.20 | 0.79 | – |
| fast instability τ_g ≈ 1 h | 1.00 | 0.20 | 0.19 | 0.68 | 0.52 / 0.68 | 0.50 | – |

- **P0(a)** passes: E_F size 0.02. **P0(b)** passes: kill 0.75 and π₁ ≥ 0.6 in 100% of step worlds at ρ = 1 (per period 0.57–0.90; #37, with 3 days and 3 #best agents, is weakest). **P0(c)** passes: SSB clause 0.76 (per period 0.65–0.88), kill ≤ 0.01. **P0(d)** passes: repo rule size 0.03–0.05, power 1.00 (day 1: 0.95–1.00).
- **What the design cannot do.** A fast instability (growth time ≈ 1 active hour) looks like a step at day resolution (π₁ ≥ 0.6 in 68%). The first half-day separates them only partly: E(1,0)/E_F ≤ 0.3 in 50% of fast-instability runs vs 1% of step runs. So a step at day resolution with a small first half-day reads as R-fast; a step with a full first half-day and no repo alignment cannot separate a field present at t = 0 from growth faster than two hours.
- **Clarification (not a rule change):** the onset kill counts only where the final split is significant (E_F relabel p < 0.05), as the card's "descriptive" rule already implies; in null worlds r₁ and c₁ are otherwise meaningless (kill 0.14 without this condition in the smoke test).
- **Fix before the 40-world run (instrument, labelled):** the first smoke test set the SSB direction diffusion per coordinate, which in 32 dimensions rotated the direction fully every half-day (a regenerating world, not coarsening). D0 was rescaled to a total angular variance of 0.02 rad² per half-day at saturation (0.4 early).
- No prediction or verdict rule changes.

## Results by goal period
Primary: bge style_resid, bin-centred, a_i removed (P and P⁻ left out); gte in brackets. r₁ = E(1)/E_F; π₁ = day-1 separation along the final direction as a share of the final separation; c₁ = disattenuated onset cosine.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G35](goalperiod-subhypotheses/G35/README.md) | native (forks) | mixed | r₁ 1.39 [0.88, 1.89] (1.95); π₁ 0.43 [0.31, 0.69] (0.62); no constants (regime II) |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication (descriptive) | descriptive | day 1 in regime II; regime-III days: no final split (E_F p 0.40; gte 0.12) |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | supported | E_F p 0.018; r₁ 0.09 [0.06, 1.08] (0.15); growth 0.09 → 0.66 → 1.00; f_repo 0.00 (p 0.93) |
| [G38](goalperiod-subhypotheses/G38/README.md) | native (kickoff field) | mixed | r₁ 1.11 [0.81, 1.60] (1.36); π₁ 0.53 [0.34, 0.80] (0.44); c₁ 0.51 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication + native (reshuffle) | mixed | replication supported: r₁ −0.09 (E_F p 0.023; gte p 0.11); native: #38 repo field at day 1 0.00 (p 0.76); carried content 0.01 (gte 0.22, p < 0.001) |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication + native (NE42 re-split) | mixed | r₁ 0.71 [0.53, 0.98] (0.71); c₁ 0.59 (0.52); first two hours 0.82; #39 memory z −4.5 (anti-aligned); #40 repo field n.s. |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | r₁ 0.89 (0.48); c₁ 0.50; **f_repo(day 1) 0.34, p 0.002 (0.39, p 0.005)**; period-level f_repo 0.05 (p 0.34) |
| [G44](goalperiod-subhypotheses/G44/README.md) | native (kickoff field) | supported | r₁ 0.76 [0.58, 1.11] (0.69); π₁ 0.73 [0.57, 0.87] (0.78); c₁ 0.84 (0.94) |

## Results
### Exploratory round 1 (2026-10-04; non-holdout only, asserted in the scheme)
- **Scheme:** 99,272 non-holdout statements (#33–#51), 15,721 strict repo mentions mapped to statements, 973 agent × repo × goal work rows; 0.9 MB in `data/processed/H107-room-split-onset/`.
- **Code:** `scheme/build.py`; `analysis/{rslib,h107lib,synthetic,run,summarize,figures,posthoc_g38,confirm}.py`.
- **Numbers:** `results/raw_all.json` (5 instrument variants), `results/results.json` (verdicts), `results/posthoc_g38.json`, `synthetic/synthetic_summary.json`. Estimates: 91 rows in `per_period_estimates` (hypothesis H107).
- **Figures:** `figures/onset_by_period.pdf`, `figures/synthetic_rules.pdf`.

**Headline.**
1. **Two onset shapes.** In #37 and #39 the split is absent on day 1 (r₁ 0.09 and −0.09; day-1 E not significant) and grows over the week (Spearman 1.0 and 0.9; half-day profile in #37: −0.03, 0.24, 0.66, 0.87, 1.01). That is the SSB signature. In #41 and #42 it is at 70–90% of final size on day 1 (r₁ 0.71, 0.89) and already full within the first two hours in #41 (0.82).
2. **The day-1 direction is half kept everywhere a day-1 split exists.** c₁ 0.50–0.59 in #38, #41 and #42 (gte 0.37–0.52); only #44 keeps it (0.84; gte 0.94). Neither the HH's SSB clause (|c₁| < 0.5 with growth) nor its kill (r₁ ≥ 0.8 with c₁ ≥ 0.7) describes these periods.
3. **Inherited repos set the day-1 direction only in #42.** f_repo(day 1) 0.34 (direction-null p 0.002; gte 0.39, p 0.005), and the carried-content field agrees (0.40). By the period-level split the inherited direction is gone (f_repo 0.05, p 0.34): the inherited work sets the first day, and the week overwrites it. In #37, #39 and #41 the repo field carries chance shares (0.00–0.08), including #39, where three agents carried 17 days of room-specific #38 work.
4. **Known fields give full-size day-1 splits** (r₁ 0.76–1.39 in #35, #38, #44), but only #44 keeps the direction (π₁ 0.73). #38's day-1 direction is half kept even at the horizon of days 4–5 (π₁ 0.56, post hoc), while its later days are mutually persistent (H108: P(ℓ) ≈ 0.85 out to six days). The kickoff day is a transient even under a field.
5. **No room memory through the NE42 merge.** #41's day 1 does not recall #39's direction; it anti-aligns (excess z −4.5, cos −0.69 in bge; #39's own split is weak, gte E ≈ 0). P7 fails by its |z| < 2 wording, in the direction opposite to the memory rival. The anti-alignment is not interpreted (post hoc).
6. **The work field exists in the work channel but is weak.** κ_w > 0 in 4/4 identical periods (0.31, 0.001, 0.31, 0.06): rooms commit more to repos their own members used before, but in #39 almost nothing (0.001).

**Synthetic validation (axis F):** Amendment 1 (E_F size 0.02; step vs slow-SSB separated; repo rule size 0.03–0.05, power 1.0; fast instability not separable from a step at day resolution).

**Outcome vs prediction**

| | Prediction (locked) | Outcome | Verdict |
| --- | --- | --- | --- |
| P0 | (a) E size ≤ 0.07; (b) step: kill ≥ 50%, π₁ ≥ 0.6 ≥ 70%; (c) slow SSB: r₁ ≤ 0.3 ≥ 50%, kill ≤ 10%; (d) repo rule size ≤ 0.07, power ≥ 0.7 | 0.02; 75%, 100%; 76%, ≤ 1%; 0.03–0.05, 1.00 | passed |
| P1 | SSB clause in ≥ 3/4 [0.2]; kill onset in ≥ 2/4 [0.35]; median π₁ ≥ 0.5 [0.6] | 2/4 (#37, #39); 0/4; 0.33 (gte 0.32) | not met; not met; failed |
| P2 | first half-day ≤ 0.3 in ≥ 3/4 [0.35] | 2/4 (#37 −0.03, #39 −0.11; #41 0.82, #42 2.38) | not met |
| P3 | f_repo period clause in ≥ 2/4 [0.2]; day 1 in ≥ 2/4 [0.2]; κ_w > 0 in ≥ 3/4 [0.6] | 0/4; 1/4 (#42, both models); 4/4 (one ≈ 0) | not met; not met; met |
| P4 | π₁ ≥ 0.6 in #38 and #44 [0.6]; r₁ ≥ 0.8 and c₁ ≥ 0.7 in both [0.4] | #44 0.73, #38 0.53; #38 c₁ 0.51, #44 r₁ 0.76 | **failed** (half) |
| P5 | G35 π₁ ≥ 0.6 [0.5] | 0.43 (gte 0.62) | failed (bge) |
| P6 | G39 repo field or carried content at day 1 ≥ 0.15, p < 0.05 [0.3 each] | repo 0.00 (both models); carried 0.01 (gte 0.22, p < 0.001) | mixed (models split) |
| P7 | G41 day 1 × #39 within the null [0.65]; #40 repos n.s. [0.7] | z −4.5 (anti-aligned); #40 repo n.s. | first clause failed (reversed); second met |
| HH337 | SSB (≥ 3/4 supported and P4) / hidden field (≥ 2/4 fail) | 2 supported, 1 failed, 1 mixed; P4 failed | **mixed** |

**What this means.**
1. In vector-spin terms, a goal kickoff is a quench, and the room order parameter appears in two ways. In #37 (three #best agents, 3 days) and #39 (just reshuffled) it nucleates from zero and grows over days. In #41 and #42 it is ordered within hours, too fast for a day-resolution test to tell a field from a fast instability. What sets the shape is not identified: #37's rooms had existed since #35, so partition age alone does not explain it.
2. The direction set on day 1 is not the final direction, except where the room instructions differ (#44). Day 1 is a transient that partly re-orients. That favours an order parameter whose direction is soft (H108), not one pinned from t = 0.
3. The hidden-field reading of H100's residual is supported only weakly: inherited repos explain the first day of one week out of four, and never the week as a whole.

**Operator-facing conclusion.**
- With identical instructions, expect the room content split to appear within the first day in some weeks and to build over several days in others (#39, right after a reshuffle, started from zero).
- Do not read the first day's room difference as the week's: its direction is only about half kept (c₁ ≈ 0.5), unless the rooms got different instructions.

**Caveats.**
- **Few periods and small rooms.** Four identical periods with 3–5 #best agents; r₁ CIs span 1.0–1.9 in #37, #39 and #42.
- **Day resolution.** A growth time below about two active hours cannot be separated from a field present at t = 0 (Amendment 1).
- **Positive control half met.** #38's direction shortfall is a day-1 transient, not a missing step; still, by the pre-registered rule the card-level onset clauses are inconclusive.
- **Repo field coverage.** Repo vectors need same-regime statements naming the repo before the period; #37's field rests on four days of #36. Repos never named in chat or intentions do not enter.
- **Post hoc items:** the G38 horizon check (`posthoc_g38.py`), the "transient day 1" reading, the G41 anti-alignment, and the reshuffle reading of #39 (C4 tests it).

**Claim that stands:** In the four identical-kickoff #best/#rest periods, the room content split does not have one onset shape: it starts near zero and grows over days in #37 and #39 (r₁ 0.09 and −0.09 in bge; gte 0.15 and 0.43, #39's final split n.s. in gte), and is at 70–90% of its final size on day 1 in #41 and #42 with a day-1 direction only half aligned with the final one (c₁ 0.50–0.59); members' pre-period repos set the day-1 direction only in #42 (f_repo 0.34, p 0.002; gte 0.39). Excluded: the card-level SSB or hidden-field verdict (positive control #38 failed π₁ ≥ 0.6), the G41 anti-alignment (sign post hoc), the G38 horizon check (post hoc), and the half-day timing (underpowered for growth below two hours).

### Confirmatory design (written 2026-10-04 after exploration; not run)
`analysis/confirm.py`, frozen predictions in the script header (SHA-256 recorded in `analysis/confirm.sha256`):
- **C1 (no hidden-field step):** among scorable identical-kickoff held-out periods among #45–#48 (E_F relabel p < 0.05; whitened kickoff cos ≥ 0.95), the HH337 onset kill (r₁ ≥ 0.8 and c₁ ≥ 0.7) fires in ≤ 1/3 [0.7]. Round 1: 0/4.
- **C2 (day 1 is a transient):** in those periods with day-1 E relabel p < 0.2, c₁ < 0.7 in ≥ 2/3 [0.6].
- **C3 (repos rarely set the week):** period-level f_repo ≥ 0.15 with direction-null p < 0.05 in ≤ 1/3 of held-out periods with a defined field [0.7].
- **C4 (reshuffle onset, the #39 analog):** in scorable identical-kickoff periods that open with an operator move (NE19 opens #45), r₁ ≤ 0.3 [0.4]. One exploratory instance.
- *Design note (2026-10-04, before freezing):* a first draft tested "onset shape by partition age". The dry run showed that #37's rooms were not new, so the rule rested on a wrong reading; it was replaced by C1 and C4 before the freeze.
- **Safeguards:** `--confirm` plus `H107_CONFIRM=1`; refuses unless the SHA-256 of the script and of `rslib.py`, `h107lib.py` and `scheme/build.py` match the frozen values and the files are committed; calls `holdout_ledger.check("H107", target, "content", ["content_alignment"])` per target. `--dry-run` runs on non-holdout stand-ins (#39, #41, #42, #44) and asserts that no held-out row is loaded.
- **Reuse disclosure:** #45–#48 content is planned by H23, H26, H47, H81–H83, H100 and H102; NE19 (#45) is H23's, H65's and H100's target. H100's C2/C4 and H102's C1 use the same #best/#rest separation family. Whoever runs second discloses.

## Round 2 redirects
**What the direction is really after:** whether a room's content order is born from a field the room inherits or from an instability, and how fast it orients.
- **H107-R1. Hour resolution on day 1.** Per-30-min excess separation over the first active day (statement level, both models), pooled across periods by hierarchical shrinkage: is there a growth time τ_g of 0.5–2 h (R-fast) or a jump at t = 0 (R-field)?
- **H107-R2. What sets the onset shape.** #37 and #39 (growth) vs #41 and #42 (immediate): candidates are a reshuffle at the kickoff (#39; C4 on #45), room size and period length. Needs more periods (holdout, #51 side rooms).
- **H107-R3. Contemporaneous work field** (H100-R3): the room's period-P repo shares as a Potts field; does the final split lie along what each room builds?
- **H107-R4. Day-1 transient mechanism.** Does the day-1 direction follow the kickoff-day operator messages or the first repos each room touches (read vs posted-unread at matched age, HH339)?

## Notes
- 2026-10-04 21:24–21:28 UTC: card, observables, nulls and predictions written by the H107 round-1 agent, before any H107 statistic on real data.
- 21:29 UTC: period folders with dated predictions; scheme built (0.9 MB). 21:31–21:37 UTC: synthetic validation, Amendment 1. H108's synthetic and Amendment 1 (21:44 UTC) were finished before H107's real-data run, because H107's daily E(d) overlaps H108's inputs.
- 21:45 UTC: real-data run (`run.py`), then `summarize.py`. One labelled post hoc check (`posthoc_g38.py`), after seeing G38's π₁ shortfall.
- Suggested shared changes (not made; outside edit scope): DEFINITIONS entries for the named variants above; move the room-of-statement helper and `rslib.py` to `infra/shared/` (now four users: H100, H102, H107, H108); a model-11 pitfall ("day 1 is a transient: its room direction is only half kept, even under a field").
